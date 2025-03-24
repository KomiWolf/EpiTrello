"""
The file that contains every data initialised for the runtime
"""

from display_tty import Disp, TOML_CONF, FILE_DESCRIPTOR, SAVE_TO_FILE, FILE_NAME
from .sql import SQL
from .bucket import Bucket
from .background_tasks import BackgroundTasks, Tasks
from . import Endpoints, ServerPaths, RuntimeData, ServerManagement, CONST
from .boilerplates import BoilerplateIncoming, BoilerplateNonHTTP, BoilerplateResponses

class Server:
    """
    The class that contains every data initialised for the runtime
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5000, success: int = 0, error: int = 84, app_name: str = "EpiTrello", debug: bool = False) -> None:
        """
            This is the class Server, a class that contains the structures used to allow the uvicorn and fastapi combo to run successfully.
        """
        # ---------------------   The inherited arguments  ---------------------
        self.host: str = host
        self.port: int = port
        self.success: int = success
        self.error: int = error
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
        # ------------------------ Shared Runtime data  ------------------------
        self.runtime_data_initialised: RuntimeData = RuntimeData(
            host=self.host,
            port=self.port,
            app_name=app_name,
            error=self.error,
            success=self.success
        )
        # ----- The classes that need to be tracked for the server to run  -----
        self.disp.log_debug("Initialising database link.", "__init__")
        self.runtime_data_initialised.database_link = SQL(
            url=CONST.DB_HOST,
            port=CONST.DB_PORT,
            username=CONST.DB_USER,
            password=CONST.DB_PASSWORD,
            db_name=CONST.DB_DATABASE,
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        self.runtime_data_initialised.bucket_link = Bucket(
            error=self.error,
            success=self.success,
            debug=self.debug
        )
        self.runtime_data_initialised.server_management_initialised = ServerManagement(
            self.runtime_data_initialised,
            error=self.error,
            success=self.success,
            debug=self.debug
        )
        self.runtime_data_initialised.paths_initialised = ServerPaths(
            self.runtime_data_initialised,
            error=self.error,
            success=self.success,
            debug=self.debug
        )
        self.runtime_data_initialised.endpoints_initialised = Endpoints(
            self.runtime_data_initialised,
            error=self.error,
            success=self.success,
            debug=self.debug
        )
        self.runtime_data_initialised.boilerplate_responses_initialised = BoilerplateResponses(
            self.runtime_data_initialised,
            debug=self.debug
        )
        self.runtime_data_initialised.boilerplate_incoming_initialised = BoilerplateIncoming(
            self.runtime_data_initialised,
            error=self.error,
            success=self.success,
            debug=self.debug
        )
        self.runtime_data_initialised.boilerplate_non_http_initialised = BoilerplateNonHTTP(
            self.runtime_data_initialised,
            error=self.error,
            success=self.success,
            debug=self.debug
        )
        self.runtime_data_initialised.background_tasks_initialised = BackgroundTasks(
            success=self.success,
            error=self.error,
            debug=self.debug
        )
        self.runtime_data_initialised.tasks_initialised = Tasks(
            self.runtime_data_initialised,
            success=self.success,
            error=self.error,
            debug=self.debug
        )

    def __del__(self) -> None:
        """
            The destructor of the class.
        """
        self.disp.log_info("The server is shutting down.", "__del__")
        self.stop_server()

    def main(self) -> int:
        """
            The main function of the server.
            This is the one in charge of starting the server.
        """
        self.runtime_data_initialised.server_management_initialised.initialise_classes()
        self.runtime_data_initialised.paths_initialised.load_default_paths_initialised()
        self.runtime_data_initialised.paths_initialised.inject_routes()
        self.runtime_data_initialised.tasks_initialised.inject_tasks()
        status = self.runtime_data_initialised.background_tasks_initialised.safe_start()
        if status != self.success:
            self.disp.log_error(
                "Error: background tasks failed to start.",
                "main"
            )
            return status
        try:
            self.runtime_data_initialised.server.run()
        except Exception as e:
            self.disp.log_error(f"Error: {e}", "main")
            return self.error
        return self.success

    def is_running(self) -> bool:
        """
            The function in charge of checking if the server is running.

        Returns:
            bool: Returns True if the server is running.
        """
        return self.runtime_data_initialised.server_management_initialised.is_server_running()

    def stop_server(self) -> None:
        """
            The function in charge of stopping the server.
        """
        title = "stop_server"
        self.disp.log_info("Stopping server", title)
        if self.runtime_data_initialised.server_management_initialised is not None:
            del self.runtime_data_initialised.server_management_initialised
            self.runtime_data_initialised.server_management_initialised = None
        if self.runtime_data_initialised.tasks_initialised is not None:
            del self.runtime_data_initialised.tasks_initialised
            self.runtime_data_initialised.tasks_initialised = None
        self.disp.log_info("Server stopped", title)
