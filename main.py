# from pymongo import MongoClient
#
#
# import asyncio
# from typing import Optional
#
# from motor.motor_asyncio import AsyncIOMotorClient
# from pydantic import BaseModel
#
# from beanie import Document, Indexed, init_beanie
#
#
#
#
#
# from fastapi import FastAPI,Depends,status,Request,Form
# from fastapi.responses import RedirectResponse,HTMLResponse
# from fastapi.security import OAuth2PasswordRequestForm
# from fastapi_login import LoginManager #Loginmanager Class
# from fastapi_login.exceptions import InvalidCredentialsException #Exception class
# from os import path
# from starlette.templating import Jinja2Templates
#
# app= FastAPI()
#
# # Beanie uses Motor async client under the hood
# # DATABASE_URL = "mongodb://localhost:27017"
# # client = AsyncIOMotorClient(
# #     DATABASE_URL, uuidRepresentation="standard"
# # )
#
# # Initialize beanie with the Product document class
# # init_beanie(database=client.LD, document_models=[User])
#
# SECRET = "secret-key"
# # To obtain a suitable secret key you can run | import os; print(os.urandom(24).hex())
# pth = path.dirname(__file__)
# templates = Jinja2Templates(directory=path.join(pth, "templates"))
#
# manager = LoginManager(SECRET,token_url="/auth/login",use_cookie=True)
# manager.cookie_name = "some-name"
#
# @manager.user_loader()
# async def load_user(username:str):
#     # # Beanie uses Motor async client under the hood
#     # DATABASE_URL = "mongodb://localhost:27017"
#     # client = motor.motor_asyncio.AsyncIOMotorClient(
#     #     DATABASE_URL, uuidRepresentation="standard"
#     # )
#     #
#     # # Initialize beanie with the Product document class
#     # await init_beanie(database=client.LD, document_models=[User])
#
#     try:
#         user = await User.find_one(User.username == username)
#         print('user get from beanie',user)
#         return user
#     except KeyError:
#         return 'user not found'
#
# @app.post("/auth/login")
# async def login(data: OAuth2PasswordRequestForm = Depends()):
#     username = data.username
#     password = data.password
#     user = await load_user(username)
#     if not user:
#         raise InvalidCredentialsException
#     elif password != user.password:
#         raise InvalidCredentialsException
#     access_token = manager.create_access_token(
#         data={"sub":username}
#     )
#     resp = RedirectResponse(url="/private",status_code=status.HTTP_302_FOUND)
#     manager.set_cookie(resp,access_token)
#     return resp
#
# @app.get("/private")
# def getPrivateendpoint(_=Depends(manager)):
#     return "You are an authentciated user"
#
# @app.get("/",response_class=HTMLResponse)
# def loginwithCreds(request:Request):
#     with open(path.join(pth, "templates/login.html")) as f:
#         return HTMLResponse(content=f.read())
#
#
# @app.get("/register",response_class=HTMLResponse)
# def register_template(request:Request):
#     with open(path.join(pth, "templates/register.html")) as f:
#         return HTMLResponse(content=f.read())
#     # username = data.username
#     # password = data.password
#     # User(username=username,password=password).create()
#
# @app.post("/auth/register")
# async def register_user(request:Request,username: str = Form(...), password: str = Form(...)):
#     # username = data.username
#     # password = data.password
#     print('going to register user',username)
#
#     new_user = User(username=username,password=password)
#     await new_user.insert()
#     # with open(path.join(pth, "templates/login.html")) as f:
#     #     return HTMLResponse(content=f.read())

import uvicorn
from server import app
if __name__ == "__main__":
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)