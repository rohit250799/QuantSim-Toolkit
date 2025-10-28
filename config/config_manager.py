import os
from dotenv import load_dotenv
from pathlib import Path

class ConfigManager:
    """
    A central configuration manager for this project
    """

    def __init__(self):
        env_path = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=env_path)

        #for environment type
        self.APP_ENV = os.getenv('APP_ENV', 'development')

        #for database settings


        #for API keys
        self.ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

        #other app configurations


        