"""
    This is the file in charge of storing the endpoints_initialised ready to be imported into the server class.
"""

from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .runtime_data import RuntimeData
from .endpoints import (
    Bonus,
    UsersAuthentication,
    UserManagement,
    WorkspacesManagement,
    BoardsManagement,
    WorkspacesInvitations,
    WorkspacesMembers,
    ListsManagement,
    ActivitiesHistory,
    CardAssignees,
    CardManagement,
    CardsLabelManagement,
    Notifications,
    OAuthAuthentication
)

class Endpoints:
    """
    The class that contains every endpoints of the server
    """
    def __init__(self, runtime_data: RuntimeData, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """
        The constructor of the Endpoints class
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
        # ------------------- Initialize endpoints sub-classes ------------------
        self.bonus: Bonus = Bonus(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.users_authentication: UsersAuthentication = UsersAuthentication(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.oauth_authentication: OAuthAuthentication = OAuthAuthentication(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.user_management: UserManagement = UserManagement(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.workspaces_management: WorkspacesManagement = WorkspacesManagement(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.boards_management: BoardsManagement = BoardsManagement(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.workspaces_invitations: WorkspacesInvitations = WorkspacesInvitations(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.workspaces_members: WorkspacesMembers = WorkspacesMembers(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.list_management: ListsManagement = ListsManagement(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.activities_hitory: ActivitiesHistory = ActivitiesHistory(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.card_assignees: CardAssignees = CardAssignees(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.card_management: CardManagement = CardManagement(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.card_label_management: CardsLabelManagement = CardsLabelManagement(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )
        self.notifications: Notifications = Notifications(
            runtime_data=runtime_data,
            success=success,
            error=error,
            debug=debug
        )

    def inject_routes(self) -> None:
        """
        The function to inject every routes in the uvicorn data
        """
        # Bonus routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/", self.bonus.get_hello_world, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/", self.bonus.get_hello_world, "GET"
        )

        # Users authentication routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/register", self.users_authentication.post_register, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/login", self.users_authentication.post_login, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/send_email_verification", self.users_authentication.post_send_email_verification, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/reset_password", self.users_authentication.patch_reset_password, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/reset_code/{email}", self.users_authentication.delete_reset_code, "DELETE"
        )

        # OAuth authentication routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/oauth/login", self.oauth_authentication.oauth_login, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/oauth/callback", self.oauth_authentication.oauth_callback, "POST"
        )

        # User Management routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/user", self.user_management.get_user, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/user/{user_id}", self.user_management.get_user_by_id, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/user", self.user_management.put_user, "PUT"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/user", self.user_management.patch_user, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/update_profile_photo", self.user_management.upload_profile_image_file, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/user", self.user_management.delete_user, "DELETE"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/logout", self.user_management.logout_user, "DELETE"
        )

        # Workspaces Management routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}", self.workspaces_management.get_workspace_by_id, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/my_workspaces", self.workspaces_management.get_user_workspaces, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace", self.workspaces_management.create_workspace, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}", self.workspaces_management.put_workspace, "PUT"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}", self.workspaces_management.patch_workspace, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}", self.workspaces_management.delete_workspace, "DELETE"
        )

        # Boards Management routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/boards", self.boards_management.get_workspace_boards, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}", self.boards_management.get_board_by_id, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/board", self.boards_management.create_board, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/board/{board_id}", self.boards_management.put_board, "PUT"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/board/{board_id}", self.boards_management.patch_board, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/board/{board_id}", self.boards_management.delete_board, "DELETE"
        )

        # Workspaces invitations routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/send_invitation/{email}", self.workspaces_invitations.send_invitation, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/my_invitations", self.workspaces_invitations.get_my_invitations, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/invitations", self.workspaces_invitations.get_workspace_invitations, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/accept_invitation/{invitation_id}", self.workspaces_invitations.accept_invitation, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/delete_invitation/{invitation_id}", self.workspaces_invitations.delete_workspace_invitation, "DELETE"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/delete_invitation/{invitation_id}", self.workspaces_invitations.delete_personal_invitation, "DELETE"
        )

        # Workspaces members routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/members", self.workspaces_members.get_workspace_members, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/member/{user_id}", self.workspaces_members.get_workspace_specific_member, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/member_admin/{user_id}", self.workspaces_members.change_member_admin_value, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/member_board_creation/{user_id}", self.workspaces_members.change_member_board_creation_value, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/member_board_deletion/{user_id}", self.workspaces_members.change_member_board_deletion_value, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/member_invitation/{user_id}", self.workspaces_members.change_member_invitation_value, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/workspace/{workspace_id}/delete_member/{user_id}", self.workspaces_members.delete_member_from_workspace, "DELETE"
        )

        # List management routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}/lists", self.list_management.get_lists, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}/list/{list_id}", self.list_management.get_list_by_id, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}/list", self.list_management.create_list, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/name", self.list_management.update_list_name, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/position", self.list_management.update_list_position, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}", self.list_management.delete_list, "DELETE"
        )

        # Card management routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/card/{card_id}", self.card_management.get_card_by_id, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/cards", self.card_management.get_list_cards, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/card", self.card_management.create_card, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/card/{card_id}", self.card_management.put_card, "PUT"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/card/{card_id}/position", self.card_management.update_card_position, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/card/{card_id}", self.card_management.patch_card, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/list/{list_id}/card/{card_id}", self.card_management.delete_card, "DELETE"
        )

        # Card assignees routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/assignees", self.card_assignees.get_card_assignees, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/assignee", self.card_assignees.add_assignee, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/assignee/{user_id}", self.card_assignees.delete_assignee, "DELETE"
        )

        # Card label management routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/labels", self.card_label_management.get_card_labels, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/label", self.card_label_management.add_label, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/label/{label_id}", self.card_label_management.put_label, "PUT"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/label/{label_id}", self.card_label_management.patch_label, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/card/{card_id}/label/{label_id}", self.card_label_management.delete_label, "DELETE"
        )

        # Board activities history routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}/activities_history", self.activities_hitory.get_board_activities, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}/activity", self.activities_hitory.add_activity, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}/activity/{activity_id}", self.activities_hitory.delete_activity, "DELETE"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/board/{board_id}/activities_history", self.activities_hitory.delete_activities, "DELETE"
        )

        # Notifications routes
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/my_notifications", self.notifications.get_user_notifications, "GET"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/user/{user_id}/notification", self.notifications.add_user_notification, "POST"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/notification/{notification_id}", self.notifications.set_notification_to_read, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/my_notifications", self.notifications.set_every_notifications_to_read, "PATCH"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/notification/{notification_id}", self.notifications.delete_notification, "DELETE"
        )
        self.runtime_data_initialised.paths_initialised.add_path(
            "/api/v1/my_notifications", self.notifications.delete_notifications, "DELETE"
        )
