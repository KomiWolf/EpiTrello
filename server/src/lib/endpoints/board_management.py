"""
The file that contains the class that handle boards management
"""

from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class BoardsManagement:
    """
    The class that handle boards management
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

    async def get_workspace_boards(self, request: Request, workspace_id: str) -> Response:
        """
        Get every boards of a workspace
        """
        title: str = "Get workspace boards"

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

        # Get the boards data
        boards: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS,
            column="*",
            where=f"workspace_id='{workspace_id}'",
        )

        # Check if the boards was found
        if boards == self.error or not boards:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The boards was not found.",
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
            message=boards,
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_board_by_id(self, request: Request, board_id: str) -> Response:
        """
        Get a board by his id
        """
        title: str = "Get boards by id"

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

        # Get the boards data
        board: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS,
            column="*",
            where=f"id='{board_id}'",
        )

        # Check if the board was found
        if board == self.error or not board:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The board was not found.",
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
            message=board[0],
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def create_board(self, request: Request, workspace_id: str) -> Response:
        """
        Create a board
        """
        title: str = "Create board"

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
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Check if every required information is in the request body
        if not request_body or not all(key in request_body for key in ("name", "background_color")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        if request_body["name"] == "" or request_body["background_color"] == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        workspace_member: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title,
        )
        if isinstance(workspace_member, Response):
            return workspace_member

        # Check the user right
        if workspace_member[0]["admin"] == 0 and workspace_member[0]["board_creation_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Get columns names of the boards table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_BOARDS
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        # Insert the data to the boards table
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_BOARDS,
            data=[request_body["name"], request_body["background_color"], "0", workspace_id],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The board has been created successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def put_board(self, request: Request, board_id: str, workspace_id: str) -> Response:
        """
        Update a board by his id
        """
        title: str = "Put board"

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
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Check if every required information is in the request body
        if not request_body or not all(key in request_body for key in ("name", "background_color")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        if request_body["name"] == "" or request_body["background_color"] == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        workspace_member: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(workspace_member, Response):
            return workspace_member

        # Check the user right
        if workspace_member[0]["admin"] == 0 and workspace_member[0]["board_creation_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Update the data to the boards table
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_BOARDS,
            data=[request_body["name"] , request_body["background_color"]],
            columns=["name", "background_color"],
            where=f"id='{board_id}'",
            title=title,
            message="The board information has been updated."
        )

    async def patch_board(self, request: Request, board_id: str, workspace_id: str) -> Response:
        """
        Update a board by his id
        """
        title = "Patch board"

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
                title,
                token
            )

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Get the user id by the token
        usr_id = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        workspace_member: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(workspace_member, Response):
            return workspace_member

        # Check the user right
        if workspace_member[0]["admin"] == 0 and workspace_member[0]["board_creation_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Update the board data
        if "name" in request_body:
            if request_body["name"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_BOARDS,
                "id",
                "name",
                board_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title, token)
        if "background_color" in request_body:
            if request_body["background_color"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_BOARDS,
                "id",
                "background_color",
                board_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title, token)

        # Set the response body
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The board information has been updated.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_board(self, request: Request, board_id: str, workspace_id: str) -> Response:
        """
        Update a board by his id
        """
        title: str = "Delete board"

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
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        workspace_member: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(workspace_member, Response):
            return workspace_member

        # Check the user right
        if workspace_member[0]["admin"] == 0 and workspace_member[0]["board_deletion_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Delete the board
        status: int = self.runtime_data_initialised.boilerplate_non_http_initialised.delete_board(
            board_id=board_id
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The board was deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
