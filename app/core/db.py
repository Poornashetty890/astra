from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.device import Astra
from app.models.user import AstraUser
from app.core.config import get_settings

client = None
db = None

async def init_db():
    global client, db

    if client:
        return db

    settings = get_settings()
    client = AsyncIOMotorClient(settings.uri)
    db_name = f"{settings.service_name}_{settings.environment}"
    db = client.get_database(db_name)

    await init_beanie(database=db, document_models=[Astra, AstraUser])

    return db
