import sqlite3

# 连接数据库
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# 获取materials表结构
cursor.execute('PRAGMA table_info(materials)')
columns = cursor.fetchall()

print("材料表结构:")
for column in columns:
    print(f"{column[0]}: {column[1]} ({column[2]})")

# 关闭连接
conn.close() 