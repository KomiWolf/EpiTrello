"""
The file that store every constants of the server program
"""

import dotenv
import toml
from display_tty import IDISP
IDISP.logger.name = "Constants"

# Environement initialisation
dotenv.load_dotenv(".env")
ENV = dict(dotenv.dotenv_values())

# toml config file
TOML_CONF = toml.load("config.toml")

def _get_environement_variable(environement: dotenv, variable_name: str) -> str:
    """
        Get the content of an environement variable.

    Returns:
        str: the value of that variable, otherwise an exception is raised.
    """
    data = environement.get(variable_name)
    if data is None:
        raise ValueError(
            f"Variable {variable_name} not found in the environement"
        )
    return data

def _get_toml_variable(toml_conf: dict, section: str, key: str, default=None) -> any:
    """
    Get the value of a configuration variable from the TOML file.

    Args:
        toml_conf (dict): The loaded TOML configuration as a dictionary.
        section (str): The section of the TOML file to search in.
        key (str): The key within the section to fetch.
        default: The default value to return if the key is not found. Defaults to None.

    Returns:
        str: The value of the configuration variable, or the default value if the key is not found.

    Raises:
        KeyError: If the section is not found in the TOML configuration.
    """
    try:
        keys = section.split('.')
        current_section = toml_conf

        for k in keys:
            if k in current_section:
                current_section = current_section[k]
            else:
                raise KeyError(
                    f"Section '{section}' not found in TOML configuration."
                )

        if key in current_section:
            msg = f"current_section[{key}] = {current_section[key]} : "
            msg += f"{type(current_section[key])}"
            IDISP.log_debug(msg, "_get_toml_variable")
            if current_section[key] == "none":
                IDISP.log_debug(
                    "The value none has been converted to None.",
                    "_get_toml_variable"
                )
                return None
            return current_section[key]
        if default is None:
            msg = f"Key '{key}' not found in section '{section}' "
            msg += "of TOML configuration."
            raise KeyError(msg)
        return default

    except KeyError as e:
        IDISP.log_warning(f"{e}", "_get_toml_variable")
        return default

# Return value
SUCCESS = 0
ERROR = -84

# Json default keys
JSON_TITLE: str = "title"
JSON_MESSAGE: str = "msg"
JSON_ERROR: str = "error"
JSON_RESP: str = "resp"
JSON_LOGGED_IN: str = "logged in"
JSON_UID: str = "user_uid"

# Json header for the server response header
JSON_HEADER_APP_NAME: str = "EpiTrello"
JSON_HEADER_HOST: str = "0.0.0.0"
JSON_HEADER_PORT: str = "5000"
CONTENT_TYPE="JSON"

# Mail management
SENDER_ADDRESS = _get_environement_variable(ENV, "SENDER_ADDRESS")
SENDER_KEY = _get_environement_variable(ENV, "SENDER_KEY")
SENDER_HOST = _get_environement_variable(ENV, "SENDER_HOST")
SENDER_PORT = int(_get_environement_variable(ENV, "SENDER_PORT"))

# Data for the database link
DB_HOST = _get_environement_variable(ENV, "DB_HOST")
DB_PORT = _get_environement_variable(ENV, "DB_PORT")
DB_USER = _get_environement_variable(ENV, "DB_USER")
DB_PASSWORD = _get_environement_variable(ENV, "DB_PASSWORD")
DB_DATABASE = _get_environement_variable(ENV, "DB_DATABASE")

# For Path creation variables
PATH_KEY: str = "path"
ENDPOINT_KEY: str = "endpoint"
METHOD_KEY: str = "method"
ALLOWED_METHODS: list[str] = [
    "GET", "POST",
    "PUT", "PATCH",
    "DELETE", "HEAD",
    "OPTIONS"
]

# Database management
DB_HOST = _get_environement_variable(ENV, "DB_HOST")
DB_PORT = int(_get_environement_variable(ENV, "DB_PORT"))
DB_USER = _get_environement_variable(ENV, "DB_USER")
DB_PASSWORD = _get_environement_variable(ENV, "DB_PASSWORD")
DB_DATABASE = _get_environement_variable(ENV, "DB_DATABASE")

# Minio management
MINIO_HOST = _get_environement_variable(ENV, "MINIO_HOST")
MINIO_PORT = int(_get_environement_variable(ENV, "MINIO_PORT"))
MINIO_ROOT_USER = _get_environement_variable(ENV, "MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = _get_environement_variable(ENV, "MINIO_ROOT_PASSWORD")

# Server oath variables
REDIRECT_URI = _get_environement_variable(ENV, "REDIRECT_URI")

# TOML variables
# |- Server configurations
SERVER_WORKERS = _get_toml_variable(
    TOML_CONF, "Server_configuration", "workers", None
)
SERVER_LIFESPAN = _get_toml_variable(
    TOML_CONF, "Server_configuration", "lifespan", "auto"
)
SERVER_TIMEOUT_KEEP_ALIVE = _get_toml_variable(
    TOML_CONF, "Server_configuration", "timeout_keep_alive", 30
)

# |- Server configuration -> Status codes
SUCCESS = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.status_codes", "success", 0
))
ERROR = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.status_codes", "error", 84
))

