from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserUpdate


class UpdateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        #TODO: Provide tool name as `update_user`
        return "update_user"

    @property
    def description(self) -> str:
        #TODO: Provide description of this tool
        return "Updates user"

    @property
    def input_schema(self) -> dict[str, Any]:
        #TODO:
        # Provide tool params Schema:
        # - id: number, required, User ID that should be updated.
        # - new_info: UserUpdate.model_json_schema()
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "number",
                    "description": " User id that should be updated"
                },
                "new_info": UserUpdate.model_json_schema()
            },
            "required": ["id"]
        }

    def execute(self, arguments: dict[str, Any]) -> str:
        #TODO:
        try:
        # 1. Get user `id` from `arguments`
            user_id = int(arguments.get('id'))
        # 2. Get `new_info` from `arguments` and create `UserUpdate` via pydentic `UserUpdate.model_validate`
            user_update_model = UserUpdate.model_validate(arguments)
        # 3. Call user_client update_user and return its results
            self._user_client.update_user(user_id, user_update_model)
        # 4. Optional: You can wrap it with `try-except` and return error as string `f"Error while creating a new user: {str(e)}"`
        except Exception as e:
            return f"Error while updating a user: {str(e)}"

