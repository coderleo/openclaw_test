---
inclusion: always
---

# OpenClaw 安装与问题排查指南

## 什么是 OpenClaw

OpenClaw 是一个开源的自主 AI agent 框架，由 Peter Steinberger 开发（前身为 Clawdbot / Moltbot）。
它运行在本地硬件上，通过 WhatsApp、Telegram、Discord 等消息平台交互，能主动执行任务。

- GitHub: https://github.com/openclaw/openclaw
- 官方文档: https://docs.openclaw.ai

## 前置条件

- Node.js 22+（Ubuntu apt 源只有 18.x，需要用 NodeSource 源）
- LLM 后端（Anthropic API / OpenAI API / 本地 vLLM 等）
- Windows 用户推荐使用 WSL2（原生 Windows 支持不稳定）

## 安装步骤

### 1. 安装 Node.js 22（WSL/Linux）

Ubuntu 默认源只有 Node 18，需要添加 NodeSource 源：

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
node -v  # 确认 v22.x
```

### 2. 安装 OpenClaw

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### 3. 运行 onboarding 向导

```bash
openclaw onboard --install-daemon
```

配置 API key、消息渠道、后台守护进程。

### 4. 验证安装

```bash
openclaw doctor
```

### 5. 启动 Gateway

```bash
openclaw gateway
```

### 6. 使用

- 终端聊天: `openclaw tui`
- 管理面板: `openclaw dashboard`
- 浏览器: `http://127.0.0.1:18789/`

## 常见问题与解决方案

### 问题 1: WSL 中 DNS 解析失败

**现象:** 
- `Temporary failure resolving 'archive.ubuntu.com'`
- 或飞书消息无回复，日志中出现 `getaddrinfo EAI_AGAIN open.feishu.cn`
- `ping` 可能通，但 Node.js 进程仍然解析失败（Gateway 启动时缓存了旧的 DNS 配置）

**原因:** WSL 的 DNS 配置不正确，且 8.8.8.8 在国内可能被墙。

**解决:**
```bash
# 国内环境用阿里/114 DNS
echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf

# 重要：修改 DNS 后必须重启 Gateway
openclaw gateway stop
openclaw gateway
```

**永久解决（防止 WSL 重启后 DNS 被重置）：**
```bash
sudo bash -c 'echo -e "[network]\ngenerateResolvConf = false" > /etc/wsl.conf'
echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf
```

> ⚠️ 修改 DNS 后必须重启 Gateway，`ping` 通不代表 Gateway 进程能解析，Node.js 可能缓存了旧的 DNS 结果。

### 问题 2: `openclaw` 命令找不到

**现象:** `openclaw: command not found`

**原因:** npm 全局安装目录未加入 PATH。

**解决:**
```bash
export PATH="$(npm prefix -g)/bin:$PATH"
echo 'export PATH="$(npm prefix -g)/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 问题 3: Dashboard 认证失败

**现象:** `unauthorized: gateway token missing` 或 `too many failed authentication attempts`

**解决:** 获取带 token 的 URL：
```bash
openclaw dashboard --no-open
```
复制输出的完整 URL（含 `#token=...`）到浏览器打开。

### 问题 4: WSL 中浏览器无法访问 127.0.0.1

**现象:** Windows 浏览器访问 `127.0.0.1:18789` 报 `ERR_CONNECTION_REFUSED`

**原因:** WSL 和 Windows 的 localhost 不互通。

**解决:**
```bash
hostname -I  # 获取 WSL 的实际 IP（如 172.x.x.x）
```
用该 IP 替换 `127.0.0.1` 访问。或直接用 `openclaw tui` 在终端聊天。

### 问题 5: Agent 报 Connection error

**现象:** 发消息后返回 `Connection error`

**原因:** OpenClaw 连不上 LLM 后端。

**排查:**
```bash
# 检查模型配置
openclaw models list
cat ~/.openclaw/agents/main/agent/models.json

# 测试 LLM 连通性
curl http://你的vLLM地址:端口/v1/models
```

### 问题 6: HTTP 400 错误（vLLM 调用失败）

**现象:** `400 status code (no body)`

**原因 A:** vLLM 未启用 tool calling 支持。OpenClaw 作为 agent 框架会自动发送 tools 参数。

**验证:**
```bash
curl http://vLLM地址:端口/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"模型名","messages":[{"role":"user","content":"hi"}],"tools":[{"type":"function","function":{"name":"test","description":"test","parameters":{"type":"object","properties":{}}}}]}'
```

如果报错 `enable-auto-tool-choice`，需要重启 vLLM 加参数：

```bash
vllm serve Qwen/Qwen3-14B --enable-auto-tool-choice --tool-call-parser hermes
```

**原因 B:** `openclaw.json` 中 `models.providers.vllm.api` 配置错误。

