from typing import Optional
from sqlalchemy.orm import Session

from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: User, user: UserUpdate) -> User:
    # 获取更新数据，包括所有字段，即使是未设置的
    update_data = user.dict(exclude_unset=True)
    print(f"更新用户ID: {db_user.id}, 更新数据: {update_data}")
    
    # 处理密码
    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    # 更新所有字段，包括is_admin和is_active    
    for field, value in update_data.items():
        print(f"  设置字段 {field} = {value}")
        setattr(db_user, field, value)
    
    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    print(f"更新后的用户: {db_user.id}, admin={db_user.is_admin}, active={db_user.is_active}")
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    # 首先尝试通过用户名查找
    user = get_user_by_username(db, username)
    
    # 如果未找到，尝试通过邮箱查找（向后兼容）
    if not user:
        user = get_user_by_email(db, username)
    
    # 如果仍未找到或密码错误，认证失败
    if not user or not verify_password(password, user.hashed_password):
        return None
        
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True 