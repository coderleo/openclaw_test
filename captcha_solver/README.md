# 验证码人机协作方案

## 工作流程

```
爬虫遇到验证码 → 截图提交到本地服务 → OpenClaw 发图到你手机
    → 你看图回复坐标 → 服务器收到 → 爬虫自动点击 → 继续爬取
```

## 文件说明

| 文件 | 作用 |
|------|------|
| `server.py` | 本地协作服务器（接收截图、存储、分发结果） |
| `client.py` | 爬虫端客户端（截图→提交→轮询→点击） |
| `openclaw_notify.sh` | 通过 OpenClaw 把验证码图片发到你的聊天 |
| `openclaw_hook.py` | 解析你的回复，提交坐标到服务器 |
| `example_usage.py` | Selenium 集成示例 |

## 使用步骤

### 1. 启动协作服务器
```bash
python captcha_solver/server.py
```

### 2. 配置 OpenClaw 通知
修改 `openclaw_notify.sh` 里的 `CHAT_TARGET` 和 `CHANNEL`，然后注册为 cron：
```bash
openclaw cron add --name "captcha-check" --interval 5s --command "bash captcha_solver/openclaw_notify.sh"
```

### 3. 配置 OpenClaw 消息钩子
让 OpenClaw 监听你的 "solve" 回复：
```bash
openclaw hooks add --trigger "message:solve*" --command "python3 captcha_solver/openclaw_hook.py"
```

### 4. 在爬虫里集成
```python
from captcha_solver.client import CaptchaSolver

solver = CaptchaSolver()
# 检测到验证码时
solver.solve(driver, captcha_element)
```

### 5. 回复格式
收到验证码图片后，在聊天里回复：
```
solve abc123 120,85 230,150 300,200
```
格式：`solve <task_id> x坐标,y坐标 x坐标,y坐标 ...`
