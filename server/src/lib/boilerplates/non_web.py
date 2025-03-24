"""
    This is the the class in charge of containing the non-http boilerplates.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Union, List, Dict, Any

from fastapi import Response
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME

from .. import RuntimeData, CONST
from ..sql.sql_manager import SQL
from ..http_codes import HCI

class BoilerplateNonHTTP:
    """
    The class that contains every non HTTP method
    """

    def __init__(self, runtime_data_initialised: RuntimeData, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """
        Constructor
        """
        self.debug: bool = debug
        self.error: int = error
        self.success: int = success
        self.runtime_data_initialised: RuntimeData = runtime_data_initialised
        # ------------------------ The logging function ------------------------
        self.disp: Disp = Disp(
            TOML_CONF,
            FILE_DESCRIPTOR,
            SAVE_TO_FILE,
            FILE_NAME,
            debug=self.debug,
            logger=self.__class__.__name__
        )

    def pause(self) -> str:
        """
            This is a pause function that works in the same wat as the batch pause command.
            It pauses the program execution until the user presses the enter key.

        Returns:
            str: The input from the user
        """
        return input("Press enter to continue...")

    def set_lifespan(self, seconds: int) -> datetime:
        """
                The function to set the lifespan of the user token
            Args:
                seconds (int): Seconds

            Returns:
                datetime: The datetime of the lifespan of the token
            """
        current_time = datetime.now()
        offset_time = current_time + timedelta(seconds=seconds)
        return offset_time

    def is_token_correct(self, token: str) -> bool:
        """
            Check if the token is correct.
        Args:
            token (str): The token to check

        Returns:
            bool: True if the token is correct, False otherwise
        """
        title = "is_token_correct"
        self.disp.log_debug("Checking if the token is correct.", title)
        if isinstance(token, str) is False:
            return False
        login_table = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_CONNECTIONS,
            "*",
            where=f"token={token}",
            beautify=False
        )
        if isinstance(login_table, int):
            return False
        self.disp.log_debug(f"login_table = {login_table}", title)
        return True

    def generate_token(self) -> str:
        """
            This is a function that will generate a token for the user.
        Returns:
            str: The token generated
        """
        title = "generate_token"
        token = str(uuid.uuid4())
        user_token = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="token",
            where=f"token='{token}'",
            beautify=False
        )
        self.disp.log_debug(f"user_token = {user_token}", title)
        while len(user_token) > 0:
            token = str(uuid.uuid4())
            user_token = self.runtime_data_initialised.database_link.get_data_from_table(
                table=CONST.TAB_CONNECTIONS,
                column="token",
                where=f"token='{token}'",
                beautify=False
            )
            self.disp.log_debug(f"user_token = {user_token}", title)
            if isinstance(user_token, int) is True and user_token == self.error:
                return token
            if len(user_token) == 0:
                return token
        return token

    def check_date(self, date: str = "DD/MM/YYYY") -> bool:
        """
            This is a function that will check if the date is correct or not.
        Args:
            date (str, optional): The date to check. Defaults to "DD/MM/YYYY".

        Returns:
            bool: True if the date is correct, False otherwise
        """
        pattern = re.compile(
            r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}$"
        )
        match = pattern.match(date)
        return bool(match)

    def check_database_health(self) -> None:
        """
            This function will reconnect to the database in case it has been disconnected.
        """
        if self.runtime_data_initialised.database_link is None:
            try:
                self.disp.log_debug(
                    "database_link is none, initialising sql.",
                    "check_database_health"
                )
                self.runtime_data_initialised.database_link = SQL(
                    url=CONST.DB_HOST,
                    port=CONST.DB_PORT,
                    username=CONST.DB_USER,
                    password=CONST.DB_PASSWORD,
                    db_name=CONST.DB_DATABASE,
                    success=self.success,
                    error=self.error,
                    debug=self.debug
                )
            except RuntimeError as e:
                msg = "Could not connect to the database."
                raise RuntimeError(msg) from e

        if self.runtime_data_initialised.database_link.is_connected() is False:
            if self.runtime_data_initialised.database_link.connect_to_db() is False:
                try:
                    self.disp.log_debug(
                        "database_link is none, initialising sql.",
                        "check_database_health"
                    )
                    self.runtime_data_initialised.database_link = SQL(
                        url=CONST.DB_HOST,
                        port=CONST.DB_PORT,
                        username=CONST.DB_USER,
                        password=CONST.DB_PASSWORD,
                        db_name=CONST.DB_DATABASE,
                        success=self.success,
                        error=self.error,
                        debug=self.debug
                    )
                except RuntimeError as e:
                    msg = "(check_database_health) Could not connect to the database."
                    raise RuntimeError(msg) from e

    def get_user_id_from_token(self, title: str, token: str) -> Union[str, Response]:
        """
            The function in charge of getting the user id based of the provided content.

        Args:
            title (str): The title of the endpoint calling it
            token (str): The token of the user account

        Returns:
            Union[str, Response]: Returns as string id if success, otherwise, a pre-made response for the endpoint.
        """
        function_title = "get_user_id_from_token"
        usr_id_node: str = "user_id"
        self.disp.log_debug(
            f"Getting user id based on {token}", function_title
        )
        current_user: List[Dict[str]] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CONNECTIONS,
            column="*",
            where=f"token='{token}'",
            beautify=True
        )
        self.disp.log_debug(f"current_user = {current_user}", function_title)
        if current_user == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(title)
        self.disp.log_debug(
            f"user_length = {len(current_user)}", function_title
        )
        if len(current_user) == 0 or len(current_user) > 1:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(title)
        self.disp.log_debug(
            f"current_user[0] = {current_user[0]}", function_title
        )
        if usr_id_node not in current_user[0]:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(title)
        msg = "str(current_user[0]["
        msg += f"{usr_id_node}]) = {str(current_user[0][usr_id_node])}"
        self.disp.log_debug(msg, function_title)
        return str(current_user[0][usr_id_node])

    def update_single_data(self, table: str, column_finder: str, column_to_update: str, data_finder: str, request_body: dict) -> int:
        """
        The function in charge of updating the data in the database
        """
        if self.runtime_data_initialised.database_link.update_data_in_table(
            table,
            [request_body[column_to_update]],
            [column_to_update],
            f"{column_finder}='{data_finder}'"
        ) == self.error:
            return self.error
        return self.success

    def delete_card(self, card_id: int) -> int:
        """
        Delete a card list
        """
        # Delete the card assignees
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_CARDS_ASSIGNEES,
            where=f"card_id='{card_id}'"
        )

        # Delete the card assignees
        return self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            where=f"id='{card_id}'"
        )

    def delete_list(self, list_id: int) -> int:
        """
        Delete a board list
        """
        # Get every board lists id by the board_id
        cards_id: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="id",
            where=f"list_id='{list_id}'",
        )

        # Delete every card in the list
        if isinstance(cards_id, int) is False:
            for _, card in enumerate(cards_id):
                self.delete_card(card_id=card["id"])

        # Delete the list
        return self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            where=f"id='{list_id}'"
        )

    def delete_board(self, board_id: int) -> int:
        """
        Delete a workspace board
        """
        # Delete the board activities
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_BOARDS_ACTIVITIES,
            where=f"board_id='{board_id}'"
        )

        # Get every board lists id by the board_id
        lists_id: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="id",
            where=f"board_id='{board_id}'",
        )

        # Delete every board in the list
        if isinstance(lists_id, int) is False:
            for _, board_list in enumerate(lists_id):
                self.delete_list(list_id=board_list["id"])

        # Delete the board
        return self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_BOARDS,
            where=f"id='{board_id}'"
        )

    def delete_workspace(self, workspace_id: int) -> None:
        """
        The function to delete every data of a workspace
        """
        # Delete the workspace invitation
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            where=f"workspace_id='{workspace_id}'"
        )

        # Delete the workspace member
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            where=f"workspace_id='{workspace_id}'"
        )

        # Get every boards id by the workspace_id
        boards_id: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS,
            column="id",
            where=f"workspace_id='{workspace_id}'",
        )

        # Delete every board in the list
        if isinstance(boards_id, int) is False:
            for _, board in enumerate(boards_id):
                self.delete_board(board_id=board["id"])

        # Delete the workspace
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_WORKSPACES,
            where=f"id='{workspace_id}'"
        )

    def get_workspace_member(self, user_id: str, workspace_id: str, title: str) -> Union[List[Dict[str, Any]], Response]:
        """
        A function to get a workspace member
        """
        workspace_member: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            column="*",
            where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
        )

        # Check if the workspace member was found
        if workspace_member == self.error or not workspace_member:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace member was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )
        return workspace_member

    def update_table_values(self, table: str, data: List[Any], columns: List[str], where: str, title: str, message: str) -> Response:
        """
        A function to update a SQL table values
        """
        status: int = self.runtime_data_initialised.database_link.update_data_in_table(
            table=table,
            data=data,
            column=columns,
            where=where,
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=message,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
