# OpenClaw Session 2026-03-08 — 模型配置修复与常见误区

## 问题 1: Gateway 启动报 Model "1" 错误

### 现象

```
[model-selection] Model "1" specified without provider. Falling back to "anthropic/1". Please use "anthropic/1" in your config.
[gateway] agent model: anthropic/1
```

### 原因

`~/.openclaw/openclaw.json` 中模型配置不正确，`agents.defaults` 部分如下：

```json
"agents": {
  "defaults": {
    "model": {
      "primary": "1"
    },
    "models": {
      "1": {}
    }
  }
}
```

模型名写成了 `"1"`，且 `"1": {}` 内容为空，没有指定 provider、baseUrl 等信息。OpenClaw 无法识别，默认 fallback 到 `anthropic/1`。

### 解决

将模型配置改为正确的格式。例如使用本地 vLLM：

```json
"agents": {
  "defaults": {
    "model": {
      "primary": "vllm/Qwen/Qwen3-14B"
    },
    "models": {
      "vllm/Qwen/Qwen3-14B": {
        "provider": "vllm",
        "api": "openai-completions",
        "baseUrl": "http://你的vLLM地址:端口/v1"
      }
    }
  }
}
```

也可以用交互式命令重新配置：

```bash
openclaw configure --section model
```

配置完成后重启 Gateway：

```bash
openclaw gateway stop
openclaw gateway
```

### 修复结果

配置为 `zai/glm-5` 后，Gateway 正常启动：

```
[gateway] agent model: zai/glm-5
[gateway] listening on ws://127.0.0.1:18789, ws://[::1]:18789 (PID 2123)
```

---

## 问题 2: Windows PowerShell 中运行 openclaw 报 "无法识别"

### 现象

```
PS C:\Mac\Home\Desktop> openclaw
openclaw : 无法将"openclaw"项识别为 cmdlet、函数、脚本文件或可运行程序的名称。
```

### 原因

OpenClaw 安装在 WSL (Linux) 环境中，Windows 原生 PowerShell 找不到该命令。

### 解决

所有 `openclaw` 命令必须在 WSL 终端中运行。在 PowerShell 中先进入 WSL：

```powershell
wsl
```

然后再执行 `openclaw` 相关命令。或者直接使用已经打开的 WSL 终端窗口。

---

## 问题 3: 更换模型后 tui 仍显示旧模型

### 现象

Gateway 启动日志已显示新模型：

```
[gateway] agent model: zai/glm-4.5-air
```

但 `openclaw tui` 底部状态栏仍显示旧模型：

```
agent main | session main (openclaw-tui) | zai/glm-5 | think low | tokens 7.6k/205k (4%)
```

### 原因

tui 的 session 会记住之前使用的模型。更改 `openclaw.json` 中的模型配置后，已存在的 session 不会自动切换，需要手动重置。

### 解决

在 tui 中输入：

```
/reset
```

或者退出 tui 后清除 session 再重新进入：

```bash
openclaw sessions clear
openclaw tui
```

重置后状态栏会显示新配置的模型。

---

## 问题 4: 浏览器访问 Dashboard 报 unauthorized

### 现象

浏览器打开 `http://127.0.0.1:18789/` 显示：

```
unauthorized: gateway token missing (open the dashboard URL and paste the token in Control UI settings)
```

### 原因

OpenClaw Dashboard 需要 token 认证，直接访问 IP:端口 不带 token 会被拒绝。

### 解决

在 WSL 终端中获取带 token 的完整 URL：

```bash
openclaw dashboard --no-open
```

复制输出的完整 URL（含 `#token=...`）到浏览器打开。

### 补充：WSL 中 127.0.0.1 无法访问

如果 Windows 浏览器打不开 `127.0.0.1:18789`，是因为 WSL 和 Windows 的 localhost 不互通。在 WSL 中获取实际 IP：

```bash
hostname -I
```

用输出的 IP（如 `172.x.x.x`）替换 URL 中的 `127.0.0.1`。

### 补充：端口 18791 不是 Dashboard

`http://127.0.0.1:18791/` 是 Browser Control 服务（OpenClaw agent 控制浏览器的内部接口），不是管理面板。Dashboard 端口是 18789。

---

## 模型更换方法速查

### 方式一：交互式配置（推荐）

```bash
openclaw configure --section model
```

### 方式二：直接编辑配置文件

```bash
nano ~/.openclaw/openclaw.json
```

修改 `agents.defaults.model.primary` 和 `agents.defaults.models` 对象。

### 方式三：查看当前模型

```bash
openclaw models list
```

### 注意事项

- 改完配置后必须重启 Gateway：`openclaw gateway stop && openclaw gateway`
- 已有的 tui session 需要 `/reset` 才会使用新模型
- vLLM 的 api 类型应为 `openai-completions`（不是 `openai-chat-completions`）

---

## 本次 Session 要点总结

| 项目 | 内容 |
|------|------|
| 问题 1 | 模型配置为 `"1"`，Gateway 无法识别 |
| 修复 1 | 通过 `openclaw configure --section model` 配置正确的模型 |
| 问题 2 | Windows PowerShell 不能直接跑 `openclaw` |
| 修复 2 | 需先 `wsl` 进入 WSL 环境 |
| 问题 3 | 换模型后 tui 仍显示旧模型 (zai/glm-5) |
| 修复 3 | 在 tui 中 `/reset` 或 `openclaw sessions clear` |
| 问题 4 | 浏览器访问 Dashboard 报 unauthorized / token missing |
| 修复 4 | 用 `openclaw dashboard --no-open` 获取带 token 的 URL |
| 注意 | 端口 18791 是 Browser Control，不是 Dashboard（用 18789） |
| 最终状态 | Gateway: zai/glm-4.5-air，tui 需 reset 后生效 |
