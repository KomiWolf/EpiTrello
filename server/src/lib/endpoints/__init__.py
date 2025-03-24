"""
The file that export every endpoints class
"""

from .bonus import Bonus
from .user_authentication import UsersAuthentication
from .user_management import UserManagement
from .workspaces_management import WorkspacesManagement
from .board_management import BoardsManagement
from .workspaces_invitations import WorkspacesInvitations
from .workspaces_members import WorkspacesMembers
from .list_management import ListsManagement
from .activities_history import ActivitiesHistory
from .card_assignees import CardAssignees
from .card_management import CardManagement
from .label_management import CardsLabelManagement
from .notifications_management import Notifications
from .oauth_authentication import OAuthAuthentication


__all__ = [
    "Bonus",
    "UsersAuthentication",
    "UserManagement",
    "WorkspacesManagement",
    "BoardsManagement",
    "WorkspacesInvitations",
    "WorkspacesMembers",
    "ListsManagement",
    "ActivitiesHistory",
    "CardAssignees",
    "CardManagement",
    "CardsLabelManagement",
    "Notifications",
    "OAuthAuthentication"
]
