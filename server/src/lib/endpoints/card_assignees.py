"""
The file that contains the class that handle collaboration on a card
"""

from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class CardAssignees:
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

    async def get_card_assignees(self, request: Request, card_id: str) -> Response:
        """
        get an assignee
        """
        title: str = "add assignee"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the card assignees
        card_assignees: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CARDS_ASSIGNEES,
            column="*",
            where=f"card_id='{card_id}'",
        )

        # Check if the assignees was found
        if card_assignees == self.error or not card_assignees:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The card assignees was not found.",
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
            message=card_assignees,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def add_assignee(self, request: Request, card_id: str) -> Response:
        """
        Add an assignee
        """
        title: str = "add assignee"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not all(key in request_body for key in ("user_id", "workspace_id")) or request_body["user_id"].strip() == "" or request_body["workspace_id"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Get the workspace member
        user_id = request_body.get("user_id")
        workspace_id = request_body.get("workspace_id")
        member: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            column="*",
            where=[f"workspace_id='{workspace_id}'", f"user_id='{user_id}'"]
        )

        # Check if the workspace member was found
        if member == self.error or not member:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The user was not found in the workspace.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Get the card
        card: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=f"id='{card_id}'",
        )

        # Check if the card was found
        if card == self.error or not card:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The card was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_CARDS_ASSIGNEES,
            data=[user_id, card_id],
            column=["user_id", "card_id"]
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The user was added in the card assignees successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_assignee(self, request: Request, card_id: str, user_id: str) -> Response:
        """
        Delete an assignee
        """
        title: str = "Delete assignee"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the card assignee
        card_assignee: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CARDS_ASSIGNEES,
            column="*",
            where=[f"user_id='{user_id}'", f"card_id='{card_id}'"]
        )

        # Check if the card assignee was found
        if card_assignee == self.error or not card_assignee:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The card assignee was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_CARDS_ASSIGNEES,
            where=[f"user_id='{user_id}'", f"card_id='{card_id}'"]
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The card assignee was deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
