import json
from typing import Any

import requests

from task.models.message import Message
from task.models.role import Role
from task.tools.base import BaseTool


class DialClient:

    def __init__(
            self,
            endpoint: str,
            deployment_name: str,
            api_key: str,
            tools: list[BaseTool] | None = None
    ):
        #TODO:
        if not api_key or api_key.strip() == "":
            raise ValueError("API key cannot be null or empty")
        # 1. If not api_key then raise error
        # 2. Add `self.__endpoint` with formatted `endpoint` with model (model=deployment_name):
        #   - f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        self.__endpoint = f"{endpoint}/openai/deployments/{deployment_name}/chat/completions"
        # 3. Add `self.__api_key`
        self._api_key = api_key
        # 4. Prepare tools dict where key will be tool name and value will

        self.__tools_dict: dict[str, BaseTool] = {tool.name: tool for tool in tools} or {}

        # 5. Prepare tools list with tool schemas
        self.__tools_schemas: list[str]= [tool.schema for tool in tools] or []
        # 6. Optional: print endpoint and tools schemas
        print(self.__endpoint)
        print(json.dumps(self.__tools_schemas, indent=4))


    def get_completion(self, messages: list[Message], print_request: bool = True) -> Message:
        #TODO:
        # 1. create `headers` dict with:
        #   - "api-key": self._api_key
        #   - "Content-Type": "application/json"
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        # 2. create `request_data` dict with:
        #   - "messages": [msg.to_dict() for msg in messages]
        #   - "tools": self._tools
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "tools": self.__tools_schemas
        }
        # 3. Optional: print request (message history)
        if print_request:
            print("Request:", json.dumps({"message_history": [msg.to_dict() for msg in messages]}, indent=2))
        # 4. Make POST request (requests) with:
        #   - url=self._endpoint
        #   - headers=headers
        #   - json=request_data
        response = requests.post(self.__endpoint, json=request_data, headers=headers)

        # 5. If response status code is 200:
        if response.status_code == 200:
        #   - get response as json
            data = response.json()
        #   - get "choices" from response json
        #   - get first choice
            choice = data["choices"][0]
            if choice:
        #   - Optional: print choice
                print(f"Result: {json.dumps(choice, indent=2)}")
        #   - Get `message` from `choice` and assign to `message_data` variable
                message_data = choice.get("message", {})
        #   - Get `content` from `message` and assign to `content` variable
                content = message_data.get("content", "")
        #   - Get `tool_calls` from `message` and assign to `tool_calls` variable
                tool_calls = message_data.get("tool_calls")
        #   - Create `ai_response` Message (with AI role, `content` and `tool_calls`)
                ai_response = Message(role=Role.AI, content=content,tool_calls=tool_calls)
        #   - If `choice` `finish_reason` is `tool_calls`:
        #       Yes:
        #           - append `ai_response` to `messages`
        #           - call `_process_tool_calls` with `tool_calls` and assign result to `tool_messages` variable
        #           - add `tool_messages` to `messages` (use `extend` method)
        #           - make recursive call (return `get_completion` with `messages` and `print_request`)
                if choice["finish_reason"] == "tool_calls" and tool_calls:
                    messages.append(ai_response)
                    tool_messages = self._process_tool_calls(tool_calls=tool_calls)
                    messages.extend(tool_messages)

                    return self.get_completion(messages=messages, print_request=True)
        #       No: return `ai_response` (final assistant response)
                else:
                    return ai_response

            raise ValueError("No Choice has been present in the response")
        # Otherwise raise exception
        raise Exception(f"HTTP {response.status_code}: {response.text}")



    def _process_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[Message]:
        """Process tool calls and add results to messages."""
        print("tool_calls", tool_calls)
        tool_messages = []
        for tool_call in tool_calls:
            #TODO:
            # 1. Get `id` from `tool_call` and assign to `tool_call_id` variable
            tool_call_id = tool_call["id"]
            # 2. Get `function` from `tool_call` and assign to `function` variable
            function = tool_call.get("function", {})
            # 3. Get `name` from `function` and assign to `function_name` variable
            function_name=function["name"]
            # 4. Get `arguments` from `function` as json (json.loads) and assign to `arguments` variable
            arguments = json.loads(function.get("arguments"))
            # 5. Call `_call_tool` with `function_name` and `arguments`, and assign to `tool_execution_result` variable
            tool_execution_result = self._call_tool(function_name=function_name, arguments=arguments)
            # 6. Append to `tool_messages` Message with:
            #       - role=Role.TOOL
            #       - name=function_name
            #       - tool_call_id=tool_call_id
            #       - content=tool_execution_result
            tool_messages.append(Message(
                role=Role.TOOL,
                name=function_name,
                tool_call_id=tool_call_id,
                content=tool_execution_result
            ))
            # 7. print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")
            print(f"FUNCTION '{function_name}'\n{tool_execution_result}\n{'-'*50}")
            # 8. Return `tool_messages`
            # -----
            # FYI: It is important to provide `tool_call_id` in TOOL Message. By `tool_call_id` LLM make a  relation
            #      between Assistant message `tool_calls[i][id]` and message in history.
            #      In case if no Tool message presented in history (no message at all or with different tool_call_id),
            #      then LLM with answer with Error (that not find tool message with specified id).

        return tool_messages

    def _call_tool(self, function_name: str, arguments: dict[str, Any]) -> str:
        #TODO:
        # Get tool from `__tools_dict`, id present then return executed result, otherwise return `f"Unknown function: {function_name}"`
        tool = self.__tools_dict.get(function_name)

        if not tool:
            return f"Unknown function: {function_name}"

        return tool.execute(arguments)
