import pandas as pd
import logging
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from src.data_loader.data_loader import DataLoader
from src.circuit_breaker import CircuitBreaker
from src.data_validator import DataValidator
from src.custom_errors import CircuitOpenStateError, EmptyRecordReturnError
from src.adapters.api_adapter import ApiAdapter
from src.analysis_module import AnalysisModule

logger = logging.getLogger("flow")

class FlowController:
    def __init__(self, data_loader: DataLoader, circuit_breaker: CircuitBreaker, data_validator: DataValidator, data_analyzer: AnalysisModule) -> None:
        self.data_loader = data_loader
        self.circuit_breaker = circuit_breaker
        self.data_validator = data_validator
        self.analysis_module = data_analyzer

    def handle_validation_test(self, ticker: str, start_date: str, end_date: str) -> str:
        """
        Acts as a diagnostic tool - by loading data from a CSV file into pandas dataframe, validates and cleans data, logs output and prepares 
        a Data Integrity repprt,
        Displays the validation log in the validation.log file

        Data integrity report calculation logic:
        score = 1.0 - (report['gaps'] * 0.05) - (report['outliers'] * 0.1) - (report['stale'] * 0.02)

        Returns: the score obtained from Data Integrity test report
        """
        format_str = '%Y-%m-%d'
        # start_date_datetime_object = datetime.strptime(start_date, format_str)
        # end_date_datetime_object = datetime.strptime(end_date, format_str)
        # unix_epoch_start_ts = int(start_date_datetime_object.timestamp())
        # unix_epoch_end_ts = int(end_date_datetime_object.timestamp())
        start_ts = int(
            datetime.strptime(start_date, format_str)
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

        end_ts = int(
            (
                datetime.strptime(end_date, format_str)
                + timedelta(days=1)
            )
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )   
        df = self.data_loader.get_historical_data(ticker, start_ts=start_ts, end_ts=end_ts)
        if df.empty:
            logger.info('Error: No data found in the DB for ticker: %s', ticker)
            raise LookupError(
                f"No price data found for {ticker} "
                f"between {start_date} and {end_date}"
            )
        price_columns = ["close"]
        clean_and_valid_data, validation_report = self.data_validator.validate_and_clean(ticker, df, price_columns=price_columns)
        validation_score = self.data_validator.calculate_quality_score(validation_report)
        validation_logs = self.data_loader.get_validation_log(ticker)

        logger.debug('The dataframe with clean and valid data is: \n%s', clean_and_valid_data)
        logger.debug('The validation logs are: \n%s', validation_logs)
        logger.debug('The validation score is: %f', validation_score)

        return f'Gaps: {validation_report['gap_number']} \n Outliers: {validation_report['outlier_number']} \n Stale data: {validation_report['stale_data_number']} \n Validation score: {validation_score}'


    def dispatch_analysis_request(self, ticker: str, benchmark: str | None, start: str, end: str) -> Dict[str, Any]:
        """
        Serves the computation purpose for price data analysis. Fetches price data for both tickers -> if data exists ->
        enters into the analysis module for computation and returns results to the terminal. In simpler terms, its job is
        to collect data from the db, ensure it is mathematically valid for comparison and feed it to the calculator
        """
        # start_unix_epoch = int(pd.Timestamp(start).timestamp())
        # end_unix_epoch = int(pd.Timestamp(end).timestamp())
        current_timestamp = datetime.now()
        current_unix_epoch_timestamp = int(current_timestamp.timestamp())
        start_unix_epoch = int(pd.Timestamp(start, tz="UTC").timestamp())
        end_unix_epoch = int((pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1)).timestamp())
        ticker_dataframe = self.data_loader.get_historical_data(ticker=ticker, start_ts=start_unix_epoch, end_ts=end_unix_epoch)

        if ticker_dataframe.empty or ticker_dataframe is None:
            logger.info('Data missing for ticker: %s. Please run download first. Raising Lookup error', ticker)
            raise LookupError('No price data found for ticker: %s', ticker)
        
        if not benchmark:
            benchmark = 'Nifty50_id.csv' 
                 
        # else:
        #     try:
        #         benchmark_dataframe = self.data_loader.get_historical_data(benchmark, start_unix_epoch, end_unix_epoch).dropna()
        #     except EmptyRecordReturnError as e:
        #         logger.debug('Benchmark Record not found in the db due to error: %s. Using Nifty50 as default', e)
        #         benchmark = 'Nifty50'
        #         benchmark_dataframe = self.data_loader.get_historical_data(ticker='NIFTY50_id.csv', start_ts=start_unix_epoch, end_ts=end_unix_epoch)
        #     else:
        #         logger.info('The non-default benchmark dataframe fetched is: \n%s', benchmark_dataframe)            

        # ticker_dataframe_close_column = ticker_dataframe['close']
        # benchmark_dataframe_close_column = benchmark_dataframe['close']

        # concatenated_closing_prices_pd_df = pd.concat([ticker_dataframe_close_column, benchmark_dataframe_close_column], axis=1, join='inner').dropna()
        # concatenated_closing_prices_pd_df.columns = ['ticker_close', 'benchmark_close']
        # if len(concatenated_closing_prices_pd_df) < 2:
        #     logger.debug('The resultant concatenated dataframe has < 2 rows, so returns cannot be calculated. Returning None')
        #     return
        # logger.debug('The concatenated closing prices dataframe looks like: \n%s', concatenated_closing_prices_pd_df)
        
        # price_columns=["ticker_close", "benchmark_close"]
        # validated_df, report = self.data_validator.validate_and_clean(ticker, concatenated_closing_prices_pd_df, price_columns=price_columns)
        # validation_score = self.data_validator.calculate_quality_score(report)
        # compute_metrics = self.analysis_module.compute_metrics(validated_df)
        benchmark_dataframe = self.data_loader.get_historical_data(benchmark, start_unix_epoch, end_unix_epoch)
        if benchmark_dataframe.empty or benchmark_dataframe is None:
            logger.info('Data missing for benchmark: %s. Raising Lookup error', benchmark)
            raise LookupError('No price data found for benchmark: %s', benchmark)

        # ------------------------------------------------------------------
        # 3. Convert DB timestamps → UTC DatetimeIndex (ONCE)
        # ------------------------------------------------------------------
        ticker_dataframe = ticker_dataframe.copy()
        benchmark_dataframe = benchmark_dataframe.copy()

        ticker_dataframe.index = pd.to_datetime(ticker_dataframe.index, unit="s", utc=True)
        benchmark_dataframe.index = pd.to_datetime(benchmark_dataframe.index, unit="s", utc=True)

        # ------------------------------------------------------------------
        # 4. Extract CLOSE prices only (vectorized, cache-friendly)
        # ------------------------------------------------------------------
        ticker_close = ticker_dataframe["close"]
        benchmark_close = benchmark_dataframe["close"]

        # ------------------------------------------------------------------
        # 5. Build a COMMON TIME GRID (lossless union)
        # ------------------------------------------------------------------
        common_index = ticker_close.index.union(benchmark_close.index)

        # ------------------------------------------------------------------
        # 6. Reindex + forward-fill (industry standard for close prices)
        # ------------------------------------------------------------------
        concatenated_df = pd.DataFrame(
        {
            "ticker_close": ticker_close.reindex(common_index).ffill(),
            "benchmark_close": benchmark_close.reindex(common_index).ffill(),
        }).dropna()

        if len(concatenated_df) < 2:
            raise ValueError("Insufficient aligned data to compute returns")

        # ------------------------------------------------------------------
        # 7. Validate (NO DB, NO LOGIC LEAK INTO ANALYSIS)
        # ------------------------------------------------------------------
        price_columns = ["ticker_close", "benchmark_close"]
        validated_df, report = self.data_validator.validate_and_clean(
            ticker=ticker,
            df=concatenated_df,
            price_columns=price_columns,
        )

        validation_score = self.data_validator.calculate_quality_score(report)
         # ------------------------------------------------------------------
        # 8. Pure math computation (final step)
        # ------------------------------------------------------------------
        metrics = self.analysis_module.compute_metrics(validated_df)

        # ------------------------------------------------------------------
        # 9. Return structured result (terminal-safe)
        # ------------------------------------------------------------------


        results_payload = {
            'timestamp': current_unix_epoch_timestamp,
            'ticker': ticker,
            'benchmark': benchmark,
            'start_date': start_unix_epoch,
            'end_date': end_unix_epoch,
            'log_returns_alpha': metrics['log_returns_alpha'],
            'beta': metrics['beta'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'ticker_volatility': metrics['ticker_annualized_volatility'],
            'benchmark_volatility': metrics['benchmark_annualized_volatility'],
            'correlation': metrics['correlation_coefficient'],
            'data_quality_score': validation_score
        }
        
        logger.debug('The results payload is: \n%s. Saving it to analysis_results table', results_payload)
        self.data_loader.save_analysis_results(results_payload)
        return results_payload

    def handle_download_request(self, ticker: str, start_date: str, end_date: str) -> None:
        """
        Transforms the user's command into a clean, validated and stored dataset. It is responsible for handling the
        db, network(API) and validator in a single sequence
        """
        self.data_loader.initialize_circuit_state(ticker)
        try:
            circuit_state = self.circuit_breaker.check_circuit_state(ticker)
        except CircuitOpenStateError as e:
            logger.debug('Insode the handle download request function body, circuit open state error has occured')
            logger.info('Since circuit is open, terminating the request and returning. Error: %s', e)
            return
        #except 
        else:
            logger.info('The circuit state from handle download request function is: %s', circuit_state)
            pd_end_date = pd.Timestamp(end_date)
            pd_start_date = pd.Timestamp(start_date)
            logger.info('The end date unix is: %s and the start date unix is: %s', pd_end_date, pd_start_date)
            
            api_adapter = ApiAdapter()
            try:
                api_call_data = api_adapter.fetch_data(ticker, pd_start_date, pd_end_date)
                logger.debug('The api call returned data in handle download request is: \n%s', api_call_data)
            except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, TimeoutError, requests.exceptions.HTTPError) as e:
                logger.debug('Inside the handle download request function, the api call has failed. Error: %s', e)
                current_timestamp = int(datetime.now().timestamp())
                self.circuit_breaker.handle_failure(ticker, current_timestamp=current_timestamp)
                return
            else:
                if api_call_data is None:
                    logger.debug(
                        "API call succeeded but returned no data for ticker %s", ticker
                    )
                    current_timestamp = int(datetime.now().timestamp())
                    self.circuit_breaker.handle_failure(
                        ticker, current_timestamp=current_timestamp
                    )
                    return
                price_columns = ['close']
                clean_dataframe, _ = self.data_validator.validate_and_clean(ticker, df=api_call_data, price_columns=price_columns)
                logger.debug('The data as param in validate and clean, as dataframe is: \n%s', api_call_data)
                self.data_loader.insert_daily_data(ticker=ticker, df=clean_dataframe)
        return


# fc = FlowController(data)
# print(fc.dispatch_analysis_request('TCS', 'NMDC', '2025-09-01', '2025-09-20'))
#problem: dispatch analysis request is called by analyze.py file ultimately which reauires the CSV file to be present to fetch data from it
# and load it into DataFrame. We can solve this by directly loading the data from the db instead of parsing it from the CSV file we downloaded.