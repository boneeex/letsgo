from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import user_db

app = FastAPI()

class User(BaseModel):
    username: str
    password: str

@app.post("/login")
async def get_user(request=Body()):
    token = request['token'].split()[1]
    if token:
        new_token = user_db.check_jwt_token(token)
        if new_token:
            return JSONResponse({"token": new_token}, status_code=200)
    if request['username'] and request['password']:
        user = user_db.get_user(username=request['username'])
        if user['password'] == request['passwword']:
            user_db.update_last_activity(username=request['username'])
            new_token = user_db.create_jwt({user['user_id']})
            return JSONResponse({"token": new_token}, status_code=200)
        elif user:
            return JSONResponse({"error": "User already exists"}, status_code=400)
        if not user:
            user_db.update_last_activity(username=request['username'])
            user = user_db.user_register(username=request['username'], pswd=request['password'])
            token = user_db.create_jwt({"user_id": user['user_id']})
            return JSONResponse({"token": token}, status_code=200)

@app.post("/topliststreak")
async def get_toplist():
    return user_db.top_by_days_streak()

@app.post("/toplistpoints")
async def get_toplist():
    return user_db.top_by_points()

@app.post("/profile")
async def get_user(request=Body()):
    return user_db.get_user(username=request['token'])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)