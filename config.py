@"
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

# Default values
Q3_PORT = 8000
Q3_WORKERS = 1
Q3_DEBUG = False
Q3_LOG_LEVEL = "info"
Q3_API_KEY = "default-secret-000"

# Load from YAML if exists
if os.path.exists("config.development.yaml"):
    with open("config.development.yaml") as f:
        yaml_config = yaml.safe_load(f)
        if yaml_config:
            Q3_PORT = yaml_config.get("port", Q3_PORT)
            Q3_WORKERS = yaml_config.get("workers", Q3_WORKERS)
            Q3_DEBUG = yaml_config.get("debug", Q3_DEBUG)
            Q3_LOG_LEVEL = yaml_config.get("log_level", Q3_LOG_LEVEL)
            Q3_API_KEY = yaml_config.get("api_key", Q3_API_KEY)

# Override from environment variables
Q3_PORT = int(os.getenv("APP_PORT", Q3_PORT))
Q3_WORKERS = int(os.getenv("APP_WORKERS", Q3_WORKERS))
Q3_DEBUG = str(os.getenv("APP_DEBUG", Q3_DEBUG)).lower() in ["true", "1", "yes", "on"]
Q3_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", Q3_LOG_LEVEL)
Q3_API_KEY = os.getenv("APP_API_KEY", Q3_API_KEY)
"@ | Out-File -FilePath config.py -Encoding UTF8