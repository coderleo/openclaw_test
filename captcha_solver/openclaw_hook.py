"""
OpenClaw 消息处理钩子
当你在聊天里回复 "solve task_id x1,y1 x2,y2" 时，
这个脚本解析坐标并提交到协作服务器
"""
import sys
import json
import requests

SERVER = "http://127.0.0.1:5555"


def parse_and_solve(message: str):
    """
    解析消息格式: solve <task_id> x1,y1 x2,y2 x3,y3
    """
    parts = message.strip().split()
    if len(parts) < 3 or parts[0].lower() != "solve":
        print("格式错误。用法: solve <task_id> x1,y1 x2,y2 ...")
        return

    task_id = parts[1]
    clicks = []
    for coord in parts[2:]:
        try:
            x, y = coord.split(",")
            clicks.append({"x": int(x), "y": int(y)})
        except ValueError:
            print(f"坐标格式错误: {coord}，应为 x,y")
            return

    resp = requests.post(
        f"{SERVER}/solve/{task_id}",
        json={"clicks": clicks},
    )
    result = resp.json()
    print(f"✅ 已提交: task={task_id}, 点击{len(clicks)}个位置, 状态={result['status']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        parse_and_solve(" ".join(sys.argv[1:]))
    else:
        # 从 stdin 读取（OpenClaw hook 模式）
        for line in sys.stdin:
            if line.strip().lower().startswith("solve"):
                parse_and_solve(line)
