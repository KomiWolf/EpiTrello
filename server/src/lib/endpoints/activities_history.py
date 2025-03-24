"""
The file that contains the class that handle any boards activities history
"""

from typing import Union, List, Dict, Any
from datetime import datetime
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class ActivitiesHistory:
    """
    The class that handle any boards activities history
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

    async def get_board_activities(self, request: Request, board_id: str) -> Response:
        """
        Get a board activities
        """
        title: str = "Get board activities"

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

        # Get the activities data
        activities: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_ACTIVITIES,
            column="*",
            where=f"board_id='{board_id}'",
        )

        # Check if the activities were found
        if activities == self.error or not activities:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The activities were not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        for _, activity in enumerate(activities):
            if activity["created_at"] is not None:
                activity["created_at"] = activity["created_at"].isoformat()

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=activities,
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def add_activity(self, request: Request, board_id: str) -> Response:
        """
        Add an activity
        """
        title: str = "add activity"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not request_body.get("message") or request_body["message"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Get the board data
        board: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS,
            column="*",
            where=f"id='{board_id}'",
        )

        # Check if the boards was found
        if board == self.error or not board:
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

        # Get columns names of the activities history table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_BOARDS_ACTIVITIES
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        # Insert the data to the activities history table
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_BOARDS_ACTIVITIES,
            data=[request_body["message"], str(datetime.now().replace(microsecond=0)), board_id],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The activity has been created successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_activity(self, request: Request, board_id: str, activity_id: str) -> Response:
        """
        Delete an activity
        """
        title: str = "delete activity"

        # Token checking
        token: Union[str, None] = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the activity data
        activity: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_ACTIVITIES,
            column="*",
            where=[f"id='{activity_id}'", f"board_id='{board_id}'"],
        )

        # Check if the activity was found
        if activity == self.error or not activity:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The activity was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Delete the activity
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_BOARDS_ACTIVITIES,
            where=f"id='{activity_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The activity was deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_activities(self, request: Request, board_id: str) -> Response:
        """
        Delete every activities of a board
        """
        title: str = "delete activities"

        # Token checking
        token: Union[str, None] = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the activities data
        activities: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_ACTIVITIES,
            column="*",
            where=f"board_id='{board_id}'",
        )

        # Check if the activities was found
        if activities == self.error or not activities:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The activities were not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Delete the activities
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_BOARDS_ACTIVITIES,
            where=f"board_id='{board_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The activities were deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
