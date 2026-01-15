from fastapi import APIRouter, UploadFile, Depends, HTTPException
from bson import ObjectId
from app.core.auth import get_current_entity
from app.models.device import Astra
from app.models.user import AstraUser
from app.core.db import init_db
from app.core.mqtt import notify_device, convert_for_oled
from app.utils.id_utils import get_uuid_int_type

image_controller = APIRouter()

@image_controller.post("/upload")
async def upload_image(device_id: str, file: UploadFile, curr_user: AstraUser = Depends(get_current_entity)):
    db = await init_db()

    device = await Astra.find_one(Astra.device_id == device_id)
    if not device or device.user_id != curr_user.user_id:
        raise HTTPException(403, "Not your device")

    oled_bytes = convert_for_oled(file.file)
    image_data = {
        "image_id":f"I{get_uuid_int_type(12)}",
        "device_id": device_id,
        "data": oled_bytes,
        "version": device.image_version + 1
    }

    device.images.append(image_data)
    device.image_version += 1

    await device.save()

    await notify_device(device_id, device.image_version)
    return {"status": "ok"}
