"""
    File containing boilerplate functions that could be used by the server in it's endpoints_initialised for checking incoming data.
"""

from typing import Union, Dict, Any
from fastapi import Request, UploadFile
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import RuntimeData, CONST

class BoilerplateIncoming:
    """
    The boilerplates that contains every method to handle incomming data from the client
    """

    def __init__(self, runtime_data: RuntimeData, error: int = 84, success: int = 0, debug: bool = False) -> None:
        """
        The constructor of the BoilerplateIncoming class
        """
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.runtime_data_initialised: RuntimeData = runtime_data
        # ------------------------ The logging function ------------------------
        self.disp: Disp = Disp(
            TOML_CONF,
            FILE_DESCRIPTOR,
            SAVE_TO_FILE,
            FILE_NAME,
            debug=self.debug,
            logger=self.__class__.__name__
        )

    def token_correct(self, request: Request) -> bool:
        """
            This is a function that will check if the token is correct or not.
        Args:
            request (Request): The request object

        Returns:
            bool: True if the token is correct, False otherwise
        """
        title = "token_correct"
        self.disp.log_debug(
            f"request = {request}", title
        )
        token = self.get_token_if_present(request)
        self.disp.log_debug(
            f"token = {token}", title
        )
        if token is None:
            return False
        return self.runtime_data_initialised.boilerplate_non_http_initialised.is_token_correct(token)

    def _insert_login_into_database(self, user_data: dict[str, any]) -> int:
        """
            Insert the user data into the database.
        Args:
            user_data (dict[str, any]): The user data to insert into the database

        Returns:
            int: The status of the operation
        """
        title = "_insert_login_into_database"
        if len(user_data) != 2:
            self.disp.log_error(
                "The user data is not in the correct format !", title
            )
            return self.error
        self.disp.log_debug(
            f"user_data = {user_data}", title
        )
        table_columns = self.runtime_data_initialised.database_link.get_table_column_names(
            CONST.TAB_CONNECTIONS
        )
        table_columns.pop(0)
        self.disp.log_debug(
            f"table_columns = {table_columns}", title
        )
        status = self.runtime_data_initialised.database_link.insert_data_into_table(
            CONST.TAB_CONNECTIONS,
            user_data,
            table_columns
        )
        if status != self.success:
            self.disp.log_error(
                "Data not inserted successfully !", title
            )
            return self.error
        self.disp.log_debug(
            "Data inserted successfully.", title
        )
        return self.success

    def log_user_in(self, email: str = '') -> Dict[str, Any]:
        """
            Attempt to log the user in based on the provided credentials and the database.

        Args:
            email (str): The email of the account

        Returns:
            Dict[str, Any]: The response status
            {'status':Union[success, error], 'token':Union['some_token', '']}
        """
        title = "log_user_in"
        data = {'status': self.success, 'token': ''}
        self.disp.log_debug(f"e-mail = {email}", title)
        token = self.runtime_data_initialised.boilerplate_non_http_initialised.generate_token()
        usr_id = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS,
            "id",
            f"email='{email}'",
            beautify=False
        )
        if isinstance(usr_id, int):
            data['status'] = self.error
            return data
        self.disp.log_debug(f"usr_id = {usr_id}", title)
        try:
            uid = str(int(usr_id[0][0]))
            self.disp.log_debug(f"uid = {uid}", title)
        except ValueError:
            data['status'] = self.error
            return data
        usr_data = [token, uid]
        self.disp.log_debug(f"usr_data = {usr_data}", title)
        data['status'] = self._insert_login_into_database(usr_data)
        data['token'] = token
        self.disp.log_debug(f"Response data: {data}", title)
        return data

    def get_token_if_present(self, request: Request) -> Union[str, None]:
        """
            Return the token if it is present.

        Args:
            request (Request): the request header created by the endpoint caller.

        Returns:
            Union[str, None]: If the token is present, a string is returned, otherwise, it is None.
        """
        mtoken: Union[str, None] = request.get(CONST.REQUEST_TOKEN_KEY)
        mbearer: Union[str, None] = request.get(CONST.REQUEST_BEARER_KEY)
        token: Union[str, None] = request.headers.get(CONST.REQUEST_TOKEN_KEY)
        bearer: Union[str, None] = request.headers.get(
            CONST.REQUEST_BEARER_KEY
        )
        cookie_token = request.cookies.get("token")
        self.disp.log_debug(f"Cookie = {cookie_token}")
        msg = f"mtoken = {mtoken}, mbearer = {mbearer}"
        msg += f", token = {token}, bearer = {bearer}"
        self.disp.log_debug(msg, "get_token_if_present")
        if token is None and bearer is None and token is None and bearer is None and cookie_token is None:
            return None
        if cookie_token is not None:
            return cookie_token
        if mbearer is not None and mbearer.startswith('Bearer '):
            return mbearer.split(" ")[1]
        if bearer is not None and bearer.startswith('Bearer '):
            return bearer.split(" ")[1]
        if token is not None:
            return token
        return mtoken

    async def get_body(self, request: Request) -> Dict[str, Any]:
        """
            Get the body of a request, whether it's JSON or form data.
        Args:
            request (Request): The incoming request object.

        Returns:
            Dict[str, Any]: Parsed request body in dictionary format.
        """
        body: Dict[str, Any] = {}

        try:
            body = await request.json()
        except Exception:
            try:
                form = await request.form()
                body = dict(form)

                body["_files"] = {}
                for file_key, file_value in form.items():
                    if isinstance(file_value, UploadFile):
                        body["_files"][file_key] = {
                            "filename": file_value.filename,
                            "content_type": file_value.content_type,
                            "content": await file_value.read()
                        }
            except Exception as form_error:
                msg = f"Failed to parse request body: {str(form_error)}"
                body = {"error": msg}
        return body

    def log_user_out(self, token: str = "") -> Dict[str, Any]:
        """
            Attempt to log the user out based on the provided token.

        Args:
            token (str): The token of the account

        Returns:
            Dict[str, Any]: The response status
            {'status':Union[success, error], 'msg':'message'}
        """
        title = "log_user_out"
        data = {'status': self.error, 'msg': "You are not logged in !"}
        if token == "":
            data["msg"] = "No token provided !"
            return data

        login_table = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_CONNECTIONS,
            "*",
            where=f"token={token}",
            beautify=False
        )
        if isinstance(login_table, int):
            return False
        if len(login_table) != 1:
            return False
        self.disp.log_debug(f"login_table = {login_table}", title)
        status = self.runtime_data_initialised.database_link.remove_data_from_table(
            CONST.TAB_CONNECTIONS,
            f"token={token}"
        )
        if status != self.success:
            data["msg"] = "Data not removed successfully !"
            self.disp.log_error(data["msg"], title)
            return data
        data["status"] = self.success
        data["msg"] = "You have successfully logged out."
        return data
