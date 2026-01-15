import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.controllers.device import device_controller
from app.controllers.image import image_controller
from app.controllers.user import user_controller
from app.core.config import get_settings
from app.core.db import init_db
from app.core.mqtt import get_mqtt_client, mqtt_client
from app.utils.cors import add_additional_headers

app = FastAPI(title=get_settings().service_name.title())


async def start_db():
    await init_db()
    client = get_mqtt_client()
    client.publish("test/alive", "backend-started")


async def shutdown_event():
    print("Shutting down API")
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()


app.add_event_handler("startup", start_db)
app.add_event_handler("shutdown", shutdown_event)

app.include_router(user_controller, prefix="/v1/user")
app.include_router(device_controller, prefix="/v1/device")
app.include_router(image_controller, prefix="/v1/image")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        resp = add_additional_headers(request=request, resp=Response(status_code=200))
        return resp

    response = await call_next(request)
    response = add_additional_headers(request=request, resp=response)
    return response


@app.get("/healthz", include_in_schema=True)
async def health_check():
    return {
        "status": "ok",
        "env": get_settings().environment,
        "service": get_settings().service_name,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)