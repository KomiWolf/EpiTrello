"""
The file that contains the class that handle list management
"""

from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class ListsManagement:
    """
    The class that handle list management
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

    async def get_lists(self, request: Request, board_id: str) -> Response:
        """
        Get every lists of a board
        """
        title: str = "Get lists"

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

        # Get the lists data
        lists: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"board_id='{board_id}'",
        )

        # Check if the lists was found
        if lists == self.error or not lists:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The lists was not found.",
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
            message=lists,
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_list_by_id(self, request: Request, board_id: str, list_id: str) -> Response:
        """
        Get a list by his id
        """
        title: str = "Get list by id"

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

        # Get the lists data
        single_list: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=[f"id='{list_id}'", f"board_id='{board_id}'"],
        )

        # Check if the lists was found
        if single_list == self.error or not single_list:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The list was not found.",
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
            message=single_list[0],
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def create_list(self, request: Request, board_id: str) -> Response:
        """
        Create a new list
        """
        title: str = "Create list"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not request_body.get("name") or request_body["name"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Get the list number from the board
        board: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS,
            column="*",
            where=f"id='{board_id}'",
        )

        # Check if the boards was found
        if board == self.error or not board:
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

        # Get columns names of the boards table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_BOARDS_LISTS
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        lists_nb: str = str(board[0]["list_nb"] + 1)
        # Insert the data to the boards table
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_BOARDS_LISTS,
            data=[request_body["name"], board_id, lists_nb, "0"],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        status: int = self.runtime_data_initialised.database_link.update_data_in_table(
            table=CONST.TAB_BOARDS,
            data=[lists_nb],
            column=["list_nb"],
            where=f"id={board_id}"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The list has been created successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def update_list_name(self, request: Request, list_id: str) -> Response:
        """
        Update the name of a list
        """
        title: str = "Update list name"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not request_body.get("name") or request_body["name"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Update the list name in the database
        status: int = self.runtime_data_initialised.database_link.update_data_in_table(
            table=CONST.TAB_BOARDS_LISTS,
            data=[request_body["name"]],
            column=["name"],
            where=f"id='{list_id}'"
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title=title)

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The list name has been updated successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def update_list_position(self, request: Request, list_id: str) -> Response:
        """
        Update the position of a list and reorganize the affected lists
        """
        title: str = "Update list position"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not request_body.get("position"):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Get the current list data
        current_list: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"id='{list_id}'"
        )

        # Check if the list was found
        if current_list == self.error or not current_list:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The lists was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        current_list: Dict[str, Any] = current_list[0]
        current_position: int = current_list["position"]
        new_position: int = int(request_body["position"])
        board_id: int = current_list["board_id"]

        board_data: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS,
            column="*",
            where=f"id='{board_id}'"
        )

        if (new_position <= 0 or new_position > board_data[0]["list_nb"]):
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The given list position is not authorized.",
                resp="forbidden"
            )

            # Send the response
            return HCI.forbidden(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # If no position change, return success
        if current_position == new_position:
            # Set the response body
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The list position remains the same.",
                resp="success"
            )

            # Send the response
            return HCI.success(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        board_lists: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"board_id='{board_id}'"
        )

        for _, board_list in enumerate(board_lists):
            if board_list["id"] == int(list_id):
                self.runtime_data_initialised.database_link.update_data_in_table(
                    table=CONST.TAB_BOARDS_LISTS,
                    data=[str(new_position)],
                    column=["position"],
                    where=f"id='{list_id}'"
                )
            else:
                if new_position > current_position:
                    if board_list["position"] >= current_position and board_list["position"] <= new_position:
                        self.runtime_data_initialised.database_link.update_data_in_table(
                            table=CONST.TAB_BOARDS_LISTS,
                            data=[str(board_list["position"] - 1)],
                            column=["position"],
                            where=f"id={board_list['id']}"
                        )
                elif new_position < current_position:
                    if board_list["position"] >= new_position and board_list["position"] <= current_position:
                        self.runtime_data_initialised.database_link.update_data_in_table(
                            table=CONST.TAB_BOARDS_LISTS,
                            data=[str(board_list["position"] + 1)],
                            column=["position"],
                            where=f"id={board_list['id']}"
                        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The list position has been updated successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_list(self, request: Request, list_id: str) -> Response:
        """
        Delete a list and adjust the positions and list count
        """
        title: str = "Delete list"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the current list data
        current_list: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"id='{list_id}'"
        )

        # Check if the list was found
        if current_list == self.error or not current_list:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The lists was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        current_list: Dict[str, Any] = current_list[0]
        current_position: int = current_list["position"]
        board_id: int = current_list["board_id"]

        # Delete the list
        status: int = self.runtime_data_initialised.database_link.remove_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            where=f"id='{list_id}'"
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title=title)

        board_lists: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"board_id='{board_id}'"
        )

        if isinstance(board_lists, int):
            # Decrement the list count in the board
            status: int = self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_BOARDS,
                data=["0"],
                column=["list_nb"],
                where=f"id='{board_id}'"
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title=title)
        else:
            # Decrement the position of every lists after the deleted list
            for _, board_list in enumerate(board_lists):
                if board_list["position"] >= current_position:
                    self.runtime_data_initialised.database_link.update_data_in_table(
                        table=CONST.TAB_BOARDS_LISTS,
                        data=[str(board_list["position"] - 1)],
                        column=["position"],
                        where=f"id={board_list['id']}"
                    )

            # Decrement the list count in the board
            status: int = self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_BOARDS,
                data=[str(len(board_lists))],
                column=["list_nb"],
                where=f"id='{board_id}'"
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title=title)

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The list has been deleted successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
