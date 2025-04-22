import sqlite3
import os
from app.core.config import settings

def run_migrations():
    """运行数据库迁移脚本，添加新字段"""
    db_path = "app.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查preview_image_path字段是否已存在
    cursor.execute("PRAGMA table_info(materials)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    if "preview_image_path" not in column_names:
        print("添加preview_image_path字段到materials表")
        cursor.execute("ALTER TABLE materials ADD COLUMN preview_image_path TEXT;")
        conn.commit()
        print("字段添加成功")
    else:
        print("preview_image_path字段已存在")
    
    # 检查source_link字段是否已存在
    if "source_link" not in column_names:
        print("添加source_link字段到materials表")
        cursor.execute("ALTER TABLE materials ADD COLUMN source_link TEXT;")
        conn.commit()
        print("source_link字段添加成功")
    else:
        print("source_link字段已存在")
    
    conn.close()

if __name__ == "__main__":
    run_migrations()
    print("数据库迁移完成") 