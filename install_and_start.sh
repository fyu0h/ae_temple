#!/bin/bash

# 自动安装依赖和启动AE模板应用的脚本
# 在Linux系统上首次使用前，请运行: chmod +x install_and_start.sh

# 设置颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 输出带颜色的信息函数
info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
  exit 1
}

# 检查系统是否为Linux
if [[ "$(uname)" != "Linux" ]]; then
  error "此脚本只能在Linux系统上运行!"
fi

# 检查必要的依赖
info "检查系统必要依赖..."

# 检查Python3
if ! command -v python3 &> /dev/null; then
  info "安装Python3..."
  sudo apt-get update || error "无法更新包列表"
  sudo apt-get install -y python3 python3-pip python3-venv || error "无法安装Python3"
else
  success "Python3已安装"
fi

# 检查Node.js和npm
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
  info "安装Node.js和npm..."
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - || error "无法设置Node.js源"
  sudo apt-get install -y nodejs || error "无法安装Node.js和npm"
else
  success "Node.js和npm已安装"
fi

# 检查虚拟环境工具
if ! command -v python3 -m venv &> /dev/null; then
  info "安装Python虚拟环境工具..."
  sudo apt-get install -y python3-venv || error "无法安装python3-venv"
fi

# 安装后端依赖
info "设置后端环境..."
cd backend || error "无法进入backend目录"

# 创建并激活虚拟环境
if [ ! -d "venv" ]; then
  info "创建Python虚拟环境..."
  python3 -m venv venv || error "无法创建虚拟环境"
fi

# 激活虚拟环境
source venv/bin/activate || error "无法激活虚拟环境"

# 安装Python依赖
info "安装Python依赖..."
pip install --upgrade pip || error "无法更新pip"
pip install -r ../requirements.txt || error "无法安装Python依赖"
# 安装缺失的pydantic_settings包
info "安装pydantic_settings包..."
pip install pydantic-settings || error "无法安装pydantic-settings"

# 安装email-validator包
info "安装email-validator包..."
pip install email-validator || error "无法安装email-validator"

# 确保初始设置已完成
info "运行初始化设置..."
python3 initial_setup.py || error "初始化设置失败"

success "后端环境设置完成"

# 检测服务器IP地址
info "检测服务器IP地址..."
SERVER_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v "127.0.0.1" | head -n 1)
if [ -z "$SERVER_IP" ]; then
  SERVER_IP="0.0.0.0"
  info "无法检测到服务器IP，将使用0.0.0.0"
else
  info "检测到服务器IP: $SERVER_IP"
fi

# 安装前端依赖
info "设置前端环境..."
cd ../frontend || error "无法进入frontend目录"

# 创建前端环境变量文件
info "创建前端环境变量配置..."
cat > .env << EOF
VITE_API_BASE_URL=http://0.0.0.0:8000
VITE_ALLOWED_HOSTS=localhost,127.0.0.1,home.iinin.me,$SERVER_IP
EOF

info "安装Node.js依赖..."
npm install || error "无法安装Node.js依赖"

success "前端环境设置完成"

# 启动后端
info "启动后端服务器..."
cd ../backend || error "无法进入backend目录"
source venv/bin/activate || error "无法激活虚拟环境"
export SERVER_HOST="0.0.0.0"
export SERVER_PORT="8000"
python3 -m uvicorn main:app --host $SERVER_HOST --port $SERVER_PORT --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
info "启动前端服务器..."
cd ../frontend || error "无法进入frontend目录"
export VITE_API_URL="http://$SERVER_IP:8000"
npm run dev -- --host &
FRONTEND_PID=$!

success "应用已成功启动!"
echo "====================================================="
echo "后端运行于: http://$SERVER_IP:8000"
echo "前端运行于: http://$SERVER_IP:5173"
echo "默认管理员登录:"
echo "  邮箱: admin@example.com"
echo "  密码: admin123"
echo "====================================================="
echo "按 Ctrl+C 停止服务器"

# 捕获终止信号
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# 保持脚本运行
wait 