# |- Server configuration -> Debug
DEBUG = _get_toml_variable(
    TOML_CONF, "Server_configuration.debug_mode", "debug", False
)

# |- Server configuration -> development
SERVER_DEV_RELOAD = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "reload", False
)
SERVER_DEV_RELOAD_DIRS = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "reload_dirs", None
)
SERVER_DEV_LOG_LEVEL = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "log_level", "info"
)
SERVER_DEV_USE_COLOURS = _get_toml_variable(
    TOML_CONF, "Server_configuration.development", "use_colours", True
)

# |- Server configuration -> production
SERVER_PROD_PROXY_HEADERS = _get_toml_variable(
    TOML_CONF, "Server_configuration.production", "proxy_headers", True
)
SERVER_PROD_FORWARDED_ALLOW_IPS = _get_toml_variable(
    TOML_CONF, "Server_configuration.production", "forwarded_allow_ips", None
)

# |- Server configuration -> database settings
DATABASE_POOL_NAME = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "pool_name", None
)
DATABASE_MAX_POOL_CONNECTIONS = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.database", "max_pool_connections", 10
))
DATABASE_RESET_POOL_NODE_CONNECTION = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "reset_pool_node_connection", True
)
DATABASE_CONNECTION_TIMEOUT = int(_get_toml_variable(
    TOML_CONF, "Server_configuration.database", "connection_timeout", 10
))
DATABASE_LOCAL_INFILE = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "local_infile", False
)
DATABASE_INIT_COMMAND = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "init_command", None
)
DATABASE_DEFAULT_FILE = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "default_file", None
)
DATABASE_SSL_KEY = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_key", None
)
DATABASE_SSL_CERT = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_cert", None
)
DATABASE_SSL_CA = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_ca", None
)
DATABASE_SSL_CIPHER = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_cipher", None
)
DATABASE_SSL_VERIFY_CERT = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl_verify_cert", False
)
DATABASE_SSL = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "ssl", None
)
DATABASE_AUTOCOMMIT = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "autocommit", False
)
DATABASE_COLLATION = _get_toml_variable(
    TOML_CONF, "Server_configuration.database", "collation", "utf8mb4_unicode_ci"
)

# |- Tasks settings
CLEAN_VERIFICATION = _get_toml_variable(
    TOML_CONF, "Tasks", "clean_verification", True
)
CLEAN_VERIFICATION_INTERVAL = _get_toml_variable(
    TOML_CONF, "Tasks", "clean_verification_interval", 300
)
RENEW_OAUTH_TOKENS = _get_toml_variable(
    TOML_CONF, "Tasks", "renew_oauth_tokens", True
)
RENEW_OAUTH_TOKENS_INTERVAL = _get_toml_variable(
    TOML_CONF, "Tasks", "renew_oauth_tokens_interval", 300
)

# For Verification value
OAUTH_STATE_EXPIRATION = 600

# Database table names
TAB_ACCOUNTS = "users"
TAB_VERIFICATION = "verification"
TAB_CONNECTIONS = "users_connections"
TAB_USER_OAUTH_CONNECTION = "oauth_providers"
TAB_ACTIVE_OAUTHS = "active_oauth"
TAB_WORKSPACES = "workspaces"
TAB_WORKSPACES_INVITATIONS = "workspaces_invitations"
TAB_WORKSPACES_MEMBERS = "workspaces_members"
TAB_NOTIFICATIONS = "notifications"
TAB_BOARDS = "boards"
TAB_BOARDS_ACTIVITIES = "boards_activities"
TAB_BOARDS_LISTS = "boards_lists"
TAB_LISTS_CARDS = "lists_cards"
TAB_CARDS_ASSIGNEES = "cards_assignees"
TAB_CARDS_LABEL = "cards_label"

# Incoming header variables
REQUEST_TOKEN_KEY = "token"
REQUEST_BEARER_KEY = "authorization"

# Get user info banned columns (filtered out columns)
USER_INFO_BANNED: list[str] = ["password"]

# Buckets (MinIO S3)
USER_PROFILE_PHOTO_BUCKET = "user-profile-photo"
WORKSPACES_PHOTO_BUCKET = "workspaces-photo"
