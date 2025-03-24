"""
    File in charge of containing the functions that will be run in the background.
"""

from typing import Any, List, Dict, Union
from datetime import datetime
import requests
from fastapi import Response
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from ..runtime_data import RuntimeData
from .. import constants as CONST

class Tasks:
    """
    Background tasks to do
    """

    def __init__(self, runtime_data: RuntimeData, error: int = 84, success: int = 0, debug: bool = False) -> None:
        # -------------------------- Inherited values --------------------------
        self.error: int = error
        self.success: int = success
        self.debug: bool = debug
        self.runtime_data: RuntimeData = runtime_data
        # ---------------------- The visual logger class  ----------------------
        self.disp: Disp = Disp(
            TOML_CONF,
            SAVE_TO_FILE,
            FILE_NAME,
            FILE_DESCRIPTOR,
            debug=self.debug,
            logger=self.__class__.__name__
        )

    def __del__(self) -> None:
        """
            The destructor of the class
        """
        self.disp.log_info("Task sub processes are shutting down.", "__del__")
        if self.runtime_data.background_tasks_initialised is not None:
            del self.runtime_data.background_tasks_initialised
            self.runtime_data.background_tasks_initialised = None

    def inject_tasks(self) -> int:
        """
        Add the task functions to the loop.

        Returns:
            int: The overall status of the injection.
        """
        if CONST.CLEAN_VERIFICATION is True:
            self.runtime_data.background_tasks_initialised.safe_add_task(
                func=self.clean_expired_verification_nodes,
                args=None,
                trigger='interval',
                seconds=CONST.CLEAN_VERIFICATION_INTERVAL
            )
        if CONST.RENEW_OAUTH_TOKENS is True:
            self.runtime_data.background_tasks_initialised.safe_add_task(
                func=self.renew_oauths,
                args=None,
                trigger='interval',
                seconds=CONST.RENEW_OAUTH_TOKENS_INTERVAL
            )

    def clean_expired_verification_nodes(self) -> None:
        """_summary_
            Remove the nodes in the verification table that have passed their lifespan.
        """
        title = "clean_expired_verification_nodes"
        date_node = "expiration"
        current_time = datetime.now()
        self.disp.log_info(
            f"Cleaning expired lines in the {CONST.TAB_VERIFICATION} table.",
            title
        )
        current_lines = self.runtime_data.database_link.get_data_from_table(
            table=CONST.TAB_VERIFICATION,
            column="*",
            where="",
            beautify=True
        )
        if isinstance(current_lines, int) is True:
            msg = "There is no data to be cleared in "
            msg += f"{CONST.TAB_VERIFICATION} table."
            self.disp.log_warning(
                msg,
                title
            )
            return
        self.disp.log_debug(f"current lines = {current_lines}", title)
        for i in current_lines:
            if i[date_node] is not None and i[date_node] != "" and isinstance(i[date_node], str) is True:
                datetime_node = self.runtime_data.database_link.string_to_datetime(
                    i[date_node]
                )
                msg = f"Converted {i[date_node]} to a datetime instance"
                msg += f" ({datetime_node})."
                self.disp.log_debug(msg, title)
            else:
                datetime_node = i[date_node]
                self.disp.log_debug(f"Did not convert {i[date_node]}.", title)
            if datetime_node < current_time:
                self.runtime_data.database_link.remove_data_from_table(
                    table=CONST.TAB_VERIFICATION,
                    where=f"id='{i['id']}'"
                )
                self.disp.log_debug(f"Removed {i}.", title)
        self.disp.log_debug("Cleaned expired lines", title)

    def _refresh_token(self, provider_name: str, refresh_link: str) -> Union[str, None]:
        """
        The function that use the given provider name and refresh link to generate a new token for oauth authentication
        """
        title: str = "refresh_token"
        if any(word in provider_name for word in ("google")):
            retrieved_data = self.runtime_data.database_link.get_data_from_table(
                CONST.TAB_USER_OAUTH_CONNECTION,
                "*",
                f"provider_name='{provider_name}'"
            )
            msg = "Retrieved provider data:"
            msg += f"{retrieved_data}"
            self.disp.log_debug(msg, title)
            if isinstance(retrieved_data, int):
                self.disp.log_error(
                    "An error has been detected when retrieving the provider data", title
                )
                return None
            token_url: str = retrieved_data[0]["token_grabber_base_url"]
            generated_data: dict = {}
            generated_data["client_id"] = retrieved_data[0]["client_id"]
            generated_data["client_secret"] = retrieved_data[0]["client_secret"]
            generated_data["refresh_token"] = refresh_link
            generated_data["grant_type"] = "refresh_token"
            self.disp.log_debug(f"Generated data: {generated_data}", title)
            provider_response: Response = requests.post(
                token_url, data=generated_data, timeout=10
            )
            self.disp.log_debug(f"Provider response: {provider_response}", title)
            if provider_response.status_code == 200:
                token_response = provider_response.json()
                msg = "Provider response to json: "
                msg += f"{token_response}"
                self.disp.log_debug(msg, title)
                if "access_token" in token_response:
                    return token_response["access_token"]
            else:
                return None
        self.disp.log_error("The provider is not recognised", title)
        return None

    def renew_oauths(self) -> None:
        """
        Function in charge of renewing the oauth tokens that are about to expire.
        """
        title = "renew_oauths"
        self.disp.log_debug(
            "Checking for oauths that need to be renewed", title
        )
        oauth_connections: Union[List[Dict[str]], int] = self.runtime_data.database_link.get_data_from_table(
            table=CONST.TAB_ACTIVE_OAUTHS,
            column="*",
            where="",
            beautify=True
        )
        if isinstance(oauth_connections, int) or len(oauth_connections) == 0:
            return
        current_time: datetime = datetime.now()
        for oauth in oauth_connections:
            if oauth["token_lifespan"] == 0:
                self.disp.log_debug(f"Token for {oauth['id']} does not need to be renewed.", title)
                continue
            node_id: str = oauth['id']
            token_expiration: datetime = oauth["token_expiration"]
            if current_time > token_expiration:
                renew_link: str = oauth["refresh_link"]
                lifespan: int = int(oauth["token_lifespan"])
                provider: List[
                    Dict[str, Any]
                ] = self.runtime_data.database_link.get_data_from_table(
                    table=CONST.TAB_USER_OAUTH_CONNECTION,
                    column="*",
                    where=f"id='{oauth['provider_id']}'",
                    beautify=True
                )
                if isinstance(provider, int) is True:
                    self.disp.log_error(
                        f"Could not find provider name for {node_id}", title
                    )
                    continue
                new_token: Union[str, None] = self._refresh_token(
                    provider[0]['provider_name'],
                    renew_link
                )
                if new_token is None:
                    self.disp.log_debug("Refresh token failed to generate a new token.", title)
                    continue
                token_expiration: str = self.runtime_data.database_link.datetime_to_string(
                    datetime_instance=self.runtime_data.boilerplate_non_http_initialised.set_lifespan(
                        seconds=lifespan
                    ),
                    date_only=False,
                    sql_mode=True
                )
                self.disp.log_debug(
                    f"token expiration = {token_expiration}", title
                )
                if new_token != "":
                    self.runtime_data.database_link.update_data_in_table(
                        table=CONST.TAB_ACTIVE_OAUTHS,
                        data=[
                            new_token,
                            token_expiration
                        ],
                        column=[
                            "token",
                            "token_expiration"
                        ],
                        where=f"id='{node_id}'"
                    )
                    self.disp.log_debug(
                        f"token {new_token} updated for {node_id}"
                    )
                else:
                    self.disp.log_error(f"Could not renew token for {node_id}")
            else:
                self.disp.log_debug(
                    f"Token for {node_id} does not need to be renewed.", title
                )
        self.disp.log_debug("Checked for oauth that need to be renewed", title)
