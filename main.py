import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database import user_db
from models.user import UserBase, UserLoginRequest


app = FastAPI(root_path='/api')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup_event():
    user_db.create_table()

@app.post("/login")
async def login(
    request: UserLoginRequest | None = None
):
    try:
        if request:
            user = user_db.get_user_by_username(request.username)
            if user and user["password"] == request.password:
                user_db.update_last_activity(request.username)
                new_token = user_db.create_jwt({"user_id": user["user_id"]})
                return JSONResponse({"token": new_token}, status_code=200)
            elif not user:
                new_user = user_db.user_register(request.username, request.password)
                new_token = user_db.create_jwt({"user_id": new_user["user_id"][0]})
                user_db.update_last_activity(request.username)
                return JSONResponse({"token": new_token}, status_code=200)

        raise HTTPException(status_code=400, detail="Неверный пароль")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/topliststreak")
async def get_toplist():
    return user_db.top_by_days_streak()

@app.get("/toplistpoints")
async def get_toplist():
    return user_db.top_by_points()

@app.get("/profile")
async def get_profile(authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Неверный формат авторизации")
    token = authorization.split()[1]
    payload = user_db.jwt_token_payload(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    
    user_data = user_db.get_user_by_id(payload['user_id'])
    
    if not user_data:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return UserBase(**dict(user_data))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)