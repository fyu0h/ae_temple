# AE模板素材管理平台

一站式管理AE模板、视频、音乐和照片素材的平台，使用Vue 3前端和FastAPI后端构建。

## 功能特点

- **分类系统**：支持AE模板、视频、音乐和照片四大类素材管理
- **动态表单**：上传页面根据所选分类动态调整表单内容和限制
- **多样素材支持**：
  - AE模板：支持zip、rar格式上传，必填预览视频
  - 视频：支持常见视频格式，自动提取分辨率和生成预览图
  - 音乐：支持常见音频格式，可选上传封面图
  - 照片：支持批量上传（最多200张），自动生成缩略图
- **搜索和筛选**：支持关键词搜索和分类筛选
- **用户系统**：支持注册登录，普通用户和管理员角色
- **权限控制**：普通用户只能管理自己的素材，管理员可管理所有素材

## 技术栈

### 前端
- Vue 3 (Composition API)
- Pinia (状态管理)
- Vue Router (路由)
- Bootstrap 5 (UI框架)
- Axios (HTTP客户端)

### 后端
- FastAPI (Web框架)
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- JWT (认证)
- Python Libraries:
  - moviepy (视频处理)
  - Pillow (图像处理)

## 快速开始

### 后端设置

1. 创建并激活Python虚拟环境:

```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 初始化数据库:

```bash
cd backend
python initial_setup.py
```

4. 启动后端服务器:

```bash
cd backend
uvicorn main:app --reload
```

后端API将在 http://localhost:8000 上运行。
可以访问 http://localhost:8000/docs 查看API文档。

### 前端设置

1. 安装Node.js依赖:

```bash
cd frontend
npm install
```

2. 启动开发服务器:

```bash
npm run dev
```

前端应用将在 http://localhost:5173 上运行。

## 项目结构

```
├── backend/                  # 后端代码
│   ├── app/                  # 应用代码
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── crud/             # 数据库操作
│   │   ├── db/               # 数据库设置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模式
│   │   └── utils/            # 工具函数
│   ├── media/                # 上传的媒体文件目录
│   ├── main.py               # 主应用入口
│   └── requirements.txt      # Python依赖
└── frontend/                 # 前端代码
    ├── public/               # 静态资源
    ├── src/                  # 源代码
    │   ├── assets/           # 资源文件
    │   ├── components/       # Vue组件
    │   ├── router/           # Vue Router配置
    │   ├── services/         # API服务
    │   ├── stores/           # Pinia stores
    │   ├── views/            # 页面组件
    │   ├── App.vue           # 主组件
    │   └── main.js           # 入口文件
    ├── index.html            # HTML模板
    └── package.json          # Node.js依赖
```

## 默认用户

系统初始会创建一个管理员账户:

- 邮箱: admin@example.com
- 密码: admin123

请在生产环境中更改此密码。

## API端点

### 认证
- POST /api/v1/auth/login - 登录
- POST /api/v1/auth/register - 注册

### 用户
- GET /api/v1/users/me - 获取当前用户信息
- PATCH /api/v1/users/me - 更新当前用户信息

### 素材
- POST /api/v1/materials/ - 上传素材
- GET /api/v1/materials/search - 搜索素材
- GET /api/v1/materials/{id} - 获取素材详情
- PUT /api/v1/materials/{id} - 更新素材
- DELETE /api/v1/materials/{id} - 删除素材
- POST /api/v1/materials/{id}/thumbnails - 上传照片缩略图
- GET /api/v1/materials/{id}/thumbs - 获取所有缩略图
- GET /api/v1/materials/{id}/image/{filename} - 获取原始图片 