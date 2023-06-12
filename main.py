# from fastapi import FastAPI
from pymongo import MongoClient
#
# app = FastAPI()
client = MongoClient('mongodb://localhost:27017/')


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
#
#
# @app.get("/checkapi")
# async def check_api():
#     return {'nothing':'check_a_pi'}
#
# @app.get("/mongo")
# def read_root():
#     db = client['LD']
#     collection = db['leadManagement']
#     data = collection.find({"name": "talha"})
#     for document in data:
#         print('check loop')
#         print(document.name)
#     # Process the data and return a response
#     return {"message": f"Hello, MongoDB!{data}"}

from fastapi import FastAPI,Depends,status,Request
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager #Loginmanager Class
from fastapi_login.exceptions import InvalidCredentialsException #Exception class
from os import path
from starlette.templating import Jinja2Templates

app= FastAPI()

SECRET = "secret-key"
# To obtain a suitable secret key you can run | import os; print(os.urandom(24).hex())
pth = path.dirname(__file__)
templates = Jinja2Templates(directory=path.join(pth, "templates"))

manager = LoginManager(SECRET,token_url="/auth/login",use_cookie=True)
manager.cookie_name = "some-name"

DB = {"username":{"password":"qwertyuiop"}} # unhashed

@manager.user_loader
def load_user(username:str):
    db = client['LD']
    collection = db['leadManagement']
    try:
        data = collection.find({"usrname": username})
        return data
    except KeyError:
        return 'user not found'

@app.post("/auth/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password
    user = load_user(username)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    access_token = manager.create_access_token(
        data={"sub":username}
    )
    resp = RedirectResponse(url="/private",status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)
    return resp

@app.get("/private")
def getPrivateendpoint(_=Depends(manager)):
    return "You are an authentciated user"

@app.get("/",response_class=HTMLResponse)
def loginwithCreds(request:Request):
    with open(path.join(pth, "templates/login.html")) as f:
        return HTMLResponse(content=f.read())