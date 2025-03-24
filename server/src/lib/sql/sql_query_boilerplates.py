"""
    File in charge of storing the functions that will interract directly with the database.
"""

from typing import List, Dict, Union, Any

import mysql
import mysql.connector
from display_tty import Disp, TOML_CONF, SAVE_TO_FILE, FILE_NAME


from . import sql_constants as SCONST
from .sql_injection import SQLInjection
from .sql_connections import SQLManageConnections
from .sql_sanitisation_functions import SQLSanitiseFunctions


class SQLQueryBoilerplates:
    """
    """

    def __init__(self, sql_pool: SQLManageConnections, success: int = 0, error: int = 84, debug: bool = False) -> None:
        """
        The class in charge of managing sql queries (it contains the required boilerplate functions).

        Args:
            sql_pool (SQLManageConnections): 
            success (int, optional): . Defaults to 0.
            error (int, optional): . Defaults to 84.
            debug (bool, optional): . Defaults to False.
        """
        # -------------------------- Inherited values --------------------------
        self.sql_pool: SQLManageConnections = sql_pool
        self.error: int = error
        self.debug: bool = debug
        self.success: int = success
        # --------------------------- logger section ---------------------------
        self.disp: Disp = Disp(
            TOML_CONF,
            SAVE_TO_FILE,
            FILE_NAME,
            debug=self.debug,
            logger=self.__class__.__name__
        )
        # ---------------------- The anty injection class ----------------------
        self.sql_injection: SQLInjection = SQLInjection(
            self.error,
            self.success,
            self.debug
        )
        # -------------------- Keyword sanitizing functions --------------------
        self.sanitize_functions: SQLSanitiseFunctions = SQLSanitiseFunctions(
            success=self.success, error=self.error, debug=self.debug
        )

    def get_table_column_names(self, table_name: str) -> Union[List[str], int]:
        """
            Get the names of the columns in a table.

        Args:
            table_name (str): 

        Returns:
            List[str]: 
        """
        title = "get_table_column_names"
        try:
            columns = self.describe_table(table_name)
            if isinstance(columns, int) is True:
                self.disp.log_error(
                    f"Failed to describe table {table_name}.",
                    title
                )
                return self.error
            data = []
            for i in columns:
                data.append(i[0])
            return data
        except RuntimeError as e:
            msg = "Error: Failed to get column names of the tables.\n"
            msg += f"\"{str(e)}\""
            self.disp.log_error(msg, "get_table_column_names")
            return self.error

    def get_table_names(self) -> Union[int, List[str]]:
        """
            Get the names of the tables in the database.

        Returns:
            List[str]: 
        """
        title = "get_table_names"
        self.disp.log_debug("Getting table names.", title)
        resp = self.sql_pool.run_and_fetch_all(query="SHOW TABLES")
        if isinstance(resp, int) is True:
            self.disp.log_error(
                "Failed to fetch the table names.",
                title
            )
            return self.error
        data = []
        for i in resp:
            data.append(i[0])
        self.disp.log_debug("Tables fetched", title)
        return data

    def describe_table(self, table: str) -> Union[int, List[Any]]:
        """
            Fetch the headers (description) of a table from the database.

        Args:
            table (str): : The name of the table to describe.

        Raises:
            RuntimeError: : If there is a critical issue with the table or the database connection.

        Returns:
            Union[int, List[Any]]: : A list containing the description of the table, or self.error if an error occurs.
        """
        title = "describe_table"
        self.disp.log_debug(f"Describing table {table}", title)
        if self.sql_injection.check_if_sql_injection(table) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        try:
            resp = self.sql_pool.run_and_fetch_all(query=f"DESCRIBE {table}")
            if isinstance(resp, int) is True:
                self.disp.log_error(
                    f"Failed to describe table  {table}", title
                )
                return self.error
            return resp
        except mysql.connector.errors.ProgrammingError as pe:
            msg = f"ProgrammingError: The table '{table}'"
            msg += "does not exist or the query failed."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from pe
        except mysql.connector.errors.IntegrityError as ie:
            msg = "IntegrityError: There was an integrity constraint "
            msg += f"issue while describing the table '{table}'."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from ie
        except mysql.connector.errors.OperationalError as oe:
            msg = "OperationalError: There was an operational error "
            msg += f"while describing the table '{table}'."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from oe
        except mysql.connector.Error as e:
            msg = "MySQL Error: An unexpected error occurred while "
            msg += f"describing the table '{table}'."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e
        except RuntimeError as e:
            msg = "A runtime error occurred during the table description process."
            self.disp.log_critical(msg, title)
            raise RuntimeError(msg) from e

    def insert_data_into_table(self, table: str, data: Union[List[List[str]], List[str]], column: Union[List[str], None] = None) -> int:
        """
        Insert data into a table.

        Args:
            table (str): 
            data (List[List[str]]): 
            column (List[str]): 

        Returns:
            int: 
        """
        title = "insert_data_into_table"
        self.disp.log_debug("Inserting data into the table.", title)
        if column is None:
            column = ""
        if self.sql_injection.check_if_injections_in_strings([table, data, column]) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error

        if column == "":
            column = self.get_table_column_names(table)

        column = self.sanitize_functions.escape_risky_column_names(column)

        column_str = ", ".join(column)
        column_length = len(column)

        if isinstance(data, List) is True and (len(data) > 0 and isinstance(data[0], List) is True):
            self.disp.log_debug("processing double array", title)
            values = ""
            max_lengths = len(data)
            for index, line in enumerate(data):
                values += self.sanitize_functions.process_sql_line(
                    line, column, column_length
                )
                if index < max_lengths - 1:
                    values += ", "
                if index == max_lengths - 1:
                    break

        elif isinstance(data, List) is True:
            self.disp.log_debug("processing single array", title)
            values = self.sanitize_functions.process_sql_line(
                data, column, column_length
            )
        else:
            self.disp.log_error(
                "data is expected to be, either of type: List[str] or List[List[str]]",
                title
            )
            return self.error
        sql_query = f"INSERT INTO {table} ({column_str}) VALUES {values}"
        self.disp.log_debug(f"sql_query = '{sql_query}'", title)
        return self.sql_pool.run_editing_command(sql_query, table, "insert")

    def get_data_from_table(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "", beautify: bool = True) -> Union[int, List[Dict[str, Any]]]:
        """
        Args:
            table (str): 
            column (Union[str, List[str]]): 
            where (Union[str, List[str]]): 

        Returns:
            Union[int, List[Dict[str, Any]]]: : Will return the data you requested, self.error otherwise
        """
        title = "get_data_from_table"
        self.disp.log_debug(f"fetching data from the table {table}", title)
        if self.sql_injection.check_if_injections_in_strings([table, column]) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error
        if isinstance(column, list) is True:
            column = self.sanitize_functions.escape_risky_column_names(column)
            column = ", ".join(column)
        sql_command = f"SELECT {column} FROM {table}"
        if isinstance(where, (str, List)) is True:
            where = self.sanitize_functions.escape_risky_column_names_where_mode(
                where
            )
        if isinstance(where, List) is True:
            where = " AND ".join(where)
        if where != "":
            sql_command += f" WHERE {where}"
        self.disp.log_debug(f"sql_query = '{sql_command}'", title)
        resp = self.sql_pool.run_and_fetch_all(query=sql_command)
        if isinstance(resp, int) is True and resp != self.success:
            self.disp.log_error(
                "Failed to fetch the data from the table.", title
            )
            return self.error
        self.disp.log_debug(f"Queried data: {resp}", title)
        if beautify is False:
            return resp
        data = self.describe_table(table)
        return self.sanitize_functions.beautify_table(data, resp)

    def get_table_size(self, table: str, column: Union[str, List[str]], where: Union[str, List[str]] = "") -> Union[int]:
        """
            Get the size of a table.

        Args:
            table (str): 
            column (Union[str, List[str]]): 
            where (Union[str, List[str]]): 

        Returns:
            int: : Return the size of the table, -1 if an error occurred.
        """
        title = "get_table_size"
        self.disp.log_debug(f"fetching data from the table {table}", title)
        if self.sql_injection.check_if_injections_in_strings([table, column]) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return SCONST.GET_TABLE_SIZE_ERROR
        if isinstance(column, list) is True:
            column = ", ".join(column)
        sql_command = f"SELECT COUNT({column}) FROM {table}"
        if isinstance(where, (str, List)) is True:
            where = self.sanitize_functions.escape_risky_column_names_where_mode(
                where
            )
        if isinstance(where, List) is True:
            where = " AND ".join(where)
        if where != "":
            sql_command += f" WHERE {where}"
        self.disp.log_debug(f"sql_query = '{sql_command}'", title)
        resp = self.sql_pool.run_and_fetch_all(query=sql_command)
        if isinstance(resp, int) is True and resp != self.success:
            self.disp.log_error(
                "Failed to fetch the data from the table.", title
            )
            return SCONST.GET_TABLE_SIZE_ERROR
        if len(resp) == 0:
            self.disp.log_error(
                "There was no data returned by the query.", title
            )
            return SCONST.GET_TABLE_SIZE_ERROR
        if isinstance(resp[0], tuple) is False:
            self.disp.log_error("The data returned is not a tuple.", title)
            return SCONST.GET_TABLE_SIZE_ERROR
        return resp[0][0]

    def update_data_in_table(self, table: str, data: List[str], column: List, where: Union[str, List[str]] = "") -> int:
        """
            Update the data contained in a table.

        Args:
            table (str): 
            data (Union[List[List[str]], List[str]]): 
            column (List): 

        Returns:
            int: 
        """
        title = "update_data_in_table"
        msg = f"Updating the data contained in the table: {table}"
        self.disp.log_debug(msg, title)
        if column is None:
            column = ""

        if self.sql_injection.check_if_injections_in_strings([table, column, data]) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error

        if column == "":
            column = self.get_table_column_names(table)

        column = self.sanitize_functions.escape_risky_column_names(column)

        if isinstance(column, str) and isinstance(data, str):
            data = [data]
            column = [column]
            column_length = len(column)

        column_length = len(column)
        self.disp.log_debug(
            f"data = {data}, column = {column}, length = {column_length}",
            title
        )

        where = self.sanitize_functions.escape_risky_column_names_where_mode(
            where
        )

        if isinstance(where, List) is True:
            where = " AND ".join(where)

        update_line = self.sanitize_functions.compile_update_line(
            data, column, column_length
        )

        sql_query = f"UPDATE {table} SET {update_line}"

        if where != "":
            sql_query += f" WHERE {where}"

        self.disp.log_debug(f"sql_query = '{sql_query}'", title)

        return self.sql_pool.run_editing_command(sql_query, table, "update")

    def remove_data_from_table(self, table: str, where: Union[str, List[str]] = "") -> int:
        """
            Remove the data from a table.
        Args:
            table (str): 
            data (List): 
            column (List): 

        Returns:
            int: 
        """
        self.disp.log_debug(
            f"Removing data from table {table}",
            "remove_data_from_table"
        )
        if self.sql_injection.check_if_sql_injection(table) is True or self.sql_injection.check_if_symbol_and_command_injection(where) is True:
            self.disp.log_error("Injection detected.", "sql")
            return self.error

        if isinstance(where, List) is True:
            where = " AND ".join(where)

        sql_query = f"DELETE FROM {table}"

        if where != "":
            sql_query += f" WHERE {where}"

        self.disp.log_debug(
            f"sql_query = '{sql_query}'",
            "remove_data_from_table"
        )

        return self.sql_pool.run_editing_command(sql_query, table, "delete")
