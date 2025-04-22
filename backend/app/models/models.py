from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, DateTime, Text, Float
from sqlalchemy.orm import relationship
import datetime

from app.db.base import Base

# Many-to-many association table for materials and tags
material_tag = Table(
    "material_tag",
    Base.metadata,
    Column("material_id", Integer, ForeignKey("materials.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with materials
    materials = relationship("Material", back_populates="uploader")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    # Relationship with materials through association table
    materials = relationship("Material", secondary=material_tag, back_populates="tags")

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String, index=True, nullable=True)  # AE模板, 视频, 音乐, 照片
    file_path = Column(String, nullable=True)
    preview_path = Column(String, nullable=True)  # Preview video path for AE模板, or preview image for videos
    preview_image_path = Column(String, nullable=True)  # Preview image path for AE模板 (extracted from preview video)
    original_link = Column(String, nullable=True)  # Original source link
    source_link = Column(String, nullable=True)  # Source of the material
    resolution = Column(String, nullable=True)  # For videos, like "1920x1080"
    uploader_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    uploader = relationship("User", back_populates="materials")
    tags = relationship("Tag", secondary=material_tag, back_populates="materials")
    thumbnails = relationship("Thumbnail", back_populates="material", cascade="all, delete-orphan")

class Thumbnail(Base):
    __tablename__ = "thumbnails"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    thumb_path = Column(String)
    original_path = Column(String)
    material_id = Column(Integer, ForeignKey("materials.id"))
    
    # Relationship with material
    material = relationship("Material", back_populates="thumbnails") 