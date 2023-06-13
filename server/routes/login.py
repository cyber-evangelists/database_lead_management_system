from fastapi import FastAPI,Depends,status,Request,Form
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager #Loginmanager Class
from fastapi_login.exceptions import InvalidCredentialsException #Exception class
from starlette.templating import Jinja2Templates
from os import path
from server.models.user import User
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException
from typing import List
SECRET = "secret-key"
# To obtain a suitable secret key you can run | import os; print(os.urandom(24).hex())
pth = path.dirname(__file__)
templates = Jinja2Templates(directory=path.join(pth, "templates"))

manager = LoginManager(SECRET,token_url="/auth/login",use_cookie=True)
manager.cookie_name = "some-name"

pth = path.dirname(__file__)
router = APIRouter()

@manager.user_loader()
async def load_user(username:str):
    # # Beanie uses Motor async client under the hood
    # DATABASE_URL = "mongodb://localhost:27017"
    # client = motor.motor_asyncio.AsyncIOMotorClient(
    #     DATABASE_URL, uuidRepresentation="standard"
    # )
    #
    # # Initialize beanie with the Product document class
    # await init_beanie(database=client.LD, document_models=[User])

    try:
        user = await User.find_one(User.username == username)
        print('user get from beanie',user)
        return user
    except KeyError:
        return 'user not found'


@router.get("/login")
def loginwithCreds(request:Request):
    print('check path',pth)
    with open(path.join(pth, "../../templates/login.html")) as f:
        return HTMLResponse(content=f.read())


@router.post("/auth/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password
    user = await load_user(username)
    if not user:
        raise InvalidCredentialsException
    elif password != user.password:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(
        data={"sub":username}
    )
    resp = RedirectResponse(url="/private",status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)
    return resp

@router.get("/private")
def getPrivateendpoint(_=Depends(manager)):
    return "You are an authentciated user"


@router.get("/register",response_class=HTMLResponse)
def register_template(request:Request):
    with open(path.join(pth, "../../templates/register.html")) as f:
        return HTMLResponse(content=f.read())


@router.post("/auth/register")
async def register_user(request:Request,username: str = Form(...), password: str = Form(...)):
    print('going to register user',username)
    new_user = User(username=username,password=password)
    await new_user.insert()
    with open(path.join(pth, "../../templates/login.html")) as f:
        return HTMLResponse(content=f.read())