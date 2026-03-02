#!/bin/bash
# OpenClaw 通知脚本 - 检查待处理验证码并发送到你的聊天渠道
# 建议用 openclaw cron 定时跑，或者在 server.py 提交时触发

SERVER="http://127.0.0.1:5555"
# 你的聊天目标，改成你自己的 Telegram/WhatsApp ID
CHAT_TARGET="${OPENCLAW_CHAT_TARGET:-@your_telegram_id}"
CHANNEL="${OPENCLAW_CHANNEL:-telegram}"

# 获取待处理的验证码
PENDING=$(curl -s "$SERVER/pending")

if [ "$PENDING" = "{}" ]; then
    exit 0
fi

# 遍历每个待处理任务
echo "$PENDING" | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
for tid, info in tasks.items():
    print(f'{tid} {info[\"image\"]}')
" | while read TASK_ID IMAGE_PATH; do
    # 通过 OpenClaw 发送图片到你的聊天
    openclaw message send \
        --channel "$CHANNEL" \
        --target "$CHAT_TARGET" \
        --message "🔒 验证码待处理 [task:$TASK_ID]
请查看图片，回复格式：
solve $TASK_ID x1,y1 x2,y2 x3,y3
例如: solve $TASK_ID 120,85 230,150" \
        --attachment "$IMAGE_PATH"
    
    echo "[Notify] 已发送 task $TASK_ID 到 $CHANNEL"
done
