"""
The file that contains users authentication endpoint
"""

import random
from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI
from ..password_handling import PasswordHandling
from ..mail_management import MailManagement

class UsersAuthentication:
    """
    The class that contains users authentication endpoint
    """

    def __init__(self, runtime_data: RuntimeData, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """
        The constructor of the Bonus class
        """
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.runtime_data_initialised: RuntimeData = runtime_data
        self.disp: Disp = Disp(
            TOML_CONF,
            SAVE_TO_FILE,
            FILE_NAME,
            FILE_DESCRIPTOR,
            debug=self.debug,
            logger=self.__class__.__name__
        )
        self.password_handling_initialised: PasswordHandling = PasswordHandling(
            error=error,
            success=success,
            debug=debug
        )
        self.mail_management_initialised: MailManagement = MailManagement(
            error=error,
            success=success,
            debug=debug
        )
        self.verification_code: list[dict] = []

    async def post_register(self, request: Request) -> Response:
        """
        The register endpoint
        """
        title: str = "Register"

        # Get the response body
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(
            request
        )
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("email", "password")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        if request_body["email"] == "" or request_body["password"] == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)

        # Check if the user already exist
        email_str: str = "email"
        user_info: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"email='{request_body[email_str]}'"
        )
        if isinstance(user_info, int) is False:
            node = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Email already exist.",
                resp="email exists",
                error=True
            )
            return HCI.conflict(node)

        # Prepare the data to insert a new user
        hashed_password: str = self.password_handling_initialised.hash_password(
            password=request_body["password"]
        )
        username = request_body["email"].split('@')[0]
        self.disp.log_debug(f"Username = {username}", title)

        # Get the columns
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_ACCOUNTS
        )
        if isinstance(columns, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)
        self.disp.log_debug(f"Columns = {columns}", title)

        # Insert the data in the database
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_ACCOUNTS,
            data=[username, request_body["email"], hashed_password, "NULL", ""],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the user in the connexions
        data: Dict[str, Any] = self.runtime_data_initialised.boilerplate_incoming_initialised.log_user_in(
            request_body["email"]
        )
        if data["status"] == self.error:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Login failed.",
                resp="error",
                error=True
            )
            return HCI.forbidden(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Return response
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"Welcome {username}",
            resp="success",
            error=False
        )
        cookie_value = f"token={data['token']}; Secure; SameSite=None; HttpOnly; Path=/; Partitioned; Expires=Fri, 31 Dec 9999 23:59:59 GMT"
        headers = self.runtime_data_initialised.json_header
        headers["Set-Cookie"] = cookie_value
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=headers
        )

    async def post_login(self, request: Request) -> Response:
        """
            The endpoint allowing a user to log into the server.

        Returns:
            Response: The data to send back to the user as a response.
        """
        title: str = "Login"

        # Get the response body
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(
            request
        )
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("email", "password")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                title
            )
        email = request_body["email"]
        password = request_body["password"]
        if email == "" or password == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                title
            )

        # Check the informations passed in the request
        user_info: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"email='{email}'"
        )
        self.disp.log_debug(f"Retrived data: {user_info}", title)
        if isinstance(user_info, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title
            )
        if self.password_handling_initialised.check_password(password=password, password_hash=user_info[0]["password"]) is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title
            )

        # Set the user in the connexions
        data = self.runtime_data_initialised.boilerplate_incoming_initialised.log_user_in(
            email
        )
        if data["status"] == self.error:
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Login failed.",
                resp="error",
                error=True
            )
            return HCI.forbidden(content=body, content_type=CONST.CONTENT_TYPE, headers=self.runtime_data_initialised.json_header)
        name = user_info[0]["username"]

        # Return the response
        body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=f"Welcome {name}",
            resp="success",
            error=False
        )
        cookie_value = f"token={data['token']}; Secure; SameSite=None; HttpOnly; Path=/; Partitioned; Expires=Fri, 31 Dec 9999 23:59:59 GMT"
        headers = self.runtime_data_initialised.json_header
        headers["Set-Cookie"] = cookie_value
        return HCI.success(
            content=body,
            content_type=CONST.CONTENT_TYPE,
            headers=headers
        )

    async def post_send_email_verification(self, request: Request) -> Response:
        """
        Send an email verification to change the password
        """
        title: str = "Send e-mail verification"
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(
            request
        )
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or ("email") not in request_body:
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                title
            )
        email: str = request_body["email"]
        if email == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                title
            )
        data: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"email='{email}'",
            beautify=True
        )
        self.disp.log_debug(f"user query = {data}", title)
        if data == self.error or len(data) == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(
                title
            )
        code: str = str(random.randint(100000, 999999))
        has_code: bool = False
        for i, item in enumerate(self.verification_code):
            if item["email"] == email:
                has_code = True
                self.verification_code[i]["code"] = code
                break
        if has_code is False:
            new_node: Dict[str, Any] = {}
            new_node['email'] = email
            new_node['code'] = code
            self.verification_code.append(new_node)
        self.disp.log_debug(f"Verification codes: {self.verification_code}", title)
        code_style: str = "background-color: lightgray;border: 2px lightgray solid;border-radius: 6px;color: black;font-weight: bold;padding: 5px;padding-top: 5px;padding-bottom: 5px;padding-top: 0px;padding-bottom: 0px;"
        email_subject: str = "[Epitrello] Verification code"
        body: str = ""
        body += "<p>The code is: "
        body += f"<span style=\"{code_style}\">{code}</span></p>"
        self.disp.log_debug(f"e-mail body: {body}", title)
        status: int = self.mail_management_initialised.send_email(
            email,
            email_subject,
            body
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title
            )
        body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="Email send successfully.",
            resp="success",
            error=False
        )
        return HCI.success(
            content=body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def patch_reset_password(self, request: Request) -> Response:
        """
            The function in charge of resetting the user's password.
        """
        title: str = "Reset password"
        request_body: Dict[str, Any] = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or not all(key in request_body for key in ("email", "code", "password")):
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        body_email: str = request_body["email"]
        body_code: str = request_body["code"]
        body_password: str = request_body["password"]
        if body_code == "" or body_email == "" or body_password == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        has_code: bool = False
        for i, item in enumerate(self.verification_code):
            if item["email"] == body_email and item["code"] == body_code:
                has_code = True
                self.verification_code.pop(i)
                break
        if has_code is False:
            response_body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="This email has not asked to reset the password.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                response_body,
                CONST.CONTENT_TYPE,
                self.runtime_data_initialised.json_header
            )
        data: list = []
        column: list = []
        hashed_password: str = self.password_handling_initialised.hash_password(
            body_password
        )
        data.append(hashed_password)
        column.append("password")
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_ACCOUNTS,
            data=data,
            columns=column,
            where=f"email='{body_email}'",
            title=title,
            message="Password changed successfully."
        )

    async def delete_reset_code(self, email: str):
        """
        Delete the code to reset password when necessary
        """
        title: str = "Delete reset code"
        if not email or email == "":
            return self.runtime_data_initialised.boilerplate_responses_initialised.bad_request(title)
        for i, item in enumerate(self.verification_code):
            if item["email"] == email:
                self.verification_code.pop(i)
                break
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The code was deleted successfully.",
            resp="success"
        )
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
