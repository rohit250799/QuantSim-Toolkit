import logging
import sqlite3
from datetime import datetime
from sqlite3 import Connection
from typing import Any, Dict, Tuple
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from db.database import execute_query, get_prod_conn
from db.db_queries import (
    analysis_results_table_creation_query,
    circuit_breaker_states_table_creation_query,
    delete_validation_log,
    get_all_entries_of_ticker_from_validation_log_table_query,
    get_historical_data_query,
    insert_or_update_record_in_symbols_table_query,
    insert_triggered_indices_in_validation_log_query,
    list_all_existing_tables_query,
    price_data_table_creation_query,
    record_circuit_state_initialization_query,
    set_circuit_state_query,
    symbol_table_creation_query,
    system_config_table_creation_query,
    system_logs_table_creation_query,
    validation_log_table_creation_query,
    insert_record_into_analysis_results_table,
    rename_volatility_to_ticker_volatility_in_analysis_results_query,
    add_new_column_benchmark_volatility_in_analysis_results_query
)
from src.custom_errors import EmptyRecordReturnError
from src.quant_enums import Circuit_State, LogLevel

logger = logging.getLogger("db")

class DataLoader:
    """
    Provides all methods necessary to abstract all DB I/O operations, schema management(migrations)
    and data formatting(like date conversion)

    Must: hold the active SQLite connection and cursor as attributes
    """

    def __init__(self, db_conn: None | Connection = None) -> None:
        self.prod_db_connection = db_conn if db_conn is not None else get_prod_conn()
        #self._run_migrations()

    def get_all_existing_tables(self) -> Any:
        """Get the names of all the existing tables in the db"""
        conn = self.prod_db_connection
        cursor = conn.cursor()

        cursor.execute(list_all_existing_tables_query)
        tables = cursor.fetchall()

        for table in tables:
            logger.debug("Table name: %a", table[0])

        return

    def _run_migrations(self) -> None:
        """Handles one-time cleanup and schema creation"""
        conn = self.prod_db_connection
        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute(price_data_table_creation_query)
            cursor.execute(circuit_breaker_states_table_creation_query)
            cursor.execute(symbol_table_creation_query)
            cursor.execute(system_logs_table_creation_query)
            cursor.execute(validation_log_table_creation_query)
            cursor.execute(system_config_table_creation_query)
            cursor.execute(analysis_results_table_creation_query)
            cursor.execute(rename_volatility_to_ticker_volatility_in_analysis_results_query)
            cursor.execute(add_new_column_benchmark_volatility_in_analysis_results_query)
            conn.commit()
        except sqlite3.Error as e:
            logger.debug("An error occured: %s", e)
            conn.rollback()

        else:
            last_record = cursor.fetchone()
            logger.debug("Records %s inserted in the price_data table", last_record)
            self.insert_log_entry(
                level=LogLevel.INFO.value,
                source="Data loader module",
                message="Inserting records into price_data table",
            )

    def initialize_circuit_state(self, ticker: str) -> None:
        """
        Guarantees a default CLOSED entry for a new ticker
        Attempts to initialize a circuit breaker states record with CLOSED state. Does nothing if the record already exists.
        """
        initial_state = Circuit_State.CLOSED.value
        initial_failure_count = 0
        initial_cooldown_end_time = None
        initial_last_fail_time = None

        conn = self.prod_db_connection
        cursor = conn.cursor()

        cursor.execute(
            record_circuit_state_initialization_query,
            (
                ticker,
                initial_state,
                initial_failure_count,
                initial_last_fail_time,
                initial_cooldown_end_time,
            ),
        )
        # record = cursor.fetchone()
        logger.debug(
            "The current record of the ticker is: %s",
            execute_query(
                conn, "select * from circuit_breaker_states where ticker = ?", (ticker,)
            ),
        )
        return

    def _get_all_values_from_circuit_breaker_states(self, ticker: str) -> None:
        conn = self.prod_db_connection
        # self.initialize_circuit_state(ticker=ticker)
        cursor = conn.cursor()
        cursor.execute(
            "select * from circuit_breaker_states where ticker = ?", (ticker,)
        )
        all_records = cursor.fetchall()

        for record in all_records:
            logger.debug("The current record is: %s", record)

        return

    def insert_log_entry(
        self, level: str, source: str, message: str, **kwargs: Dict[str, Any]
    ) -> None:
        """Insert logs into the system_logs table for every database operation"""
        conn = self.prod_db_connection
        timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))
        unix_timestamp_value = int(timestamp.timestamp())
        level_value = level
        source_value = source
        message_value = message
        ticker_value = kwargs["ticker"] if "ticker" in kwargs else None
        api_status_code_value = (
            kwargs["api_status_code"] if "api_status_code" in kwargs else None
        )
        response_time_ms_value = (
            kwargs["response_time_ms"] if "response_time_ms" in kwargs else None
        )

        system_logs_table_record_query: str = """
            insert into system_logs(
                timestamp, level, source, message, ticker, api_status_code, response_time_ms
            ) values(
                ?, ?, ?, ?, ?, ?, ?
            )
        """

        try:
            cursor = conn.cursor()
            cursor.execute(
                system_logs_table_record_query,
                (
                    unix_timestamp_value,
                    level_value,
                    source_value,
                    message_value,
                    ticker_value,
                    api_status_code_value,
                    response_time_ms_value,
                ),
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.debug("An error occured: %s", e)
            raise ValueError(
                "Error raised in record insertion: %s. Please fix it first.", e
            )
        else:
            last_record_id = cursor.lastrowid
            cursor.execute("select * from system_logs where id = ?", (last_record_id,))
            last_record = cursor.fetchone()
            logger.info(
                "Record: %s has been successfully inserted into the db in system_logs table",
                last_record,
            )
            return

    def get_historical_data(
        self, ticker: str, start_ts: int, end_ts: int
    ) -> pd.DataFrame:
        """
        Primary data retrieval method. Queries price_data table based on the denormalized key (ticker, timestamp).
        Returns: a Pandas DataFrame.
        """
        conn = self.prod_db_connection
        historical_data_dataframe = pd.read_sql_query(
            sql=get_historical_data_query, con=conn, params=(ticker, start_ts, end_ts)
        )
        if not historical_data_dataframe.empty:
            historical_data_dataframe["timestamp"] = pd.to_datetime(
                historical_data_dataframe["timestamp"], unit="s"
            )
            historical_data_dataframe["timestamp"] = historical_data_dataframe[
                "timestamp"
            ].dt.tz_localize("Asia/Kolkata")
            historical_data_dataframe.set_index("timestamp", inplace=True)
            return historical_data_dataframe
        else:
            logger.info(
                "The sql query in get historical data function data yielded no results for [%s, %s and %s] and the dataframe returned is empty",
                ticker,
                start_ts,
                end_ts,
            )
            raise EmptyRecordReturnError(
                "No data found in the db based on your input. Please check it again"
            )

    def insert_daily_data(self, ticker: str, df: pd.DataFrame) -> None:
        """
        Primary data storage method
        Converts DataFrame dates to UTC UNIX Epoch integers. Inserts data into price_data table
        """
        conn = self.prod_db_connection
        if not isinstance(df.index, pd.DatetimeIndex):
            raise TypeError("Dateframe must be indexed by DateTimeIndex")

        # timezone normalization
        if df.index.tz is None:
            ts_index = df.index.tz_localize("UTC")
        else:
            ts_index = df.index.tz_convert("UTC")

        # Create epoch column WITHOUT destroying index
        df_to_insert = df.copy()
        # df_to_insert["timestamp"] = (ts_index.to_numpy().view("int64") // 10**9).astype("int64")
        df_to_insert["timestamp"] = (ts_index.astype("int64") // 10**9).astype("int64")

        df_to_insert["ticker"] = ticker

        df_to_insert = df_to_insert[
            ["ticker", "timestamp", "open", "high", "low", "close", "volume"]
        ]

        try:
            with conn:
                df_to_insert.to_sql(
                    name="price_data", con=conn, if_exists="append", index=False
                )

                logger.info(
                    "Inserted %d rows for %s into price_data", len(df_to_insert), ticker
                )

        except sqlite3.Error as e:
            logger.error("Database insertion failed: %s", e)
            raise ValueError("Error raised during database insertion")

        else:
            logger.info("Dataframe inserted successfully!")
            return

    def get_circuit_state(self, ticker: str) -> Any:
        """
        Reads the current API status
        Fetches the state from circuit_breaker_states and converts the stored string back into the Python CircuitState Enum before returning
        """
        if not ticker:
            raise ValueError("Ticker must not be empty")
        conn = self.prod_db_connection
        cursor = conn.cursor()
        try:
            cursor.execute(
                "select * from circuit_breaker_states where ticker = ?", (ticker,)
            )
            row = cursor.fetchone()
            logger.debug("tHe value returned from get circuit state is: %s", row[1])
            if row is None:
                raise LookupError(f"No circuit state found for ticker: {ticker}")
            # state_str = row[1]
            return row
        finally:
            cursor.close()

    def set_circuit_state(
        self,
        ticker: str,
        state: str,
        failure_count: int | None,
        last_fail_time: int | None,
        cooldown_end_time: int | None,
    ) -> None:
        """
        Updates the API status.
        Inserts/Updates the record in circuit_state using the Enum's explicit string value.
        """
        conn = self.prod_db_connection
        cursor = conn.cursor()
        cursor.execute(
            set_circuit_state_query,
            (state, failure_count, last_fail_time, cooldown_end_time),
        )
        logger.debug(
            "The state of the ticker has been changed. The current ticker record: %s",
            execute_query(
                conn, "select * from circuit_breaker_states where ticker = ?", (ticker,)
            ),
        )
        return

    def insert_validation_issue(
        self, ticker: str, date: str, issue_type: str, description: str
    ) -> None:
        """
        Logs data quality failures
        Inserts into the validation_log table, converting the IssueType Enum to its explicit string value.
        """
        conn = self.prod_db_connection
        cursor = conn.cursor()

        try:
            conn.execute(
                insert_triggered_indices_in_validation_log_query,
                (ticker, date, issue_type, description),
            )
        except sqlite3.Error as e:
            logger.debug("An error has occured: %s", e)
            raise
        else:
            logger.info(
                "Data quality failure has been successfully inserted in the validation_log table"
            )
        return

    def insert_asset_metadata(self, ticker: str, data: Dict[str, Any]) -> None:
        """
        Used to insert or update a record in the symbols table
        """
        timestamp = datetime.now(ZoneInfo("Asia/Kolkata"))
        unix_timestamp_value = int(timestamp.timestamp())
        logger.info("Inserting or updating into symbols table!")
        conn = self.prod_db_connection
        cursor = conn.cursor()
        company_name = data["company_name"] if data["company_name"] else None
        exchange = data["exchange"] if data["exchange"] else None
        sector = data["sector"] if data["sector"] else None
        currency = data["currency"] if data["currency"] else None

        cursor.execute(
            insert_or_update_record_in_symbols_table_query,
            (ticker, company_name, exchange, sector, currency, unix_timestamp_value),
        )

        inserted_or_updated_record = execute_query(
            conn=conn, query="select * from symbols where ticker = ?", params=(ticker,)
        )
        logger.debug(
            "The inserted or updated record is: %s", inserted_or_updated_record
        )

        return

    def get_validation_log(self, ticker: str) -> pd.DataFrame:
        """
        Fetches all validation logs of a specific ticker from the validation_log table
        """
        conn = self.prod_db_connection
        cursor = conn.cursor()
        all_validation_logs = pd.read_sql_query(
            sql=get_all_entries_of_ticker_from_validation_log_table_query,
            con=conn,
            params=(ticker,),
        )
        return all_validation_logs

    def delete_unresolved_validation_log(self, ticker: str) -> None:
        """
        Fixes the multiple entries for the same date problem by implementing a Pre-Validation Cleanup inside the validate_and_clean
        orchestrator. It first deletes any existing validation issues for that specific ticker that have not been resolved, before data
        validator runs any checks - like for gaps, stale data etc.
        """
        conn = self.prod_db_connection
        cursor = conn.cursor()
        cursor.execute(delete_validation_log, (ticker,))
        return

    def save_analysis_results(self, results_payload: Dict[str, int]) -> None:
        """
        Logs the Analysis results to the analysis_results table in the db

        Args: a results payload dict object containing the results of analysis
        """
        conn = self.prod_db_connection
        timestamp, ticker, benchmark, start_date, end_date, alpha, beta, sharpe_ratio, ticker_volatility, benchmark_volatility, correlation, data_quality_score = results_payload.values()
        logger.debug('The values: \n timestamp: %d, ticker: %s, benchmark: %s, start_date: %d, end_date: %d, alpha: %s, beta: %s, sharpe_ratio: %s, ticker_volatility: %s, benchmark_volatility: %s, correlation: %s, data_quality_score: %s', timestamp, ticker, benchmark, start_date, end_date, alpha, beta, sharpe_ratio, ticker_volatility, benchmark_volatility, correlation, data_quality_score)
        try:
            cursor = conn.cursor()
            with conn:
                cursor.execute(
                insert_record_into_analysis_results_table,
                (
                    timestamp,
                    ticker,
                    benchmark,
                    start_date,
                    end_date,
                    alpha,
                    beta,
                    sharpe_ratio,
                    ticker_volatility,
                    benchmark_volatility,
                    correlation,
                    data_quality_score,
                ),
            )
        except sqlite3.Error as e:
            logger.debug('An error occured: %s', e)
            raise InterruptedError('Transaction Interrupted error!')
        
        else:
            logger.info('Results payload Data successfully inserted into analysis_table.')
            last_record = cursor.fetchone()
            logger.info('record inserted in analysis_results table is: %s', last_record)
        
        return
    
my_dl = DataLoader()
#print(my_dl._get_all_values_from_circuit_breaker_states("TCS"))
