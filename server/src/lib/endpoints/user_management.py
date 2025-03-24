"""
The file that contains the class that handle user management
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Union
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI
from ..password_handling import PasswordHandling
from ..image_handler import ImageHandler

class UserManagement:
    """
    The class that handle user management
    """
    def __init__(self, runtime_data: RuntimeData, error: int = 84, success: int = 0, debug: bool = False) -> None:
        """
        Constructor
        """
        # -------------------------- Inherited values --------------------------
        self.runtime_data_initialised: RuntimeData = runtime_data
        self.error: int = error
        self.success: int = success
        self.debug: bool = debug
        # ------------------------ The logging function ------------------------
        self.disp: Disp = Disp(
            TOML_CONF,
            FILE_DESCRIPTOR,
            SAVE_TO_FILE,
            FILE_NAME,
            debug=self.debug,
            logger=self.__class__.__name__
        )
        # ------------------------ The password checker ------------------------
        self.password_handling_initialised: PasswordHandling = PasswordHandling(
            self.error,
            self.success,
            self.debug
        )
        # ------------------------- The Image handler --------------------------
        self.image_handler_initialised: ImageHandler = ImageHandler(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )

    async def get_user(self, request: Request) -> Response:
        """
            Endpoint allowing the user to get it's account data.
        """
        title = "Get user"
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title
            )
        usr_id = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response) is True:
            return usr_id
        user_profile = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(
                title=title
            )
        new_profile = user_profile[0]
        for i in CONST.USER_INFO_BANNED:
            if i in new_profile:
                new_profile.pop(i)
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=new_profile,
            resp="success",
            error=False
        )
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_user_by_id(self, request: Request, user_id: str) -> Response:
        """
            Endpoint allowing the user to get another account data.
        """
        title = "Get user by id"
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title
            )
        user_profile = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{user_id}'",
        )
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(
                title=title
            )
        new_profile = user_profile[0]
        for i in CONST.USER_INFO_BANNED:
            if i in new_profile:
                new_profile.pop(i)
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=new_profile,
            resp="success",
            error=False
        )
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def put_user(self, request: Request) -> Response:
        """
        The function to update every data of a user
        """
        title: str = "Put user"
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title
            )
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(
            request
        )
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("username", "email", "bio")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        body_username: str = request_body["username"]
        body_email: str = request_body["email"]
        body_bio: str = request_body["bio"]
        if body_username == "" or body_email == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id
        user_profile: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(
                title=title
            )
        data: List[str] = [
            body_username,
            body_email,
            user_profile[0]["password"],
            user_profile[0]["favicon"],
            body_bio
        ]
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_ACCOUNTS
        )
        if isinstance(columns, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title,
            )
        columns.pop(0)
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_ACCOUNTS,
            data=data,
            columns=columns,
            where=f"id='{usr_id}'",
            title=title,
            message="The account information has been updated."
        )

    async def patch_user(self, request: Request) -> Response:
        """
        The function to update some data of a user
        """
        title: str = "Patch user"
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title,
            )
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(
            request
        )
        self.disp.log_debug(f"Request body: {request_body}", title)
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id
        user_profile = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'",
        )
        self.disp.log_debug(f"User profile = {user_profile}", title)
        if user_profile == self.error or len(user_profile) == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(
                title=title,
            )
        if "username" in request_body:
            if request_body["username"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_ACCOUNTS,
                "id",
                "username",
                usr_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )
        if "email" in request_body:
            if request_body["email"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_ACCOUNTS,
                "id",
                "email",
                usr_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )
        if "password" in request_body:
            if request_body["password"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            data: Dict[str, Any] = [
                self.password_handling_initialised.hash_password(request_body["password"])
            ]
            status = self.runtime_data_initialised.database_link.update_data_in_table(
                CONST.TAB_ACCOUNTS,
                data,
                ["password"],
                f"id='{usr_id}'"
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title,
                )
        if "bio" in request_body:
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_ACCOUNTS,
                "id",
                "bio",
                usr_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The account information has been updated.",
            resp="success",
            error=False
        )
        return HCI.success(content=data, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    async def upload_profile_image_file(self, request: Request) -> Response:
        """
        The function to upload an image file
        """
        title: str = "Upload image file"

        # Check The token sended in the request
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title
            )

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Check if every required information is in the request body
        if not request_body or "file" not in request_body:
            self.disp.log_error("File not found", title)
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the user information
        user: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'"
        )
        if user == self.error or not user:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(
                title=title
            )

        # Upload the image
        file_url: Union[str, Response] = await self.image_handler_initialised.upload_image(
            bucket_name=CONST.USER_PROFILE_PHOTO_BUCKET,
            title=title,
            file=request_body["file"],
            key_name=user[0]["username"]
        )
        if isinstance(file_url, Response):
            return file_url
        self.disp.log_debug(f"User={user}", title)

        # Delete old photo from MinIO
        if user[0]["favicon"] is not None or user[0]["favicon"] != "NULL":
            link: str = user[0]["favicon"]
            counter: int = 0
            key_name: str = ""
            for idx, char in enumerate(link):
                if char == "/":
                    counter += 1
                if counter == 4:
                    key_name = link[idx + 1:]
                    break
            self.runtime_data_initialised.bucket_link.delete_file(
                bucket_name=CONST.USER_PROFILE_PHOTO_BUCKET,
                key_name=key_name
            )

        # Update the profile photo of the user
        status: int = self.runtime_data_initialised.database_link.update_data_in_table(
            table=CONST.TAB_ACCOUNTS,
            data=[file_url],
            column=["favicon"],
            where=f"id='{usr_id}'"
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The image has been uploaded successfully.",
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_user(self, request: Request) -> Response:
        """
        The function to delete a user
        """
        title: str = "Delete user"

        # Check The token sended in the request
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title,
            )

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the workspaces id created by the user
        workspaces_id: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES,
            column="id",
            where=f"creator_id='{usr_id}'",
        )

        # Delete every workspaces in the list
        if isinstance(workspaces_id, int) is False:
            for _, workspace in enumerate(workspaces_id):
                self.runtime_data_initialised.boilerplate_non_http_initialised.delete_workspace(
                    workspace_id=int(workspace["id"])
                )

        # Delete the user in the cards assignees
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_CARDS_ASSIGNEES,
            where=f"user_id='{usr_id}'"
        )

        # Delete the user in the workspaces members
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            where=f"user_id='{usr_id}'"
        )

        # Delete the user notifications
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            where=f"user_id='{usr_id}'"
        )

        # Delete the user in the connected users table
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            where=f"user_id='{usr_id}'"
        )

        # Delete the favicon
        user: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{usr_id}'"
        )
        if user == self.error or not user:
            if user[0]["favicon"] != "NULL" and user[0]["favicon"] != None:
                status: int = self.runtime_data_initialised.bucket_link.delete_file(
                    bucket_name=CONST.USER_PROFILE_PHOTO_BUCKET,
                    key_name=user[0]["favicon"]
                )
                if status == self.error:
                    return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                        title=title
                    )

        # Delete the user
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            where=f"id='{usr_id}'"
        )

        # Set the response body
        response_body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The user was deleted successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def logout_user(self, request: Request) -> Response:
        """
        The function to log a user out
        """
        title: str = "Logout"
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title,
            )
        status: int = self.runtime_data_initialised.database_link.remove_data_from_table(
            CONST.TAB_CONNECTIONS,
            f"token='{token}'"
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title
            )
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="You have successfully logged out.",
            resp="success",
            error=False
        )
        cookie_value = "token=; HttpOnly; Secure; SameSite=None; Partitioned; Path=/; Expires=" + (datetime.now(timezone.utc) - timedelta(days=1)).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
        headers = self.runtime_data_initialised.json_header
        headers["Set-Cookie"] = cookie_value
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=headers
        )
