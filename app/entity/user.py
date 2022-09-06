from pydantic import BaseModel
class User(BaseModel):
    uid:str
    password:str
    name:str
    utype:str

class UpdateUser(BaseModel):
    uid:str
    password:str
    new_name:str