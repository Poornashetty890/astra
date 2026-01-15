from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response
from random import randint

from app.core.db import init_db
from app.core.mqtt import send_pair_code, send_device_token
from app.models.device import Astra
from app.models.user import AstraUser
from app.core.auth import get_current_entity, create_access_token

device_controller = APIRouter()


@device_controller.post("/link/request/{device_id}")
async def request_link(device_id: str, curr_user: AstraUser = Depends(get_current_entity)):
    device = await Astra.find_one(Astra.device_id == device_id)

    if not device:
        device = Astra(device_id=device_id)

    if device.is_linked:
        raise HTTPException(400, "Device already linked")

    passcode = str(randint(1000, 9999))

    device.pending_code = passcode
    device.pending_user_id = curr_user.user_id
    await device.save()

    send_pair_code(device_id,passcode)

    return {
        "status": "code_sent",
        "device_id": device_id,
        "message": "Passcode sent to device"
    }


# -----------------------------------------------------------
# Step 2: Verify passcode → final link
# -----------------------------------------------------------
@device_controller.post("/link/verify")
async def verify_link(device_id: str, code: str, curr_user: AstraUser = Depends(get_current_entity)):
    device = await Astra.find_one(Astra.device_id == device_id)

    if not device or device.pending_user_id != curr_user.user_id:
        raise HTTPException(400, "Link not initiated or wrong user")

    if device.pending_code != code:
        raise HTTPException(401, "Invalid code")

    # Link confirmed
    device.user_id = curr_user.user_id
    device.is_linked = True
    token = create_access_token(data={"sub":device.device_id,"role":"device"})
    send_device_token(device_id,token)
    device.pending_code = None
    device.pending_user_id = None
    await device.save()

    return {"status": "linked", "device_id": device_id}


@device_controller.post("/unlink")
async def unlink_device(device_id: str, curr_user: AstraUser = Depends(get_current_entity)):
    device = await Astra.find_one(Astra.device_id == device_id)
    if not device or device.user_id != curr_user.user_id:
        raise HTTPException(400, "Device not owned by user")

    device.user_id = None
    device.is_linked = False
    device.images = []
    device.device_token = None
    await device.save()

    return {"status": "unlinked", "device_id": device_id}


@device_controller.get("/mine")
async def get_my_devices(curr_user: AstraUser = Depends(get_current_entity)):
    try:
        devices =  await Astra.find(Astra.user_id == curr_user.user_id).to_list()
        return [i.model_dump(exclude={"images"}) for i in devices]
    except Exception as e:
        print("error",e)


@device_controller.get("/{device_id}/image")
async def get_latest_image(device_id: str, device:Astra = Depends(get_current_entity)):
    await init_db()
    device = await Astra.find_one(Astra.device_id == device_id)

    if not device.images:
        raise HTTPException(404, "No image stored")

    image = device.images[-1]
    return Response(content=image["data"], media_type="application/octet-stream")
