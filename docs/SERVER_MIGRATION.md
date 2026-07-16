# 服务器迁移指南

> 云服务器到期时，按此流程迁移到新服务器。数据不丢，小程序免重新审核。

## 前置条件

- 新服务器已开通，有公网 IP，能 SSH 登录
- 本地备份存在 `/home/wyf/student-manager-backup/YYYYMMDD/`（含 `data/student_manager.db` 和 `uploads/`）
- GitHub 仓库可访问：`https://github.com/wyf2433/student-manager`
- 微信开发者工具已安装

## 涉及改动清单

| 环节 | 要改什么 |
|------|---------|
| 新服务器 | `git clone` + 恢复 db/uploads + `.env` + weixinkey + systemd |
| 微信云函数 | 改 `index.js` 里的 `BASE_HOST` → 重新部署 |
| 微信小程序 | **不用改**，不用重新审核 |
| API_KEY | 不变，`.env` 原样复制 |
| 数据库 | 用备份恢复，数据不丢 |

## 步骤 1：新服务器部署后端

```bash
# 安装系统依赖
apt update && apt install -y python3 python3-venv git sqlite3

# 拉代码
cd /opt
git clone https://github.com/wyf2433/student-manager.git
cd student-manager/backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 创建数据目录
mkdir -p data uploads
```

## 步骤 2：恢复数据

从本地备份把数据库和上传文件传到新服务器：

```bash
# 在本地 Linux 机器执行（替换 NEW_IP）
scp /home/wyf/student-manager-backup/YYYYMMDD/data/student_manager.db root@NEW_IP:/opt/student-manager/backend/data/
scp /home/wyf/student-manager-backup/YYYYMMDD/uploads/* root@NEW_IP:/opt/student-manager/backend/uploads/
```

## 步骤 3：配置 .env 和上传密钥

```bash
# 在新服务器创建 .env（内容与旧服务器一致）
cat > /opt/student-manager/backend/.env << 'EOF'
# ===== 后端配置 =====
API_KEY=REDACTED
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DB_PATH=./data/student_manager.db
UPLOAD_DIR=./uploads
MAX_EXCEL_SIZE_MB=10
MAX_IMAGE_SIZE_MB=5

# ===== 微信小程序配置 =====
WECHAT_APPID=wxe7bfa91a1970e2dc
WECHAT_APP_SECRET=4fec4be6b0d68c3a26044de82a2a8aae
# 上传密钥文件路径(不复制进仓库)
WECHAT_UPLOAD_KEY_PATH=/root/weixinkey
EOF

# 上传密钥文件也要从旧服务器或本地复制过去
# scp /home/wyf/weixinkey root@NEW_IP:/root/weixinkey
```

## 步骤 4：初始化数据库

```bash
cd /opt/student-manager/backend
source .venv/bin/activate
python -c "from database import init_db; init_db()"
```

> 这一步是幂等的，已有数据不会丢，只补缺的表/列。

## 步骤 5：配置开机自启（systemd）

```bash
cat > /etc/systemd/system/student-manager.service << 'EOF'
[Unit]
Description=Student Manager API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/student-manager/backend
ExecStart=/opt/student-manager/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now student-manager

# 验证运行状态
systemctl status student-manager
curl http://localhost:8000/api/classes
```

## 步骤 6：修改微信云函数（关键）

云函数 `cloudfunctions/api/index.js` 第 4 行硬编码了服务器 IP：

```js
const BASE_HOST = '47.239.25.178'  // ← 改成新服务器 IP
const BASE_PORT = 80
```

改完后：

1. 打开**微信开发者工具**
2. 右键云函数 `cloudfunctions/api` → **上传并部署：云端安装依赖**
3. 等待部署完成

> 如果只换了服务器 IP，云函数环境变量 `API_KEY` 不用改（值不变）。

## 步骤 7：验证

1. 用手机打开微信小程序，进入学生列表，确认数据正常加载
2. 测试添加学生、导入成绩等写操作
3. 测试图片上传（留痕功能）

## 小程序端说明

小程序代码里**没有硬编码 IP**，所有请求都走云函数转发，所以：

- 小程序本身**不用改代码**
- **不用重新提交微信审核**
- 用户体验版/正式版都不受影响

## 备份方法（日常）

服务器到期前，在本地 Linux 机器执行：

```bash
BACKUP_DIR="/home/wyf/student-manager-backup/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR/data" "$BACKUP_DIR/uploads"
scp root@47.239.25.178:/opt/student-manager/backend/data/student_manager.db "$BACKUP_DIR/data/"
scp -r root@47.239.25.178:/opt/student-manager/backend/uploads/* "$BACKUP_DIR/uploads/"
```

验证备份完整性：

```bash
sqlite3 "$BACKUP_DIR/data/student_manager.db" "
SELECT 'classes', COUNT(*) FROM classes
UNION ALL SELECT 'students', COUNT(*) FROM students
UNION ALL SELECT 'scores', COUNT(*) FROM scores;
"
```
