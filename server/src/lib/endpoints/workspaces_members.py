"""
The file that contains the class that handle workspaces members
"""

from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class WorkspacesMembers:
    """
    The class that handle workspaces members
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

    async def get_workspace_members(self, request: Request, workspace_id: str) -> Response:
        """
        The method to get every members in a workspace
        """
        title: str = "Get workspace members"

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
                title=title,
            )

        # Get the workspace members
        members: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            column="*",
            where=f"workspace_id='{workspace_id}'"
        )

        # Check if the workspace member was found
        if members == self.error or not members:
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

        # Set the response body
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=members,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_workspace_specific_member(self, request: Request, workspace_id: str, user_id: str) -> Response:
        """
        The method to get a specific member in a workspace
        """
        title: str = "Get workspace specific member"

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
                title=title,
            )

        # Get the workspace member
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

        # Set the response body
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=member[0],
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def change_member_admin_value(self, request: Request, user_id: str, workspace_id: str) -> Response:
        """
        The method to change a member admin value in a workspace
        """
        title: str = "Change member admin value"

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
                title=title,
            )

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        operator: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(operator, Response):
            return operator

        # Check if the user has the right to change the admin value
        if operator[0]["admin"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Get the user value to change
        user: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(user, Response):
            return user
        self.disp.log_debug(f"user={user}", title)
        self.disp.log_debug(f"Type={type(user[0]['admin'])}", title)

        # When the user is not an admin
        if user[0]["admin"] == 0:
            self.disp.log_debug("Change to admin", title)
            return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
                table=CONST.TAB_WORKSPACES_MEMBERS,
                data=["1"],
                columns=["admin"],
                where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
                title=title,
                message="The member information has been updated."
            )

        # When the user is an admin
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            data=["0"],
            columns=["admin"],
            where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
            title=title,
            message="The member information has been updated."
        )

    async def change_member_board_creation_value(self, request: Request, user_id: str, workspace_id: str) -> Response:
        """
        The method to change a member board creation value in a workspace
        """
        title: str = "Change member board creation value"

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
                title=title,
            )

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        operator: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(operator, Response):
            return operator

        # Check if the user has the right to change the admin value
        if operator[0]["admin"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Get the user value to change
        user: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(user, Response):
            return user

        # When the user has the right to create a board
        if user[0]["board_creation_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
                table=CONST.TAB_WORKSPACES_MEMBERS,
                data=["1"],
                columns=["board_creation_restriction"],
                where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
                title=title,
                message="The member information has been updated."
            )

        # When the user does not have the right to create a board
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            data=["0"],
            columns=["board_creation_restriction"],
            where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
            title=title,
            message="The member information has been updated."
        )

    async def change_member_board_deletion_value(self, request: Request, user_id: str, workspace_id: str) -> Response:
        """
        The method to change a member board deletion value in a workspace
        """
        title: str = "Change member board deletion value"

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

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        operator: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(operator, Response):
            return operator

        # Check if the user has the right to change the admin value
        if operator[0]["admin"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Get the user value to change
        user: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(user, Response):
            return user

        # When the user has the right to delete a board
        if user[0]["board_deletion_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
                table=CONST.TAB_WORKSPACES_MEMBERS,
                data=["1"],
                columns=["board_deletion_restriction"],
                where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
                title=title,
                message="The member information has been updated."
            )

        # When the user does not have the right to deletion a board
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            data=["0"],
            columns=["board_deletion_restriction"],
            where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
            title=title,
            message="The member information has been updated."
        )

    async def change_member_invitation_value(self, request: Request, user_id: str, workspace_id: str) -> Response:
        """
        The method to change a member invitation value in a workspace
        """
        title: str = "Change member invitation value"

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

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        operator: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(operator, Response):
            return operator

        # Check if the user has the right to change the admin value
        if operator[0]["admin"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Get the user value to change
        user: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(user, Response):
            return user

        # When the user has the right to invite a user
        if user[0]["invitation_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
                table=CONST.TAB_WORKSPACES_MEMBERS,
                data=["1"],
                columns=["invitation_restriction"],
                where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
                title=title,
                message="The member information has been updated."
            )

        # When the user does not have the right to invite a user
        return self.runtime_data_initialised.boilerplate_non_http_initialised.update_table_values(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            data=["0"],
            columns=["invitation_restriction"],
            where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"],
            title=title,
            message="The member information has been updated."
        )

    async def delete_member_from_workspace(self, request: Request, user_id: str, workspace_id: str) -> Response:
        """
        The method to change a member board creation value in a workspace
        """
        title: str = "Delete member form workspace"

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

        # Get the user id by the token
        usr_id: Union[str, Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_user_id_from_token(
            title,
            token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get the data of the workspace member to check his right
        operator: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title
        )
        if isinstance(operator, Response):
            return operator

        # Check if the user has the right to remove the user value
        if usr_id != user_id and operator[0]["admin"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Delete the member
        status: int = self.runtime_data_initialised.database_link.remove_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            where=[f"user_id='{user_id}'", f"workspace_id='{workspace_id}'"]
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The member was deleted successfully.",
            resp="success",
            error=False
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
