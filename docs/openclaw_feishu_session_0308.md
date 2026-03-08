# OpenClaw 对接飞书 Session 2026-03-08

## 本次目标

在已安装好 OpenClaw 的 WSL 环境中，配置飞书（Feishu）channel 并解决启动过程中遇到的问题。

## 环境信息

| 项目 | 值 |
|------|------|
| 系统 | WSL2 Ubuntu (P184) |
| 用户 | leo |
| OpenClaw 版本 | 2026.3.2 (85377a2) |
| Node.js | v22.x |

## Channel 配置方法

### 方式一：交互式配置（推荐）

```bash
openclaw channels add
```

按提示选择 Feishu，依次输入 Domain、App ID、App Secret、DM Policy。

### 方式二：直接编辑配置文件

编辑 `~/.openclaw/openclaw.json`，在 `channels` 下添加：

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

配置完成后重启 Gateway：

```bash
openclaw gateway stop
openclaw gateway
```

### DM 策略说明

| 策略 | 行为 |
|------|------|
| `pairing` | 默认，新用户需 pairing code 批准 |
| `allowlist` | 只允许 `allowFrom` 列表中的用户 |
| `open` | 允许所有人（需设 `allowFrom: ["*"]`） |
| `disabled` | 禁用私聊 |

## 遇到的问题与解决

### 问题 1: Gateway 启动报 "already running"

**现象：**

```
Gateway failed to start: gateway already running (pid 184); lock timeout after 5000ms
```

**原因：** 之前的 Gateway 进程还在运行，`openclaw gateway stop` 无法正常停止。

**解决：** 直接杀进程：

```bash
kill 184
# 如果 kill 不管用，强制杀：
kill -9 184
```

杀掉后再启动：

```bash
openclaw gateway
```

### 问题 2: systemctl is-enabled 报错

**现象：**

```
Gateway service check failed: Error: systemctl is-enabled unavailable
```

**原因：** WSL 中 systemd 支持不完整，不影响 Gateway 正常运行，可以忽略。

### 问题 3: 飞书插件重复警告

**现象：**

```
plugin feishu: duplicate plugin id detected; later plugin may be overridden
(/home/leo/.openclaw/extensions/feishu/index.ts)
```

**原因：** `~/.openclaw/extensions/feishu/` 和 npm 全局安装目录下各有一份 feishu 插件。

**影响：** 不影响使用，可忽略。如需消除警告：

```bash
rm -rf /home/leo/.npm-global/lib/node_modules/openclaw/extensions/feishu
openclaw gateway stop
openclaw gateway
```

### 问题 4: groupPolicy allowlist 但 allowFrom 为空

**现象：**

```
channels.feishu.groupPolicy is "allowlist" but groupAllowFrom (and allowFrom) is empty
— all group messages will be silently dropped.
```

**原因：** 群聊策略设为 allowlist 但没有配置允许的发送者，所有群聊消息会被丢弃。

**解决：**

如果需要群聊功能，编辑 `~/.openclaw/openclaw.json`：

```json
{
  "channels": {
    "feishu": {
      "groupPolicy": "open",
      "groupAllowFrom": ["*"]
    }
  }
}
```

如果只用私聊不用群聊，可以忽略此警告。

## 飞书侧前置配置（必须先完成）

1. 登录 [飞书开放平台](https://open.feishu.cn/app)，创建企业自建应用
2. 获取 App ID（`cli_xxx`）和 App Secret
3. 应用详情 → 添加应用能力 → 启用「机器人」
4. 权限管理中开启：`im:message`、`im:message:send_as_bot`、`im:message.p2p_msg:readonly`、`im:message.group_at_msg:readonly`、`im:resource`
5. 事件与回调 → 订阅方式选「使用长连接接收事件」→ 添加事件 `im.message.receive_v1`
6. 版本管理与发布 → 创建版本 → 提交审批 → 审批通过后生效

> ⚠️ 配置长连接时 Gateway 必须在运行状态，否则可能保存失败。

## 本次 Session 要点总结

| 项目 | 内容 |
|------|------|
| 配置方式 | `openclaw channels add` 或直接编辑 `openclaw.json` |
| 问题 1 | Gateway 进程卡住，`kill <pid>` 强制停止 |
| 问题 2 | WSL 中 systemctl 报错，不影响使用，忽略 |
| 问题 3 | 飞书插件重复，删除全局目录下的副本可消除 |
| 问题 4 | 群聊 allowlist 为空，改 `groupPolicy` 为 `open` 或忽略 |
| 关键提醒 | 改完配置后必须 `openclaw gateway stop` 再 `openclaw gateway` |
