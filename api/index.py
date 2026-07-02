from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from pydantic import BaseModel
import jwt
import config

EMAIL = "24f2008956@ds.study.iitm.ac.in"

app = FastAPI()

# ✅ CORS - MUST BE FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/stats")
def stats(values: str = Query(...)):
    nums = [int(x.strip()) for x in values.split(",")]
    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-wfrhugll.apps.exam.local"

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

class TokenRequest(BaseModel):
    token: str

@app.post("/verify")
def verify_token(req: TokenRequest):
    try:
        payload = jwt.decode(
            req.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }
    except Exception:
        raise HTTPException(status_code=401, detail={"valid": False})

# ✅ Q3 - Using the hint structure
@app.get("/effective-config")
async def get_config(request: Request):
    cfg = {
        "port": config.Q3_PORT,
        "workers": config.Q3_WORKERS,
        "debug": config.Q3_DEBUG,
        "log_level": config.Q3_LOG_LEVEL,
        "api_key": "****"
    }
    
    # Process query parameters
    for k, value in request.query_params.multi_items():
        if k == "set":
            key, val = value.split("=", 1)
            if key in ["port", "workers"]:
                cfg[key] = int(val)
            elif key == "debug":
                cfg[key] = str(val).lower() in ["true", "1", "yes", "on"]
            else:
                cfg[key] = val
    
    cfg["api_key"] = "****"
    return cfg

@app.get("/debug-env")
def debug_env():
    return {
        "APP_PORT": config.Q3_PORT,
        "APP_WORKERS": config.Q3_WORKERS,
        "APP_API_KEY_SET": config.Q3_API_KEY != "default-secret-000",
    }# CORS test deployment 20260702190336
