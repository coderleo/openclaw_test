"""
验证码协作服务器
爬虫端：POST 截图 → 等待结果
你通过 OpenClaw/Telegram 看到图片 → 回复坐标 → 爬虫继续
"""
import json
import time
import threading
import uuid
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# 存放待处理和已处理的验证码任务
TASKS = {}  # task_id -> {"image": path, "status": "pending"|"solved", "clicks": [...]}
IMAGES_DIR = Path("captcha_solver/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


class CaptchaHandler(BaseHTTPRequestHandler):
    """简单的 HTTP API 处理验证码请求"""

    def do_POST(self):
        if self.path == "/submit":
            # 爬虫提交验证码截图
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            task_id = str(uuid.uuid4())[:8]
            image_path = IMAGES_DIR / f"{task_id}.png"
            image_path.write_bytes(body)
            TASKS[task_id] = {
                "image": str(image_path),
                "status": "pending",
                "clicks": [],
                "created": time.time(),
            }
            self._respond(200, {"task_id": task_id, "status": "pending"})

        elif self.path.startswith("/solve/"):
            # 你回复坐标后，OpenClaw webhook 调这个接口
            task_id = self.path.split("/solve/")[1]
            if task_id not in TASKS:
                self._respond(404, {"error": "task not found"})
                return
            content_length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(content_length))
            # body 格式: {"clicks": [{"x": 120, "y": 85}, {"x": 230, "y": 150}]}
            TASKS[task_id]["clicks"] = body.get("clicks", [])
            TASKS[task_id]["status"] = "solved"
            self._respond(200, {"task_id": task_id, "status": "solved"})
        else:
            self._respond(404, {"error": "not found"})

    def do_GET(self):
        if self.path.startswith("/poll/"):
            # 爬虫轮询等待结果
            task_id = self.path.split("/poll/")[1]
            if task_id not in TASKS:
                self._respond(404, {"error": "task not found"})
                return
            self._respond(200, TASKS[task_id])

        elif self.path == "/pending":
            # 查看所有待处理的验证码
            pending = {
                k: v for k, v in TASKS.items() if v["status"] == "pending"
            }
            self._respond(200, pending)
        else:
            self._respond(404, {"error": "not found"})

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        print(f"[CaptchaServer] {args[0]}")


def run_server(host="0.0.0.0", port=5555):
    server = HTTPServer((host, port), CaptchaHandler)
    print(f"[CaptchaServer] 验证码协作服务启动: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
