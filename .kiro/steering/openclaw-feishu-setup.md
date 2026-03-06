# OpenClaw 对接飞书完整指南

本文档记录了将 OpenClaw AI Agent 与飞书（Feishu）连接的完整过程，包括踩过的坑和解决方案。

## 架构概览

```
飞书客户端 ←→ 飞书开放平台 ←→(WebSocket长连接)←→ OpenClaw Gateway ←→ vLLM (Qwen3-14B)
```

- OpenClaw 通过飞书 WebSocket 长连接接收消息，无需公网 IP 或 webhook
- Gateway 将消息转发给本地 vLLM 大模型处理，再将回复发回飞书

## 前置条件

- WSL2 + Ubuntu（Windows 原生支持不稳定）
- Node.js 22+（Ubuntu apt 源只有 18.x，需用 NodeSource 源）
- OpenClaw 已安装并能正常运行（`openclaw tui` 能聊天）
- vLLM 已部署并可访问（如 `http://109.254.2.180:8024/v1`）

## 第一步：创建飞书应用

1. 登录 [飞书开放平台](https://open.feishu.cn/app)
2. 点击「创建企业自建应用」，填写名称和描述
3. 进入应用详情 →「凭证与基础信息」，记下 **App ID**（`cli_xxx`）和 **App Secret**

## 第二步：开启机器人能力

1. 应用详情 → 左侧菜单「添加应用能力」
2. 启用「机器人」，设置机器人名称

> ⚠️ 不开启机器人能力会报错：`API error: app do not have bot`

## 第三步：配置权限

在「权限管理」中开启以下权限：

| 权限 | 说明 |
|------|------|
| `im:message` | 获取与发送单聊、群组消息 |
| `im:message:send_as_bot` | 以机器人身份发送消息 |
| `im:message.p2p_msg:readonly` | 读取用户发给机器人的单聊消息 |
| `im:message.group_at_msg:readonly` | 接收群聊中 @机器人的消息 |
| `im:resource` | 读取消息中的资源文件 |

> ⚠️ 缺少 `im:message` 权限会报错：`Access denied. scopes required: [im:message]`

## 第四步：配置事件订阅

1. 左侧菜单 →「事件与回调」
2. 订阅方式选择「**使用长连接接收事件/回调**」（WebSocket 模式）
3. 添加事件：`im.message.receive_v1`（接收消息）

> ⚠️ 配置长连接时 OpenClaw Gateway 必须在运行状态，否则可能保存失败

## 第五步：发布应用

1. 左侧菜单 →「版本管理与发布」
2. 创建版本，填写版本号和更新说明
3. 提交审批，等待管理员通过
4. 审批通过后，机器人才会出现在飞书客户端中

## 第六步：配置 OpenClaw

### 方式一：交互式配置（推荐）

```bash
openclaw channels add
```

选择 Feishu，按提示输入：
- Domain：Feishu (feishu.cn)
- App ID
- App Secret
- DM Policy（建议选 allowlist）

### 方式二：直接编辑配置文件

编辑 `~/.openclaw/openclaw.json`：

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
          "appSecret": "你的secret"
        }
      }
    }
  }
}
```

### DM 策略说明

| 策略 | 行为 |
|------|------|
| `pairing` | 默认，新用户需要 pairing code 批准 |
| `allowlist` | 只允许 `allowFrom` 列表中的用户（推荐） |
| `open` | 允许所有人（需设 `allowFrom: ["*"]`） |
| `disabled` | 禁用私聊 |

## 第七步：重启 Gateway 并测试

```bash
openclaw gateway stop
openclaw gateway
```

启动后观察日志，确认以下关键信息：
- `bot open_id resolved: ou_xxx` — 机器人身份识别成功
- `WebSocket client started` — 长连接启动
- `ws client ready` — 连接就绪

然后在飞书客户端搜索机器人名字，发消息测试。

## 踩坑记录

### 1. WSL DNS 解析失败（飞书消息无回复）

**现象：** 
- 飞书发消息后无回复，日志中出现 `getaddrinfo EAI_AGAIN open.feishu.cn`
- 或者 Gateway 启动时 WebSocket 连接正常（`ws client ready`），但发消息后日志无任何新内容
- `ping open.feishu.cn` 可能通，但 Node.js 进程仍然解析失败（因为 Gateway 启动时缓存了旧的 DNS 配置）

**原因：** WSL 默认 DNS 配置不正确，且 8.8.8.8 在国内可能被墙

**排查步骤：**
1. 先用 `openclaw tui` 测试模型是否正常（排除模型问题）
2. 发飞书消息后查看日志：`tail -n 20 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log`
3. 如果日志中有 `EAI_AGAIN` 错误，确认是 DNS 问题

**解决：**
```bash
# 设置国内 DNS
echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf

# 重要：修改 DNS 后必须重启 Gateway，否则 Node.js 进程还用旧的 DNS
openclaw gateway stop
openclaw gateway
```

**永久解决（防止 WSL 重启后 DNS 被重置）：**
```bash
# 禁止 WSL 自动生成 resolv.conf
sudo bash -c 'echo -e "[network]\ngenerateResolvConf = false" > /etc/wsl.conf'

