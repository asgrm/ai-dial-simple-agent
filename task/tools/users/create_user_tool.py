from typing import Any

from task.tools.users.base import BaseUserServiceTool
from task.tools.users.models.user_info import UserCreate


class CreateUserTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        #TODO: Provide tool name as `add_user`
        return 'add_user'

    @property
    def description(self) -> str:
        #TODO: Provide description of this tool
        return 'Creates user'


    @property
    def input_schema(self) -> dict[str, Any]:
        #TODO: Provide tool params Schema. To do that you can create json schema from UserCreate pydentic model ` UserCreate.model_json_schema()`
        return UserCreate.model_json_schema()

    def execute(self, arguments: dict[str, Any]) -> str:
        #TODO:
        # 1. Validate arguments with `UserCreate.model_validate`
        try:
            user_model = UserCreate.model_validate(arguments)
        # 2. Call user_client add user and return its results
            self._user_client.add_user(user_model)
        except Exception as e:
        # 3. Optional: You can wrap it with `try-except` and return error as string `f"Error while creating a new user: {str(e)}"`
            print(e)
            return f"Error while creating a new user: {str(e)}"