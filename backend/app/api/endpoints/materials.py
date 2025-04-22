import os
import shutil
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import HttpUrl
from sqlalchemy.orm import Session

from app import crud
from app.api.deps import get_current_active_user, get_current_user, get_db
from app.core.config import settings
from app.models.models import User, Material
from app.schemas.material import Material as MaterialSchema, MaterialCreate, MaterialSearchResults, MaterialUpdate
from app.utils.media import (
    is_allowed_file, save_upload_file, process_video,
    create_thumbnail, ALLOWED_EXTENSIONS
)

router = APIRouter()

@router.post("/", response_model=MaterialSchema)
async def create_material(
    *,
    db: Session = Depends(get_db),
    title: str = Form(...),
    category: str = Form(None),
    tags: str = Form(""),
    original_link: Optional[str] = Form(None),
    source_link: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    preview_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new material.
    """
    try:
        print(f"开始处理上传请求: 类别={category}, 标题={title}, 文件={file.filename if file else 'None'}, 预览文件={preview_file.filename if preview_file else 'None'}")
        
        # 检查标题是否存在
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )
        
        # 其他字段变为可选，不再强制验证
        # 如果提供了category，仍然检查它的有效性
        if category and category not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {list(ALLOWED_EXTENSIONS.keys())}"
            )
        
        # 如果提供了文件，并且提供了分类，则检查文件类型
        relative_file_path = None
        if file and category:
            # Validate file extension
            if not is_allowed_file(category, file.filename):
                print(f"文件类型验证失败: 类别={category}, 文件={file.filename}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid file extension for category {category}. Allowed extensions: {ALLOWED_EXTENSIONS[category]}"
                )
            
            # Save main file
            try:
                file_path, relative_file_path = await save_upload_file(file, category)
                print(f"主文件保存成功: 路径={file_path}, 相对路径={relative_file_path}")
            except Exception as e:
                print(f"保存主文件失败: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save the main file: {str(e)}"
                )
        
        # Process files based on category
        preview_path = None
        preview_image_path = None
        resolution = None
        
        # 只有在提供了文件和类别的情况下才处理特定类别的文件
        if file and category:
            if category == "视频":
                # Process video: extract resolution and create preview image
                try:
                    resolution, preview_path = await process_video(file_path)
                    print(f"视频处理成功: 分辨率={resolution}, 预览路径={preview_path}")
                except Exception as e:
                    print(f"Error processing video: {e}")
                    # 如果处理视频失败，仍然可以继续，只是没有预览图
                    resolution = None
                    preview_path = None
            
            elif category == "AE模板" and preview_file:
                # For AE template, save the preview video
                try:
                    print(f"AE模板: 处理预览视频 {preview_file.filename}")
                    
                    # 验证预览视频文件格式，但不再强制必须有预览视频
                    if is_allowed_file("视频", preview_file.filename):
                        # 保存预览视频文件
                        try:
                            preview_file_path, preview_video_path = await save_upload_file(preview_file, "AE模板/previews")
                            print(f"预览视频保存成功: 路径={preview_file_path}, 相对路径={preview_video_path}")
                        except Exception as e:
                            print(f"保存预览视频失败: {str(e)}")
                            raise HTTPException(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Failed to save the preview video: {str(e)}"
                            )
                        
                        # 为预览视频生成预览图片
                        preview_image_path = None
                        try:
                            # 创建预览图片的存储路径
                            preview_img_dir = os.path.join(settings.MEDIA_DIR, "AE模板/previews/images")
                            os.makedirs(preview_img_dir, exist_ok=True)
                            
                            # 提取视频的第一帧作为预览图片
                            temp_resolution, preview_image_relative_path = await process_video(
                                preview_file_path, 
                                custom_preview_dir=preview_img_dir,
                                custom_preview_name=f"thumb_{os.path.basename(preview_file_path).split('.')[0]}.jpg"
                            )
                            
                            # 使用视频路径作为预览路径，图片路径保存为预览图路径
                            preview_path = preview_video_path
                            preview_image_path = preview_image_relative_path
                            print(f"预览图片生成成功: 路径={preview_image_path}")
                        except Exception as e:
                            print(f"提取预览帧失败: {str(e)}")
                            # 如果提取预览图片失败，仍然使用视频作为预览
                            preview_path = preview_video_path
                            preview_image_path = None
                    else:
                        print(f"预览视频格式无效: {preview_file.filename}")
                except HTTPException:
                    raise
                except Exception as e:
                    print(f"处理AE模板失败: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to process AE template: {str(e)}"
                    )
            
            elif category == "音乐" and preview_file:
                # For music, optionally save a cover image
                if is_allowed_file("照片", preview_file.filename):
                    _, preview_path = await save_upload_file(preview_file, "音乐/covers")
        
        # Convert tags string to list
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        # Create material object
        material_in = MaterialCreate(
            title=title,
            category=category or "",  # 如果没有提供类别，使用空字符串
            original_link=original_link,
            source_link=source_link,
            tags=tag_list
        )
        
        # 将URL对象转换为字符串，如果存在的话
        original_link_str = original_link if original_link else None
        source_link_str = source_link if source_link else None
        
        # Save to database
        try:
            material = crud.material.create_material(
                db=db,
                material=material_in,
                uploader_id=current_user.id,
                file_path=relative_file_path,
                preview_path=preview_path,
                preview_image_path=preview_image_path,
                resolution=resolution,
                original_link_str=original_link_str,
                source_link_str=source_link_str
            )
            print(f"素材创建成功: ID={material.id}, 类别={category}")
            return material
        except Exception as e:
            print(f"保存素材到数据库失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save material to database: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"上传处理出现未预期的错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/{material_id}/thumbnails", response_model=MaterialSchema)
async def upload_thumbnails(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Upload thumbnails for a material (for photo category).
    """
    # Get the material
    material = crud.material.get_material(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Check permissions
    if material.uploader_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Make sure the material is in the photo category
    if material.category != "照片":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thumbnails can only be added to photo materials"
        )
    
    # Limit number of thumbnails
    if len(files) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 200 thumbnails allowed"
        )
    
    # Process each file
    for file in files:
        # Validate file extension
        if not is_allowed_file("照片", file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension. Must be an image format."
            )
        
        # Save original image
        original_path, relative_original_path = await save_upload_file(file, f"照片/originals/{material_id}")
        
        # Create thumbnail
        relative_thumb_path = await create_thumbnail(original_path)
        
        # Save thumbnail to database
        crud.material.create_thumbnail(
            db=db,
            material_id=material_id,
            filename=file.filename,
            original_path=relative_original_path,
            thumb_path=relative_thumb_path
        )
    
    # Return updated material
    return crud.material.get_material(db, material_id)

