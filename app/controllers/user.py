from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import hash_password, get_current_entity, verify_password, create_access_token
from app.models.user import AstraUser, CreateUserReq

user_controller = APIRouter()

@user_controller.post("/")
async def handler_create_user(req:CreateUserReq):
    hashed_password = hash_password(req.password)
    user =  AstraUser(
        email=req.email,
        password=hashed_password,
        mobile=req.mobile,
        username=req.username
    )
    await user.save()
    return {"data":"Success","status_code":0}

@user_controller.post("/login")
async def handler_login_restaurant(form_data:OAuth2PasswordRequestForm=Depends()):
    user= await AstraUser.find_one(AstraUser.email == form_data.username)
    if not user:
        return {"message":"User not found for the user id","status_code":404}
    if not verify_password(password=form_data.password,hashed_password=user.password):
        return {"message":"Invalid Password","status_code":400}
    token = create_access_token(data={"sub":user.user_id},expire_minutes=2400)
    return{"access_token":token,"token_type":"bearer","status_code":0 }


@user_controller.get("/me")
async def handler_get_me(curr_user:AstraUser = Depends(get_current_entity)):
    only_fields = {
        "password"
    }
    user = await AstraUser.find_one(AstraUser.user_id == curr_user.user_id)
    return {"data":user.model_dump(exclude=only_fields),"status_code":0 }