from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from sqlalchemy.orm import Session

from models import User
from .userBase import UserResponse, UserBase, UserUpdate

from auth import bcrypt_context, get_db
        
db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get("/", response_model=List[UserResponse])
async def get_all_users(db: db_dependency, skip: int = 0, limit: int = 100):

    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: db_dependency):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Usuário não encontrado."
        )
    return user