**注意：** OpenClaw 2026.2.26 版本支持的 api 类型为：`openai-completions`、`openai-responses`、`openai-codex-responses`、`anthropic-messages`、`google-generative-ai`、`github-copilot`、`bedrock-converse-stream`、`ollama`。vLLM 应使用 `openai-completions`（不是 `openai-chat-completions`，该选项在此版本中不存在）。

**验证配置：**
```bash
grep "api" ~/.openclaw/openclaw.json
```

### 问题 7: 飞书插件 duplicate plugin 警告

**现象:** `plugin feishu: duplicate plugin id detected`

**原因：** `~/.openclaw/extensions/feishu/` 和 npm 全局安装目录下各有一份 feishu 插件

**影响:** 不影响使用，可忽略。如需消除警告：
```bash
rm -rf /home/ryan/.npm-global/lib/node_modules/openclaw/extensions/feishu
openclaw gateway stop
openclaw gateway
```

## 关键配置文件路径

| 文件 | 路径 |
|------|------|
| 模型配置 | `~/.openclaw/agents/main/agent/models.json` |
| 认证信息 | `~/.openclaw/agents/main/agent/auth-profiles.json` |
| Gateway 日志 | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| 插件目录 | `~/.openclaw/extensions/` |

## 常用命令速查

```bash
openclaw gateway              # 启动 Gateway
openclaw gateway stop         # 停止 Gateway
openclaw tui                  # 终端聊天
openclaw dashboard --no-open  # 获取带 token 的 dashboard URL
openclaw doctor               # 健康检查
openclaw models list          # 查看模型配置
openclaw skills list          # 查看可用技能
openclaw configure --section model  # 重新配置模型
openclaw status               # 查看运行状态
openclaw --help               # 查看所有命令
```

## 飞书（Feishu）对接配置

### 1. 创建飞书应用

- 登录 [飞书开放平台](https://open.feishu.cn/app)，创建企业自建应用
- 在「凭证与基础信息」页面获取 App ID（`cli_xxx`）和 App Secret

### 2. 开启机器人能力

- 应用详情 → 添加应用能力 → 启用「机器人」
- 不开启会报错：`API error: app do not have bot`

### 3. 配置权限

在「权限管理」中开启以下权限：

- `im:message` — 获取与发送消息
- `im:message:send_as_bot` — 以机器人身份发送消息
- `im:message.p2p_msg:readonly` — 读取私聊消息
- `im:message.group_at_msg:readonly` — 接收群聊 @消息
- `im:resource` — 读取消息中的资源文件

### 4. 配置事件订阅

- 「事件与回调」→ 订阅方式选「使用长连接接收事件」
- 添加事件：`im.message.receive_v1`
- **注意：** gateway 必须在运行状态，否则长连接配置可能保存失败

### 5. 发布应用

- 「版本管理与发布」→ 创建版本 → 提交审批
- 审批通过后机器人才能在飞书客户端中使用

### 6. 配置 OpenClaw

```bash
openclaw channels add
# 选择 Feishu，输入 App ID 和 App Secret
```

或直接编辑 `~/.openclaw/openclaw.json`：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "dmPolicy": "allowlist",
      "allowFrom": ["ou_你的open_id"],
      "accounts": {
        "main": {
          "appId": "cli_xxx",
          "appSecret": "xxx"
        }
      }
    }
  }
}
```

### 7. 重启 Gateway 并测试

```bash
openclaw gateway stop
openclaw gateway
```

在飞书客户端搜索机器人名字，发消息测试。

### 常见问题

- **`app do not have bot`：** 飞书应用未开启机器人能力
- **`Access denied. scopes required: im:message`：** 权限未开启或未发布新版本
- **`getaddrinfo EAI_AGAIN open.feishu.cn`：** WSL DNS 问题，设置国内 DNS 后必须重启 Gateway：
  ```bash
  echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf
  openclaw gateway stop
  openclaw gateway
  ```
  永久解决见「问题 1: WSL 中 DNS 解析失败」
- **`access not configured` + pairing code：** 需要批准用户或改为 allowlist/open 模式

### DM 策略说明

| 值 | 行为 |
|---|------|
| `pairing` | 默认，未知用户需 pairing code 批准 |
| `allowlist` | 只允许 allowFrom 列表中的用户 |
| `open` | 允许所有用户（需设 `allowFrom: ["*"]`） |
| `disabled` | 禁用私聊 |

## Token 消耗说明

OpenClaw 每次请求会携带 system prompt + tools 定义 + 对话历史，首次对话即可能消耗 ~15k tokens。
128k 上下文窗口是输入+输出共享的总量，接近上限时 OpenClaw 会自动压缩历史对话。
使用本地 vLLM 时 token 不花钱，主要影响响应速度。
