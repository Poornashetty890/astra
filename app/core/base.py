import datetime
from uuid import uuid4

import pytz
from beanie import Document
from pydantic import Field


class MongoDocument(Document):
    id: str = Field(default_factory=lambda: str(uuid4().int))
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=pytz.UTC)
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(tz=pytz.UTC)
    )
    is_deleted: bool = False

    async def save(self, *args, **kwargs):
        current_datetime = datetime.datetime.now(tz=pytz.UTC)
        if not self.created_at:
            self.created_at = current_datetime
        self.updated_at = current_datetime
        return await super(MongoDocument, self).save(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        current_datetime = datetime.datetime.now(tz=pytz.UTC)
        if not self.created_at:
            self.created_at = current_datetime
        self.is_deleted = True
        self.updated_at = current_datetime
        return await super(MongoDocument, self).save(*args, **kwargs)

    def to_json(self):
        return self.model_dump()
