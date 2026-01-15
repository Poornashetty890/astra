from pydantic import Field, BaseModel, constr

from app.core.base import MongoDocument
from app.core.config import get_settings
from app.utils.id_utils import get_uuid_int_type


EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
MOBILE_REGEX = r"^[6-9]\d{9}$"
OTP_REGEX = r"^\d{6}$"
PIN_REGEX = r"^\d{6}$"

class AstraUser(MongoDocument):
    user_id: str = Field(default=f"U{get_uuid_int_type(5)}")
    username: str
    password: str
    email: constr(pattern=EMAIL_REGEX)
    mobile: constr(pattern=MOBILE_REGEX)
    password_reset_needed: bool = Field(default=False)

    class Settings:
        name = f"{get_settings().service_name}_{get_settings().environment}_users"


class CreateUserReq(BaseModel):
    username: str
    password: str
    email: constr(pattern=EMAIL_REGEX)
    mobile: constr(pattern=MOBILE_REGEX)