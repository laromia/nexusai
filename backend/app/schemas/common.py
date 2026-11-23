from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    application: str
    version: str
    environment: str
    timestamp: datetime