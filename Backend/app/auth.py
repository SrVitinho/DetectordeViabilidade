from fastapi.responses import JSONResponse
from typing_extensions import Annotated
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from fastapi.security import  OAuth2PasswordBearer
from User.userBase import LoginRequest, UserResponseLogin, ResponseDataLogin, UserDataLogin
from database import SessionLocal
from models import User
from datetime import timedelta, datetime
from jose import jwt
from keys import ALGORITHM, SECRET_KEY
from starlette import status


router = APIRouter(
    prefix='/api/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[SessionLocal, Depends(get_db)]

def authenticate_user(email: str, password: str, db):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": email, "id": user_id}
    expires = datetime.now(datetime.timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)

@router.post("/login", response_model=UserResponseLogin)
async def login_for_access_token(login_data: LoginRequest, db: db_dependency):
    user = authenticate_user(login_data.email, login_data.password, db)
    if not user:
        return JSONResponse(
            status_code= status.HTTP_401_UNAUTHORIZED,
            content={
                "status": "error",
                "message": "Credenciais inválidas",
                "code": 401
            })
    token = create_access_token(user.email, user.id,  timedelta(days=3))
    return UserResponseLogin(
        status="success",
        message="Login realizado com sucesso",
        data=ResponseDataLogin(
            token=token,
            usuario=UserDataLogin.model_validate()(user)
        )
    )