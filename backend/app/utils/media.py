import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import UploadFile
from PIL import Image
import moviepy.editor as mp

from app.core.config import settings

# Allowed file extensions by category
ALLOWED_EXTENSIONS = {
    "AE模板": [".zip", ".rar"],
    "视频": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "音乐": [".mp3", ".wav", ".flac", ".ogg", ".aac"],
    "照片": [".jpg", ".jpeg", ".png", ".gif", ".webp"]
}

def is_allowed_file(category: str, filename: str) -> bool:
    """Check if the file is allowed for the given category."""
    extension = os.path.splitext(filename)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(category, [])

def create_unique_filename(filename: str) -> str:
    """Create a unique filename using UUID."""
    extension = os.path.splitext(filename)[1]
    return f"{uuid.uuid4()}{extension}"

async def save_upload_file(upload_file: UploadFile, category: str) -> Tuple[str, str]:
    """Save uploaded file and return the file path relative to the media directory."""
    try:
        # 确保媒体根目录存在
        if not os.path.exists(settings.MEDIA_DIR):
            print(f"创建媒体根目录: {settings.MEDIA_DIR}")
            os.makedirs(settings.MEDIA_DIR, exist_ok=True)
        
        # Create category subdirectory if it doesn't exist
        category_dir = os.path.join(settings.MEDIA_DIR, category)
        print(f"检查目录: {category_dir}")
        
        # 确保分类目录存在
        if not os.path.exists(category_dir):
            print(f"创建目录: {category_dir}")
            os.makedirs(category_dir, exist_ok=True)
        
        # 检查目录是否可写
        if not os.access(category_dir, os.W_OK):
            raise IOError(f"无法写入目录 {category_dir} - 权限不足")
        
        # Create unique filename
        filename = create_unique_filename(upload_file.filename)
        file_path = os.path.join(category_dir, filename)
        print(f"将保存文件到: {file_path}")
        
        # Save file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(upload_file.file, f)
        
        # 确认文件已创建
        if not os.path.exists(file_path):
            raise IOError(f"文件未能正确保存: {file_path}")
            
        # 文件大小检查
        file_size = os.path.getsize(file_path)
        print(f"文件 {filename} 已保存，大小: {file_size} 字节")
        
        # Return relative paths for storage in database
        relative_path = os.path.join(category, filename).replace("\\", "/")
        return file_path, relative_path
    except Exception as e:
        print(f"保存文件失败 {upload_file.filename}: {str(e)}")
        # 重新抛出异常，让调用方处理
        raise

async def process_video(file_path: str, custom_preview_dir: str = None, custom_preview_name: str = None) -> Tuple[str, str]:
    """
    Process a video file:
    1. Extract resolution
    2. Create a thumbnail from the first frame
    Return: (resolution, preview_path)
    """
    try:
        # 确保文件路径使用正斜杠
        file_path = file_path.replace("\\", "/")
        print(f"处理视频: {file_path}")
        
        # Extract resolution
        video = mp.VideoFileClip(file_path)
        resolution = f"{video.size[0]}x{video.size[1]}"
        print(f"提取到分辨率: {resolution}")
        
        # Create thumbnail from first frame
        filename = os.path.basename(file_path)
        preview_filename = custom_preview_name or f"preview_{filename.split('.')[0]}.jpg"
        
        # 使用自定义路径或默认路径
        if custom_preview_dir:
            preview_dir = custom_preview_dir
        else:
            # 在同一目录下创建预览目录
            preview_dir = os.path.join(os.path.dirname(file_path), "previews")
        
        # 确保预览目录存在
        os.makedirs(preview_dir, exist_ok=True)
        
        # 构建完整的预览图路径
        preview_path = os.path.join(preview_dir, preview_filename)
        print(f"预览图将保存到: {preview_path}")
        
        # Save the first frame as a thumbnail
        video.save_frame(preview_path, t=1)  # 使用第1秒的帧而不是第0秒，避免黑屏
        video.close()
        
        # 计算相对于媒体目录的路径
        media_dir = settings.MEDIA_DIR.replace("\\", "/")
        preview_path = preview_path.replace("\\", "/")
        
        if custom_preview_dir:
            # 从媒体目录计算相对路径
            if preview_path.startswith(media_dir):
                relative_preview_path = preview_path[len(media_dir):].lstrip("/")
            else:
                relative_preview_path = os.path.relpath(preview_path, media_dir).replace("\\", "/")
        else:
            # 构建相对路径
            category_dir = os.path.basename(os.path.dirname(file_path))
            relative_preview_path = f"{category_dir}/previews/{preview_filename}"
        
        print(f"相对预览路径: {relative_preview_path}")
        return resolution, relative_preview_path
    except Exception as e:
        print(f"视频处理失败: {str(e)}")
        raise

async def create_thumbnail(image_path: str, thumb_width: int = settings.THUMB_SIZE) -> str:
    """Create a thumbnail for an image and return the thumbnail path."""
    # Create thumbnails directory if it doesn't exist
    thumb_dir = os.path.join(os.path.dirname(image_path), "thumbs")
    os.makedirs(thumb_dir, exist_ok=True)
    
    # Generate thumbnail filename
    filename = os.path.basename(image_path)
    thumb_filename = f"thumb_{filename}"
    thumb_path = os.path.join(thumb_dir, thumb_filename)
    
    # Create thumbnail
    with Image.open(image_path) as img:
        # Calculate new height maintaining aspect ratio
        width_percent = (thumb_width / float(img.size[0]))
        thumb_height = int((float(img.size[1]) * float(width_percent)))
        img = img.resize((thumb_width, thumb_height), Image.LANCZOS)
        img.save(thumb_path)
    
    # Return relative thumbnail path
    relative_thumb_path = os.path.join(
        os.path.basename(os.path.dirname(image_path)),
        "thumbs",
        thumb_filename
    ).replace("\\", "/")
    
    return relative_thumb_path 