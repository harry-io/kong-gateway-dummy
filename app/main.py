from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Example Microservice")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DataModel(BaseModel):
    key: str
    value: Any


# In-memory storage (replace with a proper database in production)
storage: Dict[str, Any] = {}


@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/data")
async def create_data(data: DataModel):
    try:
        storage[data.key] = data.value
        logger.info(f"Data created for key: {data.key}")
        return {"status": "success", "key": data.key}
    except Exception as e:
        logger.error(f"Error creating data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/data/{key}")
async def get_data(key: str):
    try:
        if key not in storage:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key, "value": storage[key]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
