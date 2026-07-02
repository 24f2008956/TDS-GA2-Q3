from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import yaml
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def coerce(key, value):
    if key in ["port", "workers"]:
        return int(value)

    if key == "debug":
        return str(value).lower() in ["true", "1", "yes", "on"]

    return value


@app.get("/effective-config")
def effective_config(set: list[str] = Query(default=[])):
    config = DEFAULTS.copy()

    # 1. YAML (highest after defaults)
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml") as f:
            yaml_config = yaml.safe_load(f) or {}
            config.update(yaml_config)

    # 2. .env layer
    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_LOG_LEVEL"):
        config["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # 3. OS env (APP_* prefix)
    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    for env_key, cfg_key in mapping.items():
        if os.getenv(env_key) is not None:
            config[cfg_key] = coerce(cfg_key, os.getenv(env_key))

    # 4. CLI overrides (highest precedence)
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            config[key] = coerce(key, value)

    # mask secret
    config["api_key"] = "****"

    return config