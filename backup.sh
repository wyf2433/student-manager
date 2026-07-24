#!/bin/bash
# 学生管理后端备份脚本
# 备份:SQLite 热备份 + .env + uploads
# 保留:最近 30 份
set -euo pipefail

APP_DIR="/opt/student-manager/backend"
DB_PATH="$APP_DIR/data/student_manager.db"
BACKUP_DIR="/opt/backups/student-manager"
KEEP=30
TS=$(date +%Y%m%d_%H%M%S)
WORK_DIR=$(mktemp -d)

trap 'rm -rf "$WORK_DIR"' EXIT

mkdir -p "$BACKUP_DIR"

# 1. SQLite 热备份(.backup 命令,不锁库,WAL 安全)
echo "[$TS] 备份数据库..."
sqlite3 "$DB_PATH" ".backup '$WORK_DIR/student_manager.db'"
sqlite3 "$WORK_DIR/student_manager.db" "PRAGMA integrity_check;" >/dev/null

# 2. 复制 .env 和 uploads
cp "$APP_DIR/.env" "$WORK_DIR/.env"
if [ -d "$APP_DIR/uploads" ]; then
  cp -r "$APP_DIR/uploads" "$WORK_DIR/uploads"
fi

# 3. 打包
ARCHIVE="$BACKUP_DIR/backup_$TS.tar.gz"
tar -czf "$ARCHIVE" -C "$WORK_DIR" .
echo "[$TS] 已生成: $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1))"

# 4. 清理旧备份(保留最近 KEEP 份)
cd "$BACKUP_DIR"
ls -1t backup_*.tar.gz 2>/dev/null | tail -n +$((KEEP + 1)) | while read -r old; do
  rm -f "$old"
  echo "[$TS] 清理旧备份: $old"
done

# 5. 汇总
COUNT=$(ls -1 "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | wc -l)
echo "[$TS] 完成。当前共 $COUNT 份备份。"