@router.get("/search", response_model=MaterialSearchResults)
def search_materials(
    *,
    db: Session = Depends(get_db),
    query: Optional[str] = None,
    category: Optional[str] = None,
    uploader_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Search materials with filtering.
    - Normal users can only see their own materials unless a specific uploader_id is provided
    - Admin users can see all materials or filter by uploader_id
    """
    # 如果不是管理员且没有指定上传者ID，则只显示当前用户的素材
    if not current_user.is_admin and uploader_id is None:
        uploader_id = current_user.id
        print(f"普通用户访问: 限制为只显示用户ID={uploader_id}的素材")
    elif current_user.is_admin and uploader_id is not None:
        print(f"管理员访问: 筛选显示用户ID={uploader_id}的素材")
    elif current_user.is_admin:
        print(f"管理员访问: 显示所有素材")
    
    materials = crud.material.get_materials(
        db=db, skip=skip, limit=limit, category=category, 
        search=query, uploader_id=uploader_id
    )
    
    total = crud.material.count_materials(
        db=db, category=category, search=query, uploader_id=uploader_id
    )
    
    return {"results": materials, "total": total}

@router.get("/{material_id}", response_model=MaterialSchema)
def get_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get material by ID.
    - Normal users can only see their own materials
    - Admin users can see all materials
    """
    material = crud.material.get_material(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # 检查用户是否有权限查看这个素材
    if not current_user.is_admin and material.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this material"
        )
        
    return material

@router.get("/{material_id}/image/{filename}")
def get_original_image(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    filename: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get original image for a material.
    - Normal users can only access their own materials
    - Admin users can access all materials
    """
    material = crud.material.get_material(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # 检查用户是否有权限访问这个素材
    if not current_user.is_admin and material.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this material"
        )
    
    # Find the thumbnail
    thumbnail = None
    for t in material.thumbnails:
        if t.filename == filename:
            thumbnail = t
            break
    
    if not thumbnail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Return the original image
    file_path = os.path.join(settings.MEDIA_DIR, thumbnail.original_path)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )
    
    return FileResponse(file_path)

@router.get("/{material_id}/thumbs")
def get_thumbnails(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get all thumbnails for a material.
    - Normal users can only access their own materials
    - Admin users can access all materials
    """
    material = crud.material.get_material(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # 检查用户是否有权限访问这个素材
    if not current_user.is_admin and material.uploader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this material"
        )
    
    return [
        {
            "id": thumb.id,
            "filename": thumb.filename,
            "thumb_url": f"/media/{thumb.thumb_path}",
            "original_url": f"/api/v1/materials/{material_id}/image/{thumb.filename}"
        }
        for thumb in material.thumbnails
    ]

@router.put("/{material_id}", response_model=MaterialSchema)
def update_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    material_in: MaterialUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a material.
    """
    material = crud.material.get_material(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # 记录权限检查信息
    print(f"更新权限检查: 素材ID={material_id}, 上传者ID={material.uploader_id}, 当前用户ID={current_user.id}, 是否管理员={current_user.is_admin}")
    
    # 检查用户是否有权限编辑这个素材
    if material.uploader_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    material = crud.material.update_material(db, db_material=material, material=material_in)
    return material

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    *,
    db: Session = Depends(get_db),
    material_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """
    Delete a material.
    """
    material = crud.material.get_material(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    if material.uploader_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 记录删除操作
    print(f"删除素材ID: {material_id}, 标题: {material.title}, 分类: {material.category}")
    
    try:
        # 统一路径分隔符，确保路径一致性
        media_dir = settings.MEDIA_DIR.replace("\\", "/")
        
        # 添加一个增强的空目录清理函数
        def clean_empty_dirs(base_path):
            """
            递归向下清理目录，删除所有空目录
            """
            if not os.path.exists(base_path) or not os.path.isdir(base_path):
                return
            
            # 统一路径格式
            base_path = base_path.replace("\\", "/")
            print(f"清理目录及其子目录: {base_path}")
            
            # 对目录内容进行列表操作前，先确保目录存在
            if not os.path.exists(base_path):
                return
                
            # 列出所有子目录和文件
            try:
                contents = os.listdir(base_path)
            except Exception as e:
                print(f"无法列出目录内容: {base_path}, 错误: {str(e)}")
                return
                
            # 递归处理所有子目录
            for item in contents:
                item_path = os.path.join(base_path, item).replace("\\", "/")
                if os.path.isdir(item_path):
                    # 先清理子目录
                    clean_empty_dirs(item_path)
            
            # 再次检查目录是否为空（子目录可能已被删除）
            try:
                if os.path.exists(base_path) and not os.listdir(base_path) and os.path.normpath(base_path) != os.path.normpath(media_dir):
                    try:
                        os.rmdir(base_path)
                        print(f"删除空目录: {base_path}")
                    except Exception as e:
                        print(f"删除空目录失败: {base_path}, 错误: {str(e)}")
            except Exception as e:
                print(f"检查目录是否为空时出错: {base_path}, 错误: {str(e)}")
        
        # 添加一个递归删除空目录的辅助函数
        def remove_empty_dir_recursive(dir_path):
            """递归删除空目录"""
            if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                return
            
            # 统一路径格式，避免Windows/Linux路径混用问题
            dir_path = dir_path.replace("\\", "/")
            
            print(f"检查目录是否为空: {dir_path}")
            
            # 确保目录是空的
            if not os.listdir(dir_path):
                try:
                    os.rmdir(dir_path)
                    print(f"已删除空目录: {dir_path}")
                    
                    # 尝试递归删除父目录
                    parent_dir = os.path.dirname(dir_path)
                    # 确保不会删除media根目录
                    if os.path.normpath(parent_dir) != os.path.normpath(media_dir):
                        remove_empty_dir_recursive(parent_dir)
                except Exception as e:
                    print(f"删除目录时出错: {str(e)}")
            else:
                print(f"目录不为空，无法删除: {dir_path}")
        
        # 记录所有需要检查的目录
        dirs_to_check = set()
        
        # 对于照片素材，先尝试删除整个originals/{material_id}目录
        if material.category == "照片":
            # 直接删除material_id特定目录结构
            material_id_path = os.path.join(media_dir, f"照片/originals/{material_id}")
            material_id_path = material_id_path.replace("\\", "/")
            if os.path.exists(material_id_path):
                print(f"删除照片素材目录: {material_id_path}")
                try:
                    shutil.rmtree(material_id_path, ignore_errors=True)
                    print(f"成功删除整个照片素材目录: {material_id_path}")
                    
                    # 将originals目录添加到检查列表，以便后续清理空目录
                    originals_dir = os.path.dirname(material_id_path)
                    dirs_to_check.add(originals_dir)
                except Exception as e:
                    print(f"删除照片素材目录失败: {material_id_path}, 错误: {str(e)}")
                    # 如果整体目录删除失败，会继续删除单个文件
            
            # 记录特定存放照片的目录
            special_dirs = [
                os.path.join(media_dir, f"照片/originals/{material_id}").replace("\\", "/"),
                os.path.join(media_dir, f"照片/originals/{material_id}/thumbs").replace("\\", "/")
            ]
            for dir_path in special_dirs:
                if os.path.exists(dir_path):
                    dirs_to_check.add(dir_path)
        
        # 删除主文件
        if material.file_path:
            file_path = os.path.join(media_dir, material.file_path.replace("\\", "/"))
            print(f"尝试删除主文件: {file_path}")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除主文件: {file_path}")
                # 记录目录
                dirs_to_check.add(os.path.dirname(file_path))
            else:
                print(f"主文件不存在: {file_path}")
        
        # 删除预览文件
        if material.preview_path:
            preview_path = os.path.join(media_dir, material.preview_path.replace("\\", "/"))
            print(f"尝试删除预览文件: {preview_path}")
            if os.path.exists(preview_path):
                os.remove(preview_path)
                print(f"已删除预览文件: {preview_path}")
                # 记录目录
                dirs_to_check.add(os.path.dirname(preview_path))
            else:
                print(f"预览文件不存在: {preview_path}")
        
        # 删除预览图片
        if material.preview_image_path:
            preview_img_path = os.path.join(media_dir, material.preview_image_path.replace("\\", "/"))
            print(f"尝试删除预览图片: {preview_img_path}")
            if os.path.exists(preview_img_path):
                os.remove(preview_img_path)
                print(f"已删除预览图片: {preview_img_path}")
                # 记录目录
                dirs_to_check.add(os.path.dirname(preview_img_path))
            else:
                print(f"预览图片不存在: {preview_img_path}")
        
        # 对于照片素材，删除缩略图和原始图片（如果整体目录删除失败时的备用方案）
        if material.category == "照片":
            # 收集material_id目录以便后续删除
            material_id_dirs = set()
            
            # 检查originals/{material_id}目录是否还存在（如果之前的整体删除失败）
            material_id_path = os.path.join(media_dir, f"照片/originals/{material_id}").replace("\\", "/")
            if os.path.exists(material_id_path):
                print(f"整体目录删除失败，开始逐个删除文件")
                
                # 处理所有缩略图
                for thumb in material.thumbnails:
                    if thumb.thumb_path:
                        # 统一使用正斜杠处理路径
                        thumb_path = os.path.join(media_dir, thumb.thumb_path.replace("\\", "/"))
                        print(f"尝试删除缩略图: {thumb_path}")
                        if os.path.exists(thumb_path):
                            os.remove(thumb_path)
                            print(f"已删除缩略图: {thumb_path}")
                            # 记录缩略图所在目录
                            dirs_to_check.add(os.path.dirname(thumb_path))
                        else:
                            print(f"缩略图不存在: {thumb_path}")
                    
                    if thumb.original_path:
                        # 统一使用正斜杠处理路径
                        original_path = os.path.join(media_dir, thumb.original_path.replace("\\", "/"))
                        print(f"尝试删除原始图片: {original_path}")
                        if os.path.exists(original_path):
                            os.remove(original_path)
                            print(f"已删除原始图片: {original_path}")
                            # 记录原始图片所在目录
                            dirs_to_check.add(os.path.dirname(original_path))
                            
                            # 获取material_id目录路径
                            # 这里应对形如 /media/照片/originals/{material_id}/ 的路径
                            orig_dir = os.path.dirname(original_path)
                            material_id_dirs.add(orig_dir)
                        else:
                            print(f"原始图片不存在: {original_path}")
                
                # 确保material_id目录也会被检查
                for dir_path in material_id_dirs:
                    dirs_to_check.add(dir_path)
                    # 也添加originals目录
                    dirs_to_check.add(os.path.dirname(dir_path))
                
                # 再次尝试删除整个目录树
                try:
                    print(f"再次尝试强制删除整个目录: {material_id_path}")
                    shutil.rmtree(material_id_path, ignore_errors=True)
                    print(f"已强制删除目录树: {material_id_path}")
                except Exception as e:
                    print(f"最终尝试删除目录树失败: {material_id_path}, 错误: {str(e)}")
        
        # 递归清理所有记录的目录
        # 先按路径长度排序，确保先删除较深的目录
        sorted_dirs = sorted(dirs_to_check, key=len, reverse=True)
        for dir_path in sorted_dirs:
            # 使用增强版目录清理函数
            clean_empty_dirs(dir_path)
        
        # 特别检查照片类别的originals目录
        if material.category == "照片":
            originals_dir = os.path.join(media_dir, "照片/originals").replace("\\", "/")
            if os.path.exists(originals_dir):
                print(f"检查originals目录: {originals_dir}")
                
                # 检查originals目录是否为空
                try:
                    contents = os.listdir(originals_dir)
                    if not contents:
                        # originals目录为空，可以删除
                        try:
                            os.rmdir(originals_dir)
                            print(f"删除空的originals目录: {originals_dir}")
                        except Exception as e:
                            print(f"删除originals目录失败: {originals_dir}, 错误: {str(e)}")
                    else:
                        # originals目录不为空，打印剩余内容
                        print(f"originals目录不为空，包含 {len(contents)} 个项目")
                        for item in contents:
                            print(f"  - {item}")
                except Exception as e:
                    print(f"检查originals目录失败: {originals_dir}, 错误: {str(e)}")
                    
                # 最后检查照片目录是否为空
                photos_dir = os.path.join(media_dir, "照片").replace("\\", "/")
                if os.path.exists(photos_dir):
                    try:
                        if not os.listdir(photos_dir):
                            # 照片目录为空，可以删除
                            try:
                                os.rmdir(photos_dir)
                                print(f"删除空的照片目录: {photos_dir}")
                            except Exception as e:
                                print(f"删除照片目录失败: {photos_dir}, 错误: {str(e)}")
                    except Exception as e:
                        print(f"检查照片目录失败: {photos_dir}, 错误: {str(e)}")
        
    except Exception as e:
        print(f"删除文件时出错: {str(e)}")
        # 继续删除数据库记录，即使文件删除失败
    
    # 从数据库中删除
    crud.material.delete_material(db, db_material=material)
    print(f"已从数据库中删除素材ID: {material_id}") 