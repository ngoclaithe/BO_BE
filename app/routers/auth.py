from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..services.auth_service import create_user, authenticate_user, update_password, get_all_users_service, delete_user_service
from ..utils.auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, oauth2_scheme, add_token_to_blacklist
from datetime import timedelta
from typing import List

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  
        expires_delta=access_token_expires
    )
    return {"token": access_token, "role": user.role}  

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user = Depends(get_current_user)):
    return current_user

@router.put("/update-password", response_model=UserResponse)
def update_password_route(new_password: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_password(db, current_user.id, new_password)
    
@router.get("/users", response_model=List[UserResponse])
def get_users_route(db: Session = Depends(get_db)):  
    return get_all_users_service(db) 

@router.delete("/delete/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return delete_user_service(db, user_id)
@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    add_token_to_blacklist(token)
    return {"message": "Logout successful"}