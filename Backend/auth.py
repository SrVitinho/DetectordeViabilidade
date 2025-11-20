from fastapi.responses import JSONResponse
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import  OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
from User.userBase import LoginRequest, UserBase, UserResponse, UserResponseLogin, ResponseDataLogin, UserDataLogin, UserResponseRegister
from database import SessionLocal
from models import User
from datetime import timedelta, datetime
from jose import jwt, JWTError
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
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")    
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user

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
            usuario=UserDataLogin.model_validate(user)
        )
    )
    
@router.post("/register", response_model=UserResponseRegister, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserBase, db: db_dependency):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "Email já cadastrado ou dados inválidos",
                "code": 400
            })

    if len(user_data.password.encode('utf-8')) > 72:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "A senha não pode ter mais de 72 caracteres.",
                "code": 400
            })
    
    hashed_password = bcrypt_context.hash(user_data.password)
    
    new_user = User(
        **user_data.model_dump(exclude={'password'}),
        password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponseRegister(
        status="success",
        message="Cadastro realizado com sucesso",
        data=UserResponse.model_validate(new_user)
    )