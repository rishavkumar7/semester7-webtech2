from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import HTMLResponse,ORJSONResponse,JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
import sys
sys.path.insert(0,"..")
from app.entity.user import User,UpdateUser
from app.service.neo import conn
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates/")

@router.post("/auth/signup", response_class=JSONResponse)
async def signup(user:User):
    pre_query = '''
                    MATCH (u:User) WHERE u.uid = $uid RETURN u
                '''
    pre_response = conn.query(pre_query, parameters={"uid":user.uid})
    if len(pre_response) > 0:
        return JSONResponse(content={"message":"User already exists!"},status_code=400)
    query = '''
                CREATE (u:User {uid:$uid, password:$password, name:$name, utype:$utype})
                RETURN u
            '''
    conn.query(query,parameters=user.dict())
    # print(uid)
    jsonable_encoded_user = jsonable_encoder(user)
    return JSONResponse(content={"message":"User created successfully!","user":jsonable_encoded_user},status_code=201)

@router.post("/auth/login", response_class=JSONResponse)
async def login(user:User):
    query = '''
                MATCH (u:User {uid:$uid, password:$password})
                RETURN u
            '''
    response = conn.query(query,parameters={"uid":user.uid,"password":user.password})
    if len(response) == 0:
        return JSONResponse(content={"message":"Invalid credentials"})
    else:
        return JSONResponse(content={"data":"success"})

@router.post("/auth/delete-user",response_class=JSONResponse)
async def delete_user(user:User):
    pre_query = '''
                    Match (u:User) where u.uid = $uid return u
                '''
    pre_response = conn.query(pre_query, parameters={"uid":user.uid})
    if len(pre_response) == 0:
        return JSONResponse(content={"message":"User doesn't exist!"},status_code=400)
    auth_query = '''
                    MATCH (u:User {uid:$uid, password:$password}) RETURN u
                 '''
    auth_response = conn.query(auth_query, parameters={"uid":user.uid, "password":user.password})
    if len(auth_response) == 0:
        return JSONResponse(content={"message":"Invalid credentials"},status_code=400)
    query = ''' 
                Match (u:User {uid:$uid, password:$password}) DELETE u
            '''
    conn.query(query,parameters={"uid":user.uid,"password":user.password})
    return JSONResponse(content={"message":"User deleted successfully!"},status_code=200)

@router.post("/auth/update-user",response_class=JSONResponse)
async def update_user(user:UpdateUser):
    auth_query = '''
                    MATCH (u:User {uid:$uid, password:$password}) RETURN u
                 '''
    auth_response = conn.query(auth_query, parameters={"uid":user.uid, "password":user.password})
    if len(auth_response) == 0:
        return JSONResponse(content={"message":"Invalid credentials"},status_code=400)
    query = '''
                Match (u:User {uid:$uid, password:$password}) SET u.name = $new_name
            '''
    conn.query(query,parameters=user.dict())
    return JSONResponse(content={"message":"User updated successfully!"},status_code=200)