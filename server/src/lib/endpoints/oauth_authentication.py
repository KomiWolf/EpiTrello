"""
The file that contains all the methods for the OAuth authentication
"""

import uuid
from datetime import datetime, timedelta
from typing import Union, Dict, List, Any
import requests
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class OAuthAuthentication:
    """
    The class that handle the oauth authentication
    """

    def __init__(self, runtime_data: RuntimeData, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """_summary_
            The constructor of the OAuth authentication class

        Args:
            runtime_data (RuntimeData): _description_: The initialised version of the runtime_data class.
            success (int, optional): _description_. Defaults to 0.: The status code for success.
            error (int, optional): _description_. Defaults to 84.: The status code for error.
            debug (bool, optional): _description_. Defaults to False.: The info on if to activate debug mode.
        """
        self.debug: bool = debug
        self.success: int = success
        self.error: int = error
        self.runtime_data_initialised: RuntimeData = runtime_data
        self.verification: List[Dict[str, Any]] = []
        # --------------------------- logger section ---------------------------
        self.disp: Disp = Disp(
            TOML_CONF,
            SAVE_TO_FILE,
            FILE_NAME,
            FILE_DESCRIPTOR,
            debug=self.debug,
            logger=self.__class__.__name__
        )

    def _exchange_code_for_token(self, provider: str, code: str):
        """
        Exchange the OAuth authorization code for an access token
        """
        title = "exchange_code_for_token"

        retrieved_provider = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_USER_OAUTH_CONNECTION,
            "*",
            f"provider_name='{provider}'"
        )
        if isinstance(retrieved_provider, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                "exchange_code_for_token",
                "Internal server error.",
                "Internal server error.",
                True
            )
        headers: dict = {}
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        token_url = retrieved_provider[0]["token_grabber_base_url"]

        data: dict = {}
        data["client_id"] = retrieved_provider[0]["client_id"]
        data["client_secret"] = retrieved_provider[0]["client_secret"]
        data["code"] = code
        data["redirect_uri"] = CONST.REDIRECT_URI
        data["grant_type"] = "authorization_code"
        try:
            response = requests.post(
                token_url, data=data, headers=headers, timeout=10
            )
            self.disp.log_debug(f"Exchange response = {response}", title)
            response.raise_for_status()
            token_response = response.json()
            if "error" in token_response:
                msg = "OAuth error: "
                msg += f"{token_response['error_description']}"
                self.disp.log_error(msg, title)
                return self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                    "exchange_code_for_token",
                    "Failed to get the token",
                    f"{token_response['error']}",
                    True
                )
            return token_response
        except requests.RequestException as e:
            self.disp.log_error(f"RequestException: {str(e)}", title)
            return self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                "exchange_code_for_token",
                "HTTP request failed.",
                f"{str(e)}",
                True
            )
        except ValueError:
            self.disp.log_error("Failed to parse response JSON.", title)
            return self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                "exchange_code_for_token",
                "Invalid JSON response from provider.",
                "Invalid JSON",
                True
            )

    def _get_user_info(self, provider: str, access_token: str):
        """
        Get a user information depending
        """
        title: str = "get_user_info"
        retrieved_data = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_USER_OAUTH_CONNECTION,
            "*",
            f"provider_name='{provider}'"
        )
        self.disp.log_debug(f"Retrieved oauth provider data: {retrieved_data}", title)
        if isinstance(retrieved_data, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                "get_user_info",
                "Failed to fetch the OAuth provider information.",
                "Failed to fetch the OAuth provider information.",
                True
            )
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        user_info_url = retrieved_data[0]["user_info_base_url"]
        self.disp.log_debug(f"User info headers: {headers}", title)
        self.disp.log_debug(f"User info url: {user_info_url}", title)
        response = requests.get(user_info_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                "get_user_info",
                "Failed to retrieve the user email from the provider",
                response,
                True
            )
        user_info = response.json()
        self.disp.log_debug(f"User info: {user_info}", title)
        if provider == "github":
            for _, info in enumerate(user_info):
                if info["primary"]:
                    email: dict = {}
                    email["email"] = info["email"]
                    return email
        return user_info

    def _oauth_user_logger(self, user_info: Dict, provider: str, connection_data: list) -> Response:
        """
        The function to insert or update the user information in the database
        """
        title: str = "oauth_user_logger"
        email: str = user_info["email"]
        retrieved_user = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS,
            "*",
            f"email='{email}'"
        )
        self.disp.log_debug(f"Retrieved user: {retrieved_user}", title)

        # Si l'utilisateur existe
        if isinstance(retrieved_user, int) is False:
            retrieved_provider = self.runtime_data_initialised.database_link.get_data_from_table(
                CONST.TAB_USER_OAUTH_CONNECTION,
                "*",
                f"provider_name='{provider}'"
            )
            msg = "Retrieved provider: "
            msg += f"{retrieved_provider}"
            self.disp.log_debug(msg, title)
            if isinstance(retrieved_user, int):
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
            connection_data.append(str(retrieved_user[0]["id"]))
            connection_data.append(str(retrieved_provider[0]["id"]))
            self.disp.log_debug(f"Connection data: {connection_data}", title)

            provider_id = str(retrieved_provider[0]["id"])
            user_id = str(retrieved_user[0]["id"])
            if isinstance(self.runtime_data_initialised.database_link.get_data_from_table(
                CONST.TAB_ACTIVE_OAUTHS,
                "*",
                f"provider_id='{provider_id}' AND user_id='{user_id}'"
            ), int):
                columns = self.runtime_data_initialised.database_link.get_table_column_names(
                    CONST.TAB_ACTIVE_OAUTHS)
                if isinstance(columns, int):
                    return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
                columns.pop(0)
                self.disp.log_debug(f"Columns list = {columns}", title)
                if self.runtime_data_initialised.database_link.insert_data_into_table(
                    CONST.TAB_ACTIVE_OAUTHS,
                    connection_data,
                    columns
                ) == self.error:
                    return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
            user_data = self.runtime_data_initialised.boilerplate_incoming_initialised.log_user_in(
                email
            )
            if user_data["status"] == self.error:
                return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="User successfully logged in.",
                resp="success",
                error=False
            )
            cookie_value = f"token={user_data['token']}; Secure; SameSite=None; HttpOnly; Path=/; Partitioned; Expires=Fri, 31 Dec 9999 23:59:59 GMT"
            headers = self.runtime_data_initialised.json_header
            headers["Set-Cookie"] = cookie_value
            return HCI.success(
                body,
                content_type=CONST.CONTENT_TYPE,
                headers=headers
            )

        # Si l'utilisateur n'existe pas
        columns = self.runtime_data_initialised.database_link.get_table_column_names(
            CONST.TAB_ACCOUNTS)
        if isinstance(columns, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        columns.pop(0)
        self.disp.log_debug(f"Columns list = {columns}", title)
        username: str = email.split('@')[0]
        user_data: list = []
        user_data.append(username)
        user_data.append(email)
        user_data.append(provider)
        user_data.append("NULL")
        user_data.append("")
        self.disp.log_debug(f"Data list = {user_data}", title)
        if self.runtime_data_initialised.database_link.insert_data_into_table(CONST.TAB_ACCOUNTS, user_data, columns) == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        retrieved_user = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_ACCOUNTS,
            "*",
            f"email='{email}'"
        )
        self.disp.log_debug(f"Retrieved user: {retrieved_user}", title)
        if isinstance(retrieved_user, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        retrieved_provider = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_USER_OAUTH_CONNECTION,
            "*",
            f"provider_name='{provider}'"
        )
        self.disp.log_debug(f"Retrieved provider: {retrieved_provider}", title)
        if isinstance(retrieved_user, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        connection_data.append(str(retrieved_user[0]["id"]))
        connection_data.append(str(retrieved_provider[0]["id"]))
        self.disp.log_debug(f"Connection data: {connection_data}", title)
        columns = self.runtime_data_initialised.database_link.get_table_column_names(
            CONST.TAB_ACTIVE_OAUTHS)
        if isinstance(columns, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        columns.pop(0)
        self.disp.log_debug(f"Columns list = {columns}", title)
        if self.runtime_data_initialised.database_link.insert_data_into_table(
            CONST.TAB_ACTIVE_OAUTHS,
            connection_data,
            columns
        ) == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        user_data = self.runtime_data_initialised.boilerplate_incoming_initialised.log_user_in(
            email)
        if user_data["status"] == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="User successfully logged in.",
            resp="success",
            error=False
        )
        cookie_value = f"token={user_data['token']}; Secure; SameSite=None; HttpOnly; Path=/; Partitioned; Expires=Fri, 31 Dec 9999 23:59:59 GMT"
        headers = self.runtime_data_initialised.json_header
        headers["Set-Cookie"] = cookie_value
        return HCI.success(
            body,
            content_type=CONST.CONTENT_TYPE,
            headers=headers
        )

    def _handle_token_response(self, token_response: Dict, provider: str) -> Response:
        """
        The function that handle the response given by the provider for the oauth token
        """
        title = "handle_token_response"
        data: list = []
        access_token: str = token_response["access_token"]
        # if not access_token:
        #     return self.runtime_data_initialised.boilerplate_responses_initialised.no_access_token(title)
        data.append(access_token)
        self.disp.log_debug(f"Gotten access token: {access_token}", title)
        if provider == "github":
            data.append(
                self.runtime_data_initialised.database_link.datetime_to_string(
                    datetime.now()
                )
            )
            data.append("0")
            data.append("NULL")
        else:
            expires: int = token_response["expires_in"]
            if not expires:
                body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                    title,
                    "The expiration time was not found in the provided response.",
                    "Expiration time not found.",
                    error=True
                )
                return HCI.bad_request(
                    body,
                    content_type=CONST.CONTENT_TYPE,
                    headers=self.runtime_data_initialised.json_header
                )
            current_time = datetime.now()
            new_time = current_time + timedelta(seconds=expires)
            expiration_date = self.runtime_data_initialised.database_link.datetime_to_string(
                new_time
            )
            data.append(expiration_date)
            data.append(str(expires))
            refresh_link = token_response["refresh_token"]
            if not refresh_link:
                body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                    title,
                    "The refresh link was not found in the provided response.",
                    "Refresh link not found.",
                    error=True
                )
                return HCI.bad_request(
                    body,
                    content_type=CONST.CONTENT_TYPE,
                    headers=self.runtime_data_initialised.json_header
                )
            data.append(refresh_link)
        self.disp.log_debug(f"Generated data for new oauth connexion user: {data}", title)
        user_info = self._get_user_info(provider, access_token)
        if "error" in user_info:
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title,
                user_info["error"],
                "internal error",
                error=True
            )
            return HCI.internal_server_error(
                body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )
        return self._oauth_user_logger(user_info, provider, data)

    async def oauth_callback(self, request: Request) -> Response:
        """
        Callback of the OAuth login
        """
        title = "oauth_callback"
        query_params = request.query_params
        if not query_params:
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Query parameters not provided.",
                resp="no query parameters",
                error=True
            )
            return HCI.bad_request(
                body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )
        self.disp.log_debug(f"Query params: {query_params}", title)
        code = query_params.get("code")
        self.disp.log_debug(f"Code: {code}", title)
        state = query_params.get("state")
        self.disp.log_debug(f"State: {state}", title)
        if not code or not state:
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Authorization code or state not provided.",
                resp="no code or state",
                error=True
            )
            return HCI.bad_request(
                body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )
        uuid_gotten, provider = state.split(":")
        if not uuid_gotten or not provider:
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The state is in bad format.",
                resp="bad state format",
                error=True
            )
            return HCI.bad_request(
                body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )
        self.disp.log_debug(f"Uuid retrived: {uuid_gotten}", title)
        self.disp.log_debug(f"Provider: {provider}", title)
        data = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_VERIFICATION,
            "*",
            f"definition='{uuid_gotten}'"
        )
        self.disp.log_debug(f"Data received: {data}", title)
        if isinstance(data, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        if isinstance(self.runtime_data_initialised.database_link.drop_data_from_table(
            CONST.TAB_VERIFICATION,
            f"definition='{uuid_gotten}'"
        ), int) is False:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        token_response = self._exchange_code_for_token(provider, code)
        self.disp.log_debug(f"Token response: {token_response}", title)
        if "error" in token_response:
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="Failed to get the token.",
                resp=token_response["error"],
                error=True
            )
            return HCI.bad_request(
                body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )
        return self._handle_token_response(token_response, provider)

    def _generate_oauth_authorization_url(self, provider: str) -> Union[int, str]:
        """
        Generate an OAuth authorization url depends on the given provider
        """
        title = "generate_oauth_authorization_url"
        retrived_provider = self.runtime_data_initialised.database_link.get_data_from_table(
            CONST.TAB_USER_OAUTH_CONNECTION,
            "*",
            f"provider_name='{provider}'"
        )
        self.disp.log_debug(f"Retrived provider: {retrived_provider}", title)
        if isinstance(retrived_provider, int):
            self.disp.log_error("Unknown or Unsupported OAuth provider", title)
            return self.error
        base_url = retrived_provider[0]["authorisation_base_url"]
        client_id = retrived_provider[0]["client_id"]
        scope = retrived_provider[0]["provider_scope"]
        redirect_uri = CONST.REDIRECT_URI
        state = str(uuid.uuid4())
        columns = self.runtime_data_initialised.database_link.get_table_column_names(
            CONST.TAB_VERIFICATION
        )
        self.disp.log_debug(f"Columns list: {columns}", title)
        if isinstance(columns, int):
            return self.error
        columns.pop(0)
        expiration_time = self.runtime_data_initialised.boilerplate_non_http_initialised.set_lifespan(
            CONST.OAUTH_STATE_EXPIRATION
        )
        et_str = self.runtime_data_initialised.database_link.datetime_to_string(
            expiration_time, False)
        self.disp.log_debug(f"Expiration time: {et_str}", et_str)
        data: list = []
        data.append("state")
        data.append(state)
        data.append(et_str)
        if self.runtime_data_initialised.database_link.insert_data_into_table(CONST.TAB_VERIFICATION, data, columns) == self.error:
            return self.error
        state += ":"
        state += provider
        if provider == "google":
            url = f"{base_url}?access_type=offline&client_id={client_id}&redirect_uri={redirect_uri}&prompt=consent"
        else:
            url = f"{base_url}?client_id={client_id}&redirect_uri={redirect_uri}"
        url += f"&response_type=code&scope={scope}&state={state}"
        url = url.replace(" ", "%20")
        url = url.replace(":", "%3A")
        url = url.replace("/", "%2F")
        url = url.replace("?", "%3F")
        url = url.replace("&", "%26")
        self.disp.log_debug(f"url = {url}", title)
        return url

    async def oauth_login(self, request: Request) -> Response:
        """
        Get the authorization url for the OAuth login depending on the provider
        """
        title = "oauth_login"
        request_body = await self.runtime_data_initialised.boilerplate_incoming_initialised.get_body(request)
        self.disp.log_debug(f"Request body: {request_body}", title)
        if not request_body or "provider" not in request_body:
            body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The provider is not found in the request.",
                resp="bad request",
                error=True
            )
            return HCI.bad_request(
                body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )
        provider = request_body["provider"]
        self.disp.log_debug(f"Oauth login provider: {provider}", title)
        authorization_url = self._generate_oauth_authorization_url(provider)
        self.disp.log_debug(f"Authorization url: {authorization_url}", title)
        if isinstance(authorization_url, int):
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(title)
        body = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="Authorization url successfully generated.",
            resp="success"
        )
        body["authorization_url"] = authorization_url
        return HCI.success(
            body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
