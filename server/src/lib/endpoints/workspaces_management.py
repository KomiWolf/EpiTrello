"""
The file that contains the class that handle workspaces management
"""

from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI
from ..image_handler import ImageHandler

class WorkspacesManagement:
    """
    The class that handle workspaces management
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
        # ------------------------- The Image handler --------------------------
        self.image_handler_initialised: ImageHandler = ImageHandler(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )

    async def get_workspace_by_id(self, request: Request, workspace_id: str) -> Response:
        """
        Get a workspace by his id
        """
        title: str = "Get workspace by id"

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

        # Get the workspace data
        workspace: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES,
            column="*",
            where=f"id='{workspace_id}'",
        )
        if workspace == self.error or not workspace:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=workspace,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_user_workspaces(self, request: Request) -> Response:
        """
        Get the connected user workspaces
        """
        title: str = "Get user workspaces"

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

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get every workspaces id where the user is
        workspaces_id: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            column="*",
            where=f"user_id='{usr_id}'",
        )

        # Check if the workspaces was found
        if workspaces_id == self.error or not workspaces_id:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Get every workspaces where the user is
        workspace_id_str = "workspace_id"
        workspaces: List[Dict[str, Any]] = []
        for _, item in enumerate(workspaces_id):
            workspace: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
                table=CONST.TAB_WORKSPACES,
                column="*",
                where=f"id='{item[workspace_id_str]}'",
            )
            if isinstance(workspace, int) is False:
                workspaces.append(workspace[0])

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=workspaces,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def create_workspace(self, request: Request) -> Response:
        """
        Create a new workspace
        """
        title = "Create Workspace"

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
                title
            )

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Check if every required information is in the request body
        if not request_body or not all(key in request_body for key in ("name", "description", "favicon")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        if request_body["name"] == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)

        # Get the user id by the token
        usr_id = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Upload the image
        file_url: Union[str, Response] = await self.image_handler_initialised.upload_image(
            bucket_name=CONST.WORKSPACES_PHOTO_BUCKET,
            title=title,
            file=request_body["favicon"],
            key_name=request_body["name"]
        )
        if isinstance(file_url, Response):
            return file_url

        # Get columns names of the workspace table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_WORKSPACES
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        # Insert the data to the workspace table
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_WORKSPACES,
            data=[request_body["name"], usr_id, request_body["description"], file_url],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Get columns names of the workspace members table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_WORKSPACES_MEMBERS
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        # Get the workspace_id
        workspace_id: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES,
            column="id",
            where=f"name='{request_body['name']}'",
        )

        # Check if the workspace was found
        if workspace_id == self.error or not workspace_id:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Insert the data to the workspace members table
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            data=[usr_id, str(workspace_id[-1]["id"]), "1", "1", "1", "1"],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title,
            )

        # Set the response body
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The workspace has been created successfully.",
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def put_workspace(self, request: Request, workspace_id: str) -> Response:
        """
        Update every data of a workspace
        """
        title = "Put Workspace"

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
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(
            request
        )
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Check if every required information is in the request body
        if not request_body or not all(key in request_body for key in ("name", "description")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                title
            )

        # Get the user id by the token
        usr_id: Union[str, Any] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the workspace data
        workspace: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES,
            column="*",
            where=f"id='{workspace_id}'",
        )

        # Check if the workspace was found
        if workspace == self.error or not workspace:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Check if the user have the right to update the workspace
        if workspace[0]["creator_id"] != int(usr_id):
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Update the workspace data
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_WORKSPACES,
            data=[request_body["name"], request_body["description"]],
            columns=["name", "description"],
            where=f"id='{workspace_id}'",
            title=title,
            message="The workspace information has been updated."
        )

    async def patch_workspace(self, request: Request, workspace_id: str) -> Response:
        """
        Update some data of a workspace
        """
        title: str = "Patch Workspace"

        # Check The token sended in the request
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title, token)

        # Get the request body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the workspace data
        workspace: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES,
            column="*",
            where=f"id='{workspace_id}'",
        )

        # Check if the workspace was found
        if workspace == self.error or not workspace:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Check if the user have the right to update the workspace
        if workspace[0]["creator_id"] != int(usr_id):
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title,
            )

        # Update the workspace data
        if "name" in request_body:
            if request_body["name"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_WORKSPACES,
                "id",
                "name",
                workspace_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title, token)
        if "description" in request_body:
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_WORKSPACES,
                "id",
                "description",
                workspace_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title, token)
        if "file" in request_body:
            # Upload the image
            file_url: Union[str, Response] = await self.image_handler_initialised.upload_image(
                bucket_name=CONST.WORKSPACES_PHOTO_BUCKET,
                title=title,
                file=request_body["file"],
                key_name=workspace[0]["name"]
            )
            if isinstance(file_url, Response):
                return file_url

            # Delete old photo from MinIO
            if workspace[0]["favicon"] is not None or workspace[0]["favicon"] != "NULL":
                link: str = workspace[0]["favicon"]
                counter: int = 0
                key_name: str = ""
                for idx, char in enumerate(link):
                    if char == "/":
                        counter += 1
                    if counter == 4:
                        key_name = link[idx + 1:]
                        break
                status: int = self.runtime_data_initialised.bucket_link.delete_file(
                    bucket_name=CONST.WORKSPACES_PHOTO_BUCKET,
                    key_name=key_name
                )
                if status == self.error:
                    return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                        title=title
                    )

            # Update the profile photo of the user
            id_str: str = workspace[0]["id"]
            status: int = self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_WORKSPACES,
                data=[file_url],
                column=["favicon"],
                where=f"id='{id_str}'"
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The workspace information has been updated.",
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_workspace(self, request: Request, workspace_id: str) -> Response:
        """
        Delete a workspace
        """
        title: str = "Delete workspace"

        # Check The token sended in the request
        token: str = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(
            request
        )
        token_valid: bool = self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(
            token
        )
        self.disp.log_debug(f"token = {token}, valid = {token_valid}", title)
        if token_valid is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title, token)

        # Get the user id by the token
        usr_id: Union[str, Any] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the workspace data
        workspace: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES,
            column="*",
            where=f"id='{workspace_id}'",
        )

        # Check if the workspace was found
        if workspace == self.error or not workspace:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Check if the user have the right to delete the workspace
        if workspace[0]["creator_id"] != int(usr_id):
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title,
            )

        # Delete workspace icon from MinIO
        if workspace[0]["favicon"] is not None or workspace[0]["favicon"] != "NULL":
            link: str = workspace[0]["favicon"]
            counter: int = 0
            key_name: str = ""
            for idx, char in enumerate(link):
                if char == "/":
                    counter += 1
                if counter == 4:
                    key_name = link[idx + 1:]
                    break
            status: int = self.runtime_data_initialised.bucket_link.delete_file(
                bucket_name=CONST.WORKSPACES_PHOTO_BUCKET,
                key_name=key_name
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )

        # Delete the workspace
        self.runtime_data_initialised.boilerplate_non_http_initialised.delete_workspace(
            workspace_id=workspace[0]["id"]
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The workspace was deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
