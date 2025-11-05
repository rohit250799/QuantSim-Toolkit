import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

def load_config(path: str = 'settings.yaml') -> dict:
    """Load config values from Yaml file"""
    with open(path, 'r') as file:
        return yaml.safe_load(file)
    

#usage test