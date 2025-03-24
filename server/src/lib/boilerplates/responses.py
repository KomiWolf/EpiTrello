"""
    File containing boilerplate responses that could be used by the server in it's endpoints_initialised.
"""
from typing import Union, Dict, Any
from fastapi import Response
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import HCI, RuntimeData, CONST

class BoilerplateResponses:
    """
    """

    def __init__(self, runtime_data: RuntimeData, debug: bool = False) -> None:
        """

        Args:
            debug (bool, optional): _description_. Defaults to False.
        """
        self.debug: bool = debug
        self.runtime_data_initialised: RuntimeData = runtime_data
        self.disp: Disp = Disp(
            TOML_CONF,
            SAVE_TO_FILE,
            FILE_NAME,
            FILE_DESCRIPTOR,
            debug=self.debug,
            logger=self.__class__.__name__
        )

    def build_response_body(self, title: str, message: str, resp: Any, error: bool = False) -> Dict[str, Any]:
        """
            This is a function that will create a response body for the queries of the server.
        Args:
            title (str): The title of the message in the body
            message (any): The actual message you wish to send (this is so that it is human friendly [i.e. "You have successfully logged in"])
            resp (any): The section where you can put more coder side data.
            token Union[str, None]: The user token or None if not present
            error (bool, optional): If this is an error message or not. Defaults to False.

        Returns:
            Dict[str, any]: the final version of the body message
        """
        func_title = "build_response_body"
        json_body = {}
        msg = f"title={title}, message={message}, resp={resp},"
        msg += f" error={error}"
        self.disp.log_debug(msg, func_title)

        json_body[CONST.JSON_TITLE] = title
        json_body[CONST.JSON_MESSAGE] = message
        if error is False:
            json_body[CONST.JSON_RESP] = resp
        else:
            json_body[CONST.JSON_ERROR] = resp
        return json_body

    def invalid_token(self, title: str) -> Response:
        """
            This is a function that will return an invalid token response.

        Args:
            title (str): The title of the called endpoint

        Returns:
            Response: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The token you entered is invalid.",
            resp="Invalid token",
            error=True
        )
        return HCI.invalid_token(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def not_logged_in(self, title: str) -> Response:
        """
            This is a function that will return a not logged in response.

        Args:
            title (str): The title of the called endpoint

        Returns:
            Response: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="You need to be logged in to be able to run this endpoint.",
            resp="User not logged in",
            error=True
        )
        return HCI.unauthorized(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def login_failed(self, title: str) -> Response:
        """
            This is a function that will return a failed login response.

        Args:
            title (str): The title of the called endpoint

        Returns:
            Response: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="Login failed, invalid credentials or username.",
            resp="Invalid credentials or username.",
            error=True
        )
        return HCI.unauthorized(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def insuffisant_rights(self, title: str) -> Response:
        """
            This is a function that will return an insuffisant rights response.

        Args:
            title (str): The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.:  The token provided by the user of the called endpoint

        Returns:
            Response: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="You do not have enough permissions to execute this endpoint.",
            resp="Insufficient rights for given account.",
            error=True
        )
        return HCI.forbidden(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def bad_request(self, title: str) -> Response:
        """
            This is a function that will return a bad request response.

        Args:
            title (str): The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The request was not formatted correctly.",
            resp="Bad request",
            error=True
        )
        return HCI.bad_request(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def internal_server_error(self, title: str) -> Response:
        """
            This is a function that will return an internal server error response.

        Args:
            title (str): The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="The server has encountered an error.",
            resp="Internal server error",
            error=True
        )
        return HCI.internal_server_error(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def unauthorized(self, title: str) -> Response:
        """
            This is a function that will return an unauthorized response.

        Args:
            title (str): The title of the called endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token provided by the user of the called endpoint

        Returns:
            Response: The response ready to be sent back to the user
        """
        body = self.build_response_body(
            title=title,
            message="You do not have permission to run this endpoint.",
            resp="Access denied",
            error=True
        )
        return HCI.unauthorized(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def user_not_found(self, title: str) -> Response:
        """
            Function that will return a user not found error.

        Args:
            title (str): The title of the endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token if present.

        Returns:
            Response: The pre-compiled response (ready to go)
        """
        body = self.build_response_body(
            title=title,
            message="The current user was not found.",
            resp="Not found",
            error=True
        )
        return HCI.not_found(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)

    def missing_variable_in_body(self, title: str) -> Response:
        """
            Function that will return a message saying that there is a missing variable in the provided body.

        Args:
            title (str): The name of the endpoint
            token (Union[str, None], optional): _description_. Defaults to None.: The token of the account.

        Returns:
            Response: The pre-compiled response (ready to go)
        """
        body = self.build_response_body(
            title=title,
            message="A variable is missing in the body of the request.",
            resp="Missing variable",
            error=True
        )
        return HCI.bad_request(body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)
