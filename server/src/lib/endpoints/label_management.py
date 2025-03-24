"""
The file that contains the class that handle cards label
"""

from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class CardsLabelManagement:
    """
    The class that handle cards label
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

    async def get_card_labels(self, request: Request, card_id: str) -> Response:
        """
        Get the label of a card
        """
        title: str = "get card label"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the card labels
        card_labels: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CARDS_LABEL,
            column="*",
            where=f"card_id='{card_id}'",
        )

        # Check if the labels was found
        if card_labels == self.error or not card_labels:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The card label was not found.",
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
            message=card_labels,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def add_label(self, request: Request, card_id: str) -> Response:
        """
        Add a label to a card
        """
        title: str = "add label"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not all(key in request_body for key in ("title", "color")) or request_body["title"].strip() == "" or request_body["color"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

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

        # Get the card label
        # card_label: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
        #     table=CONST.TAB_CARDS_LABEL,
        #     column="*",
        #     where=f"card_id='{card_id}'",
        # )

        # Check if the card was found
        # if isinstance(card_label, int) is False:
        #     response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
        #         title=title,
        #         message="The label already exist for the card.",
        #         resp="conflict",
        #         error=True
        #     )
        #     return HCI.conflict(
        #         content=response_body,
        #         content_type=CONST.CONTENT_TYPE,
        #         headers=self.runtime_data_initialised.json_header
        #     )

        # Get columns names of the cards label table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_CARDS_LABEL
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_CARDS_LABEL,
            data=[request_body["title"], request_body["color"], card_id],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The card label was added successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def put_label(self, request: Request, card_id: str, label_id: str) -> Response:
        """
        Modify entirely a label
        """
        title: str = "Put label"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not all(key in request_body for key in ("title", "color")) or request_body["title"].strip() == "" or request_body["color"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Get the card label
        card_label: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CARDS_LABEL,
            column="*",
            where=[f"id='{label_id}'", f"card_id='{card_id}'"],
        )

        # Check if the card label was found
        if card_label == self.error or not card_label:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The card label was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_CARDS_LABEL,
            data=[request_body["title"], request_body["color"]],
            columns=["title", "color"],
            where=f"id='{label_id}'",
            title=title,
            message="The card label information has been updated."
        )

    async def patch_label(self, request: Request, card_id: str, label_id: str) -> Response:
        """
        Modify a label
        """
        title: str = "Patch label"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)

        # Get the card label
        card_label: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CARDS_LABEL,
            column="*",
            where=[f"id='{label_id}'", f"card_id='{card_id}'"],
        )

        # Check if the card label was found
        if card_label == self.error or not card_label:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The card label was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Update the label data
        if "title" in request_body:
            if request_body["title"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_CARDS_LABEL,
                "id",
                "title",
                label_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        if "color" in request_body:
            if request_body["color"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_CARDS_LABEL,
                "id",
                "color",
                label_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The card label information has been updated.",
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_label(self, request: Request, card_id: str, label_id: str) -> Response:
        """
        Delete a label
        """
        title: str = "Delete label"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the card label
        card_label: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_CARDS_LABEL,
            column="*",
            where=[f"id='{label_id}'", f"card_id='{card_id}'"],
        )

        # Check if the card label was found
        if card_label == self.error or not card_label:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The card label was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Delete the card label
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_CARDS_LABEL,
            where=f"id='{label_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The card label was deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
