"""
The file that contains the class that handle workspaces invitations
"""

from typing import Union, List, Dict, Any
from fastapi import Response, Request
from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .. import constants as CONST
from ..runtime_data import RuntimeData
from ..http_codes import HCI

class WorkspacesInvitations:
    """
    The class that handle workspaces invitations
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

    async def send_invitation(self, request: Request, email: str, workspace_id: str) -> Response:
        """
        The method to send an invitation to join the workspace to a user
        """
        title: str = "Send invitation"

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
        workspace_member: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title,
        )
        if isinstance(workspace_member, Response):
            return workspace_member

        # Check if the user has the right to send invitation
        if workspace_member[0]["admin"] == 0 and workspace_member[0]["invitation_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Check if the user exist
        member_to_invite: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_ACCOUNTS,
            column="*",
            where=f"email='{email}'",
        )
        if member_to_invite == self.error or not member_to_invite:
            return self.runtime_data_initialised.boilerplate_responses_initialised.user_not_found(
                title=title
            )

        # Check if the user is already in the workspace
        id_tab: str = "id"
        member_to_invite_workspace: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            column="*",
            where=[f"user_id='{member_to_invite[0][id_tab]}'", f"workspace_id='{workspace_id}'"]
        )
        if isinstance(member_to_invite_workspace, int) is False:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The user is already in the workspace.",
                resp="conflict",
                error=True
            )
            return HCI.conflict(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Check if the user has been already invited
        member_to_invite_invitation: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            column="*",
            where=[f"user_id='{member_to_invite[0][id_tab]}'", f"workspace_id='{workspace_id}'"]
        )
        if isinstance(member_to_invite_invitation, int) is False:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The user is already invited to the workspace.",
                resp="conflict",
                error=True
            )
            return HCI.conflict(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Get columns names of the workspace invitation table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_WORKSPACES_INVITATIONS
        )
        self.disp.log_debug(f"Columns: {columns}", title)
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        # Send the invitation
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            data=[str(member_to_invite[0][id_tab]), workspace_id],
            column=columns
        )
        self.disp.log_debug(f"Send invitation status: {status}", title)
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The invitation has been sent successfully.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_my_invitations(self, request: Request) -> Response:
        """
        The method to get our invitations
        """
        title: str = "Get my invitations"

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

        # Get my invitations
        my_invitations: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            column="*",
            where=f"user_id='{usr_id}'"
        )

        # Check if the workspace member was found
        if my_invitations == self.error or not my_invitations:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="You does not have invitation or it was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Get every workspaces names where the user is invited
        invitations_list: List[Dict[str, Any]] = []
        for idx, item in enumerate(my_invitations):
            workspace: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
                table=CONST.TAB_WORKSPACES,
                column="*",
                where=f"id='{item['workspace_id']}'"
            )
            self.disp.log_debug(f"workspace_name={workspace}", title)
            if workspace == self.error or not workspace:
                continue
            invitations_list.append({
                "id": my_invitations[idx]["id"],
                "name": workspace[0]["name"],
                "favicon": workspace[0]["favicon"]
            })

        # Set the response body
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=invitations_list,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def get_workspace_invitations(self, request: Request, workspace_id: str) -> Response:
        """
        The method to get every workspace invitations
        """
        title: str = "Get workspace invitations"

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

        # Get workspace invitations
        workspace_invitations: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            column="*",
            where=f"workspace_id='{workspace_id}'"
        )

        # Check if the workspace member was found
        if workspace_invitations == self.error or not workspace_invitations:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The workspace does not have invitation or it was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Get every users name invited in the workspace
        invitations_list: List[Dict[str, Any]] = []
        for _, item in enumerate(workspace_invitations):
            user: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
                table=CONST.TAB_ACCOUNTS,
                column="*",
                where=f"id='{item['user_id']}'"
            )
            if user == self.error or not user:
                continue
            invitations_list.append({
                "id": item["id"],
                "username": user[0]["username"],
                "email": user[0]["email"],
                "favicon": user[0]["favicon"]
            })

        # Set the response body
        data = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message=invitations_list,
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=data,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def accept_invitation(self, request: Request, invitation_id: str) -> Response:
        """
        The method to accept an invitation
        """
        title: str = "Accept invitation"

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

        # Get Invitation data
        invitation: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            column="*",
            where=f"id='{invitation_id}'"
        )

        # Check if the invitation was found
        if invitation == self.error or not invitation:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The invitation was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Check if the user can accept the invitation
        if (int(usr_id) != invitation[0]["user_id"]):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title
            )

        # Get columns names of the workspace invitations table
        columns: Union[List[str], int] = self.runtime_data_initialised.database_link.get_table_column_names(
            table_name=CONST.TAB_WORKSPACES_MEMBERS
        )
        self.disp.log_debug(f"Columns: {columns}", title)
        if columns == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )
        columns.pop(0)

        # Insert the user in the workspace member
        status: int = self.runtime_data_initialised.database_link.insert_data_into_table(
            table=CONST.TAB_WORKSPACES_MEMBERS,
            data=[usr_id, str(invitation[0]["workspace_id"]), "0", "0", "0", "0"],
            column=columns
        )
        if status == self.error:
            return self.runtime_data_initialised.boilerplate_responses_initialised.internal_server_error(
                title=title
            )

        # Delete the invitation
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            where=f"id='{invitation_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The invitation has been accepted.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )

    async def delete_workspace_invitation(self, request: Request, workspace_id: str, invitation_id: str) -> Response:
        """
        The method to delete a invitation from the workspace invitation
        """
        title: str = "Delete workspace invitation"

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
            title=title,
            token=token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get Invitation data
        invitation: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            column="*",
            where=f"id='{invitation_id}'"
        )

        # Check if the invitation was found
        if invitation == self.error or not invitation:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The invitation was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Get the data of the workspace member to check his right
        workspace_member: Union[List[Dict[str, Any]], Response] = self.runtime_data_initialised.boilerplate_non_http_initialised.get_workspace_member(
            user_id=usr_id,
            workspace_id=workspace_id,
            title=title,
        )
        if isinstance(workspace_member, Response):
            return workspace_member

        # Check if the user has the right to send invitation
        if workspace_member[0]["admin"] == 0 and workspace_member[0]["invitation_restriction"] == 0:
            return self.runtime_data_initialised.boilerplate_responses_initialised.insuffisant_rights(
                title=title
            )

        # Delete the invitation
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            where=f"id='{invitation_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The invitation has been deleted.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )


    async def delete_personal_invitation(self, request: Request, invitation_id: str) -> Response:
        """
        The method to delete a personal invitation
        """
        title: str = "Delete personal invitation"

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
            title=title,
            token=token
        )
        if isinstance(usr_id, Response) is True:
            return usr_id

        # Get Invitation data
        invitation: Union[List[Dict[str, Any]], int] = self.runtime_data_initialised.database_link.get_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            column="*",
            where=f"id='{invitation_id}'"
        )

        # Check if the invitation was found
        if invitation == self.error or not invitation:
            response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
                title=title,
                message="The invitation was not found.",
                resp="not found",
                error=True
            )
            return HCI.not_found(
                content=response_body,
                content_type=CONST.CONTENT_TYPE,
                headers=self.runtime_data_initialised.json_header
            )

        # Check if the user can delete the invitation
        if (int(usr_id) != invitation[0]["user_id"]):
            return self.runtime_data_initialised.boilerplate_responses_initialised.unauthorized(
                title=title
            )

        # Delete the invitation
        self.runtime_data_initialised.database_link.drop_data_from_table(
            table=CONST.TAB_WORKSPACES_INVITATIONS,
            where=f"id='{invitation_id}'"
        )

        # Set the response body
        response_body: Dict[str, Any] = self.runtime_data_initialised.boilerplate_responses_initialised.build_response_body(
            title=title,
            message="The invitation has been deleted.",
            resp="success"
        )

        # Send the response
        return HCI.success(
            content=response_body,
            content_type=CONST.CONTENT_TYPE,
            headers=self.runtime_data_initialised.json_header
        )
