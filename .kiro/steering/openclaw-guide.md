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

**现象:** `Temporary failure resolving 'archive.ubuntu.com'`

**原因:** WSL 的 DNS 配置不正确。

**解决:**
```bash
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
ping -c 3 archive.ubuntu.com  # 验证
```

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

### 问题 6: HTTP 400 错误（API 类型不匹配）

**现象:** `400 status code (no body)`

**原因 A:** models.json 中 `api` 设为 `openai-completions`，但 vLLM 提供的是 chat completions 接口。

**解决:**
```bash
sed -i 's/openai-completions/openai-chat-completions/g' ~/.openclaw/agents/main/agent/models.json
openclaw gateway stop
openclaw gateway
```

**原因 B:** vLLM 未启用 tool calling 支持。OpenClaw 作为 agent 框架会自动发送 tools 参数。

**验证:**
```bash
curl http://vLLM地址:端口/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"模型名","messages":[{"role":"user","content":"hi"}],"tools":[{"type":"function","function":{"name":"test","description":"test","parameters":{"type":"object","properties":{}}}}]}'
```

如果报错 `"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set`，需要重启 vLLM：

```bash
vllm serve Qwen/Qwen3-14B --enable-auto-tool-choice --tool-call-parser hermes
```

### 问题 7: 飞书插件 duplicate plugin 警告

**现象:** `plugin feishu: duplicate plugin id detected`

**影响:** 不影响使用，可忽略。如需消除，检查 `~/.openclaw/extensions/` 和全局安装目录是否有重复的 feishu 插件。

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

## Token 消耗说明

OpenClaw 每次请求会携带 system prompt + tools 定义 + 对话历史，首次对话即可能消耗 ~15k tokens。
128k 上下文窗口是输入+输出共享的总量，接近上限时 OpenClaw 会自动压缩历史对话。
使用本地 vLLM 时 token 不花钱，主要影响响应速度。