# 设置 DNS
echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf
```

> ⚠️ 关键点：修改 DNS 后必须重启 Gateway，`ping` 通不代表 Gateway 进程能解析，因为 Node.js 可能缓存了旧的 DNS 结果。

### 2. `app do not have bot`

**原因：** 飞书应用未开启机器人能力

**解决：** 应用详情 → 添加应用能力 → 启用「机器人」

### 3. `Access denied. scopes required: [im:message]`

**原因：** 权限未开启，或开启后未发布新版本

**解决：** 开启权限后必须创建新版本并发布审批

### 4. `access not configured` + pairing code 循环

**现象：** 每次发消息都回复 pairing code，approve 后仍然不生效

**原因：** pairing code 会频繁刷新，approve 的可能已经过期

**解决：** 
- 先 `openclaw pairing list feishu` 查看最新的 code
- 用最新的 code 执行 `openclaw pairing approve feishu <CODE>`
- 或者直接改用 allowlist 模式绕过 pairing：
  ```bash
  openclaw config set channels.feishu.dmPolicy "allowlist"
  openclaw config set channels.feishu.allowFrom '["ou_你的open_id"]'
  ```

### 5. HTTP 400 错误（vLLM 调用失败）

**现象：** `HTTP 400: status code (no body)`，`openclaw tui` 中发消息报错

**原因 A：** vLLM 未启用 tool calling 支持。OpenClaw 作为 agent 框架会自动发送 tools 参数。

**验证：**
```bash
curl http://你的vLLM地址:端口/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen3-14B","messages":[{"role":"user","content":"hi"}],"tools":[{"type":"function","function":{"name":"test","description":"test","parameters":{"type":"object","properties":{}}}}]}'
```

如果报错 `enable-auto-tool-choice`，需要重启 vLLM 加参数：
```bash
vllm serve Qwen/Qwen3-14B --enable-auto-tool-choice --tool-call-parser hermes
```

**原因 B：** `openclaw.json` 中 `models.providers.vllm.api` 配置错误。

**注意：** OpenClaw 2026.2.26 版本支持的 api 类型为：`openai-completions`、`openai-responses`、`openai-codex-responses`、`anthropic-messages`、`google-generative-ai`、`github-copilot`、`bedrock-converse-stream`、`ollama`。vLLM 应使用 `openai-completions`（不是 `openai-chat-completions`，该选项在此版本中不存在）。

**验证配置：**
```bash
grep "api" ~/.openclaw/openclaw.json
```

### 6. 飞书插件重复警告

**现象：** `plugin feishu: duplicate plugin id detected`

**原因：** `~/.openclaw/extensions/feishu/` 和 npm 全局安装目录下各有一份 feishu 插件

**影响：** 通常不影响使用，可忽略。如需消除警告：
```bash
# 删除全局安装目录下的重复插件
rm -rf /home/ryan/.npm-global/lib/node_modules/openclaw/extensions/feishu
openclaw gateway stop
openclaw gateway
```

### 7. 连续发消息导致 agent terminated

**现象：** 
- 短时间内连续发多条消息，只有第一条有回复，后续消息 `replies=0`
- 日志中出现 `isError=true error=terminated`
- 之后 WebSocket 断开重连（`[ws] reconnect`），重连后的消息也无回复

**原因：** agent 还在处理前一条消息时，新消息进来会被排队或丢弃。如果处理时间过长，可能触发超时导致 agent 被 terminate，进而引发 WebSocket 重连。

**解决：** 发完一条消息后等它回复了再发下一条，不要连续发。Qwen3-14B 本地推理一次可能需要几十秒到一两分钟。

### 8. Qwen3 thinking 模式导致回复异常

**现象：** 
- agent 运行后 `isError=true error=terminated`
- 直接 curl vLLM 正常，但通过 OpenClaw 调用失败
- vLLM 返回的内容包含 `<think>...</think>` 标签

**原因：** Qwen3 默认开启 thinking 模式，会在回复中输出 `<think>` 思考过程。当 OpenClaw 同时发送 tools 参数时，thinking + tool calling 的响应格式可能导致解析异常。

**排查：**
```bash
# 直接测试 vLLM 是否带 thinking
curl http://你的vLLM地址:端口/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen3-14B","messages":[{"role":"user","content":"hello"}]}'
```

如果返回中有 `<think>` 标签，说明 thinking 模式开启了。

**解决方案：**
- 在 `openclaw.json` 模型配置中确认 `"reasoning": false`
- 如果模型仍然输出 thinking，可以在 vLLM 启动时使用不带 thinking 的 chat template
- 或者在 vLLM 请求中加 `"chat_template_kwargs": {"enable_thinking": false}` 来禁用

## 使用方式

连接成功后，直接在飞书里给机器人发消息即可，就像跟人聊天一样。

内置命令：
- `/status` — 查看机器人状态
- `/reset` — 重置对话（清空上下文）
- `/model` — 查看或切换模型

## 关键文件路径

| 文件 | 路径 |
|------|------|
| OpenClaw 主配置 | `~/.openclaw/openclaw.json` |
| 模型配置 | `~/.openclaw/agents/main/agent/models.json` |
| 认证信息 | `~/.openclaw/agents/main/agent/auth-profiles.json` |
| Gateway 日志 | `/tmp/openclaw/openclaw-YYYY-MM-DD.log` |
| 飞书插件目录 | `~/.openclaw/extensions/feishu/` |
