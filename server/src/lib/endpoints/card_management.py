"""
The file that contains the class that handle card management
"""

from typing import Union, List, Dict, Any
from datetime import datetime
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class CardManagement:
    """
    The class that handle card management
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

    async def get_card_by_id(self, request: Request, list_id: str, card_id: str) -> Response:
        """
        Get card by his id
        """
        title: str = "Get card by his id"

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

        # Get the card data
        card: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=[f"id='{card_id}'", f"list_id='{list_id}'"],
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

        if card[0]["date_end"] is not None:
            card[0]["date_end"] = card[0]["date_end"].isoformat()

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=card[0],
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_list_cards(self, request: Request, list_id: str) -> Response:
        """
        Get every cards of a list
        """
        title: str = "Get every cards of a list"

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

        # Get the cards data
        cards: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=f"list_id='{list_id}'",
        )

        # Check if the cards was found
        if cards == self.error or not cards:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The cards was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        for _, card in enumerate(cards):
            if card["date_end"] is not None:
                card["date_end"] = card["date_end"].isoformat()

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=cards,
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def create_card(self, request: Request, list_id: str) -> Response:
        """
        Create a card
        """
        title: str = "Create a card"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not all(key in request_body for key in ("name", "description")) or request_body["name"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        date_end = request_body.get("date_end")
        if date_end:
            try:
                date_end = datetime.strptime(date_end, "%Y-%m-%d")
            except ValueError:
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                    title=title
                )
        else:
            date_end = None

        # Get the list number from the board
        searched_list: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"id='{list_id}'",
        )

        # Check if the list was found
        if searched_list == self.error or not searched_list:
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

        # Get columns names of the boards table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_LISTS_CARDS
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        cards_nb: str = str(searched_list[0]["card_nb"] + 1)

        # Insert the data to the boards table
        if date_end is not None:
            status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
                table=CONST.TAB_LISTS_CARDS,
                data=[request_body["name"], request_body["description"], date_end.isoformat(), list_id, cards_nb],
                column=columns
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )
        else:
            columns.pop(2)
            status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
                table=CONST.TAB_LISTS_CARDS,
                data=[request_body["name"], request_body["description"], list_id, cards_nb],
                column=columns
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                    title=title
                )

        status: int = self.runtime_data_initialised.database_link.update_data_in_table(
            table=CONST.TAB_BOARDS_LISTS,
            data=[cards_nb],
            column=["card_nb"],
            where=f"id={list_id}"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The card has been created successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def put_card(self, request: Request, list_id: str, card_id: str) -> Response:
        """
        Modify entirely a card
        """
        title: str = "Modify entirely a card"

        # Token checking
        token: Union[str, None] = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not all(key in request_body for key in ("name", "description")) or request_body["name"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Get the card data
        card: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=[f"id='{card_id}'", f"list_id='{list_id}'"],
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

        # Update the workspace data
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_LISTS_CARDS,
            data=[request_body["name"], request_body["description"]],
            columns=["name", "description"],
            where=f"id='{card_id}'",
            title=title,
            message="The card information has been updated."
        )

    async def update_card_position(self, request: Request, list_id: str, card_id: str) -> Response:
        """
        Update the position of a card and eventually update the list where it is
        """
        title: str = "Update card position"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not request_body.get("position") or not request_body.get("new_list_id"):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        new_list_id: str = str(request_body["new_list_id"])

        # Get the new list data
        new_list: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"id='{new_list_id}'"
        )

        # Check if the list was found
        if new_list == self.error or not new_list:
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

        # Get the card data
        card: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=[f"id='{card_id}'", f"list_id='{list_id}'"]
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

        current_card_position: int = card[0]["position"]
        new_position: int = int(request_body["position"])

        # Check if the position is a correct position
        if (new_list_id != list_id):
            if (new_position <= 0 or new_position > new_list[0]["card_nb"] + 1):
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
        else:
            if (new_position <= 0 or new_position > new_list[0]["card_nb"]):
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
        if (current_card_position == new_position and list_id == new_list_id):
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

        # Get the cards list of the new list
        list_cards: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=f"list_id='{new_list_id}'"
        )

        if (list_id != new_list_id):
            self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_LISTS_CARDS,
                data=[new_list_id],
                column=["list_id"],
                where=f"id='{card_id}'"
            )

            old_list: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
                table=CONST.TAB_BOARDS_LISTS,
                column="*",
                where=f"id='{list_id}'"
            )

            self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_BOARDS_LISTS,
                data=[str(old_list[0]["card_nb"] - 1)],
                column=["card_nb"],
                where=f"id='{list_id}'"
            )

            self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_BOARDS_LISTS,
                data=[str(new_list[0]["card_nb"] + 1)],
                column=["card_nb"],
                where=f"id='{new_list_id}'"
            )

            # Update the cards position of the old list
            old_list_cards: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
                table=CONST.TAB_LISTS_CARDS,
                column="*",
                where=f"list_id='{list_id}'"
            )

            if isinstance(old_list_cards, int):
                # Decrement the card count in the list
                status: int = self.runtime_data_initialised.database_link.update_data_in_table(
                    table=CONST.TAB_BOARDS_LISTS,
                    data=["0"],
                    column=["card_nb"],
                    where=f"id='{list_id}'"
                )
                if status == self.error:
                    return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title=title)
            else:
                for _, list_card in enumerate(old_list_cards):
                    if list_card["position"] >= current_card_position:
                        self.runtime_data_initialised.database_link.update_data_in_table(
                            table=CONST.TAB_LISTS_CARDS,
                            data=[str(list_card["position"] - 1)],
                            column=["position"],
                            where=f"id={list_card['id']}"
                        )

            # Get the cards list of the new list
            list_cards: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
                table=CONST.TAB_LISTS_CARDS,
                column="*",
                where=f"list_id='{new_list_id}'"
            )

            # Update the cards position of the new list
            for _, list_card in enumerate(list_cards):
                if list_card["id"] == int(card_id):
                    self.runtime_data_initialised.database_link.update_data_in_table(
                        table=CONST.TAB_LISTS_CARDS,
                        data=[str(new_position)],
                        column=["position"],
                        where=f"id='{card_id}'"
                    )
                else:
                    if list_card["position"] >= new_position:
                        self.runtime_data_initialised.database_link.update_data_in_table(
                            table=CONST.TAB_LISTS_CARDS,
                            data=[str(list_card["position"] + 1)],
                            column=["position"],
                            where=f"id={list_card['id']}"
                        )
        else:
            for _, list_card in enumerate(list_cards):
                if list_card["id"] == int(card_id):
                    self.runtime_data_initialised.database_link.update_data_in_table(
                        table=CONST.TAB_LISTS_CARDS,
                        data=[str(new_position)],
                        column=["position"],
                        where=f"id='{card_id}'"
                    )
                else:
                    if new_position > current_card_position:
                        if list_card["position"] >= current_card_position and list_card["position"] <= new_position:
                            self.runtime_data_initialised.database_link.update_data_in_table(
                                table=CONST.TAB_LISTS_CARDS,
                                data=[str(list_card["position"] - 1)],
                                column=["position"],
                                where=f"id={list_card['id']}"
                            )
                    elif new_position < current_card_position:
                        if list_card["position"] >= new_position and list_card["position"] <= current_card_position:
                            self.runtime_data_initialised.database_link.update_data_in_table(
                                table=CONST.TAB_LISTS_CARDS,
                                data=[str(list_card["position"] + 1)],
                                column=["position"],
                                where=f"id={list_card['id']}"
                            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The card position has been updated successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def patch_card(self, request: Request, list_id: str, card_id: str) -> Response:
        """
        Modify one value of a card
        """
        title: str = "Modify one value of a card"

        # Token checking
        token: Union[str, None] = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)

        # Get the card data
        card: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=[f"id='{card_id}'", f"list_id='{list_id}'"],
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

        # Update the workspace data
        if "name" in request_body:
            if request_body["name"] == "":
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_LISTS_CARDS,
                "id",
                "name",
                card_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        if "description" in request_body:
            if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                CONST.TAB_LISTS_CARDS,
                "id",
                "description",
                card_id,
                request_body
            ) == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        if "date_end" in request_body:
            date_end = request_body.get("date_end")
            if date_end:
                try:
                    request_body["date_end"] = datetime.strptime(date_end, "%Y-%m-%d")
                    request_body["date_end"] = request_body["date_end"].isoformat()
                    if self.runtime_data_initialised.boilerplate_non_http_initialised.update_single_data(
                        CONST.TAB_LISTS_CARDS,
                        "id",
                        "date_end",
                        card_id,
                        request_body
                    ) == self.error:
                        return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
                except ValueError:
                    return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                        title=title,
                    )
            else:
                return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                        title=title,
                    )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The card information has been updated.",
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_card(self, request: Request, list_id: str, card_id: str) -> Response:
        """
        Delete a card
        """
        title: str = "Delete a card"

        # Token checking
        token: Union[str, None] = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the card data
        card: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=[f"id='{card_id}'", f"list_id='{list_id}'"],
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

        current_position: int = card[0]["position"]

        # Delete the card
        self.runtime_data_initialised.boilerplate_non_http_initialised.delete_card(card_id=int(card_id))

        # Get the list number from the board
        searched_list: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_BOARDS_LISTS,
            column="*",
            where=f"id='{list_id}'",
        )

        # Check if the list was found
        if searched_list == self.error or not searched_list:
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

        list_cards: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_LISTS_CARDS,
            column="*",
            where=f"list_id='{list_id}'"
        )

        if isinstance(list_cards, int):
            # Decrement the card count in the list
            status: int = self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_BOARDS_LISTS,
                data=["0"],
                column=["card_nb"],
                where=f"id='{list_id}'"
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title=title)
        else:
            # Decrement the position of every cards after the deleted card
            for _, list_card in enumerate(list_cards):
                if list_card["position"] >= current_position:
                    self.runtime_data_initialised.database_link.update_data_in_table(
                        table=CONST.TAB_LISTS_CARDS,
                        data=[str(list_card["position"] - 1)],
                        column=["position"],
                        where=f"id={list_card['id']}"
                    )

            # Decrement the card count in the list
            cards_nb: str = str(searched_list[0]["card_nb"] - 1)
            status: int = self.runtime_data_initialised.database_link.update_data_in_table(
                table=CONST.TAB_BOARDS_LISTS,
                data=[cards_nb],
                column=["card_nb"],
                where=f"id='{list_id}'"
            )
            if status == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title=title)

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The cards was deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
