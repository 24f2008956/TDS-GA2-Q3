from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
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
async def get_config(request: Request):

    cfg = DEFAULTS.copy()

    # YAML
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml") as f:
            cfg.update(yaml.safe_load(f) or {})

    # .env
    if os.getenv("NUM_WORKERS"):
        cfg["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_LOG_LEVEL"):
        cfg["log_level"] = os.getenv("APP_LOG_LEVEL")

    if os.getenv("APP_API_KEY"):
        cfg["api_key"] = os.getenv("APP_API_KEY")

    # OS env
    mapping = {
        "APP_PORT": "port",
        "APP_WORKERS": "workers",
        "APP_DEBUG": "debug",
        "APP_LOG_LEVEL": "log_level",
        "APP_API_KEY": "api_key",
    }

    for k, v in mapping.items():
        if os.getenv(k) is not None:
            cfg[v] = coerce(v, os.getenv(k))

    # CLI overrides
    for k, value in request.query_params.multi_items():
        if k == "set":
            key, val = value.split("=", 1)
            cfg[key] = coerce(key, val)

    cfg["api_key"] = "****"

    return cfg

import os
port = int(os.getenv("PORT", 8000))