from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.schemas.user import User

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    
    class Config:
        orm_mode = True

class ThumbnailBase(BaseModel):
    filename: str

class ThumbnailCreate(ThumbnailBase):
    pass

class Thumbnail(ThumbnailBase):
    id: int
    thumb_path: str
    original_path: str
    material_id: int
    
    class Config:
        orm_mode = True

class MaterialBase(BaseModel):
    title: str
    category: Optional[str] = None
    original_link: Optional[str] = None
    source_link: Optional[str] = None

class MaterialCreate(MaterialBase):
    tags: List[str] = []

class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    original_link: Optional[str] = None
    source_link: Optional[str] = None
    tags: Optional[List[str]] = None

class MaterialInDBBase(MaterialBase):
    id: int
    file_path: Optional[str] = None
    preview_path: Optional[str] = None
    preview_image_path: Optional[str] = None
    resolution: Optional[str] = None
    uploader_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class Material(MaterialInDBBase):
    tags: List[Tag] = []
    uploader: User
    thumbnails: List[Thumbnail] = []

class MaterialSearchResults(BaseModel):
    results: List[Material]
    total: int 