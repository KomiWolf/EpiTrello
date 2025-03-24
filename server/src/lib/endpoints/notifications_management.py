"""
The file that contains the class that handle users notifications
"""

from typing import Union, List, Dict, Any
from datetime import datetime
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class Notifications:
    """
    The class that handle users notifications
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

    async def get_user_notifications(self, request: Request) -> Response:
        """
        Get a user notification by his token
        """
        title: str = "get_user_notifications"

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

        # Get the user id
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the notifications data
        notifications: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            column="*",
            where=f"user_id='{usr_id}'",
        )

        # Check if the notifications were found
        if notifications == self.error or not notifications:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The notifications were not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        for _, notification in enumerate(notifications):
            if notification["created_at"] is not None:
                notification["created_at"] = notification["created_at"].isoformat()

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=notifications,
            resp="success",
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def add_user_notification(self, request: Request, user_id: str) -> Response:
        """
        Add a notification to a user
        """
        title: str = "add_user_notification"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the request body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        if not request_body or not request_body.get("message") or request_body["message"].strip() == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title=title)

        # Get the user data
        user: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"id='{user_id}'",
        )

        # Check if the user was found
        if user == self.error or not user:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The user was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Get columns names of the notifications table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_NOTIFICATIONS
        )
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        # Insert the data to the notifications table
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_NOTIFICATIONS,
            data=[request_body["message"], user_id, "0", str(datetime.now().replace(microsecond=0))],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The notification has been created successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def set_notification_to_read(self, request: Request, notification_id: str) -> Response:
        """
        Set a notification to read
        """
        title: str = "set_notification_to_read"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the user id
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the notification data
        notifications: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            column="*",
            where=[f"id='{notification_id}'", f"user_id='{usr_id}'"],
        )

        # Check if the notification were found
        if notifications == self.error or not notifications:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The notification was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        status: int = self.runtime_data_initialised.database_link.update_data_in_table(
            table=CONST.TAB_NOTIFICATIONS,
            data=["1"],
            column=["is_read"],
            where=f"id='{notification_id}'"
        )

        if status == self.error:
            self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The notification has been set to read successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def set_every_notifications_to_read(self, request: Request) -> Response:
        """
        Set every notifications of a user to read
        """
        title: str = "set_notification_to_read"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the user id
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the notifications data
        notifications: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            column="*",
            where=f"user_id='{usr_id}'",
        )

        # Check if the notifications were found
        if notifications == self.error or not notifications:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The notifications were not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        status: int = self.runtime_data_initialised.database_link.update_data_in_table(
            table=CONST.TAB_NOTIFICATIONS,
            data=["1"],
            column=["is_read"],
            where=f"user_id='{usr_id}'"
        )

        if status == self.error:
            self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The notifications have been set to read successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_notification(self, request: Request, notification_id: str) -> Response:
        """
        Delete a notification
        """
        title: str = "delete_notification"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the user id
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the notification data
        notification: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            column="*",
            where=[f"id='{notification_id}'", f"user_id='{usr_id}'"],
        )

        # Check if the notification were found
        if notification == self.error or not notification:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The notification was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Delete the notification
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            where=f"id='{notification_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The notification has been deleted successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_notifications(self, request: Request) -> Response:
        """
        Delete every user notifications
        """
        title: str = "delete notifications"

        # Token checking
        token = self.runtime_data_initialised.boilerplate_incoming_initialised.get_token_if_present(request)
        if not self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(title=title)

        # Get the user id
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title=title,
            token=token
        )
        self.disp.log_debug(f"user_id = {usr_id}", title)
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the notification sdata
        notifications: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            column="*",
            where=f"user_id='{usr_id}'",
        )

        # Check if the notifications were found
        if notifications == self.error or not notifications:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The notifications were not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Delete the notifications
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_NOTIFICATIONS,
            where=f"user_id='{usr_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The notifications have been deleted successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
