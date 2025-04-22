from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.models import Material, Tag, Thumbnail
from app.schemas.material import MaterialCreate, MaterialUpdate, ThumbnailCreate

def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.name == name).first()

def create_tag(db: Session, name: str) -> Tag:
    db_tag = Tag(name=name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def get_or_create_tag(db: Session, name: str) -> Tag:
    """Get an existing tag or create a new one."""
    db_tag = get_tag_by_name(db, name)
    if db_tag:
        return db_tag
    return create_tag(db, name)

def get_material(db: Session, material_id: int) -> Optional[Material]:
    """Get a material by ID with uploader relationship loaded."""
    return db.query(Material).options(
        joinedload(Material.uploader),
        joinedload(Material.tags)
    ).filter(Material.id == material_id).first()

def get_materials(
    db: Session, 
    skip: int = 0, 
    limit: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    uploader_id: Optional[int] = None
) -> List[Material]:
    """Get materials with optional filtering by category, search term, and uploader."""
    query = db.query(Material).options(
        joinedload(Material.uploader),
        joinedload(Material.tags)
    )
    
    # 按分类筛选
    if category:
        query = query.filter(Material.category == category)
    
    # 按上传者筛选
    if uploader_id:
        query = query.filter(Material.uploader_id == uploader_id)
        
    # 搜索标题和标签
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Material.title.ilike(search_term),
                Material.id.in_(
                    db.query(Material.id)
                    .join(Material.tags)
                    .filter(Tag.name.ilike(search_term))
                    .subquery()
                )
            )
        )
        
    return query.order_by(Material.created_at.desc()).offset(skip).limit(limit).all()

def count_materials(
    db: Session,
    category: Optional[str] = None,
    search: Optional[str] = None,
    uploader_id: Optional[int] = None
) -> int:
    """Count materials with optional filtering by category, search term, and uploader."""
    query = db.query(Material)
    
    # 按分类筛选
    if category:
        query = query.filter(Material.category == category)
    
    # 按上传者筛选
    if uploader_id:
        query = query.filter(Material.uploader_id == uploader_id)
        
    # 搜索标题和标签
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Material.title.ilike(search_term),
                Material.id.in_(
                    db.query(Material.id)
                    .join(Material.tags)
                    .filter(Tag.name.ilike(search_term))
                    .subquery()
                )
            )
        )
        
    return query.count()

def create_material(
    db: Session, 
    material: MaterialCreate, 
    uploader_id: int,
    file_path: Optional[str] = None,
    preview_path: Optional[str] = None,
    preview_image_path: Optional[str] = None,
    resolution: Optional[str] = None,
    original_link_str: Optional[str] = None,
    source_link_str: Optional[str] = None
) -> Material:
    """Create a new material."""
    # Create material
    db_material = Material(
        title=material.title,
        category=material.category,
        file_path=file_path,
        preview_path=preview_path,
        preview_image_path=preview_image_path,
        original_link=original_link_str,
        source_link=source_link_str,
        resolution=resolution,
        uploader_id=uploader_id
    )
    
    # Add tags
    for tag_name in material.tags:
        tag = get_or_create_tag(db, tag_name)
        db_material.tags.append(tag)
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def update_material(
    db: Session, 
    db_material: Material, 
    material: MaterialUpdate
) -> Material:
    """Update an existing material."""
    update_data = material.dict(exclude_unset=True)
    
    # Handle tags separately
    if "tags" in update_data:
        tags = update_data.pop("tags")
        # Clear existing tags
        db_material.tags = []
        # Add new tags
        for tag_name in tags:
            tag = get_or_create_tag(db, tag_name)
            db_material.tags.append(tag)
    
    # Update other fields
    for field, value in update_data.items():
        setattr(db_material, field, value)
    
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def delete_material(db: Session, db_material: Material) -> None:
    """Delete a material and its related entries."""
    db.delete(db_material)
    db.commit()

def create_thumbnail(
    db: Session,
    material_id: int,
    filename: str,
    original_path: str,
    thumb_path: str
) -> Thumbnail:
    """Create a thumbnail for a material."""
    db_thumbnail = Thumbnail(
        material_id=material_id,
        filename=filename,
        original_path=original_path,
        thumb_path=thumb_path
    )
    db.add(db_thumbnail)
    db.commit()
    db.refresh(db_thumbnail)
    return db_thumbnail

def get_material_by_uploader(
    db: Session, 
    uploader_id: int, 
    skip: int = 0, 
    limit: int = 20
) -> List[Material]:
    """Get materials uploaded by a specific user."""
    return db.query(Material).filter(
        Material.uploader_id == uploader_id
    ).order_by(Material.created_at.desc()).offset(skip).limit(limit).all() 