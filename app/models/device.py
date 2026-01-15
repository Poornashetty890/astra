from typing import List, Optional, Dict

from pydantic import Field

from app.core.base import MongoDocument
from app.core.config import get_settings


class Astra(MongoDocument):
    device_id: str
    user_id: Optional[str] = None
    images: List[Dict] = Field(default_factory=list)
    is_linked: bool = Field(default=False)
    image_version: Optional[int] = Field(default=0)
    pending_code: Optional[str] = None
    pending_user_id: Optional[str] = None

    class Settings:
        name = f"{get_settings().service_name}_{get_settings().environment}_device"