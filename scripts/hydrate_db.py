from pathlib import Path
from scripts.seed_benchmark import seed_database

GOLDEN_SAMPLES = {
    "NIFTY50": "NIFTY50_id.csv",
    "TCS": "TCS_id.csv",
    "ITC": "ITC_id.csv",
    "RELIANCE": "RELIANCE_id.csv",
}

def hydrate_environment() -> None:
    """
    Convenience function to hydrate the database for remote environments (Codespaces/CI).
    Add all your 'Golden Sample' tickers here.
    """

    for ticker, filename in GOLDEN_SAMPLES.items():
        seed_database(ticker, filename)

    return    

if __name__ == '__main__':
    #If run directly, performing the full environmemt hydration
    hydrate_environment()
