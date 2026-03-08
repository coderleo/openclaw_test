# OpenClaw 中国用户一键安装向导 — 设计文档

## 产品定位

纯前端静态 Web 应用，面向中国社区用户。通过步骤式问答收集用户环境和需求，生成定制化 Bash 安装脚本（Windows 用户额外生成 PowerShell 脚本）。覆盖从零开始的完整链路：WSL 安装 → DNS 修复 → Node.js 22 → OpenClaw → 模型配置 → 飞书对接。

## 目标用户

中国开发者社区，对 Linux/WSL 不一定熟悉，需要一个傻瓜式的引导流程。

## 技术栈

- 纯前端：HTML + CSS + JavaScript（无框架）
- 部署：GitHub Pages / Vercel（零后端、零成本）
- 风格：深色主题，OpenClaw coral 配色（#ff4d4d 主色、#00e5cc 成功色、#8892b0 次要文字）

## 用户流程（7 步向导）

### Step 1 — 选择操作系统

选项：
- Windows（需要 WSL）
- macOS
- Linux（原生）

选完后自动决定后续哪些步骤展示。

### Step 2 — 环境准备（根据 OS 动态）

- Windows：WSL2 安装 + Ubuntu 安装 + DNS 修复
  - 生成 PowerShell 脚本（WSL 安装在 Windows 侧执行）
  - 生成 Bash 脚本（DNS 修复在 WSL 内执行）
  - 处理 `WININET_E_NAME_NOT_RESOLVED` 问题（winget 备选方案）
- macOS：Homebrew 检测提示
- Linux：DNS 修复（可选，勾选"国内网络环境"时启用）

### Step 3 — Node.js 22 安装

- Windows/Linux：NodeSource 源方式
  ```bash
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt install -y nodejs
  ```
- macOS：`brew install node@22`

### Step 4 — OpenClaw 安装

- npm 镜像源切换（国内用 npmmirror）
  ```bash
  npm config set registry https://registry.npmmirror.com
  ```
- 安装 OpenClaw
  ```bash
  curl -fsSL https://openclaw.ai/install.sh | bash
  ```
- PATH 配置
  ```bash
  export PATH="$(npm prefix -g)/bin:$PATH"
  echo 'export PATH="$(npm prefix -g)/bin:$PATH"' >> ~/.bashrc
  ```
- Onboarding（跳过交互式向导，用脚本直接写配置）

### Step 5 — 模型配置

用户选择 LLM 提供商：
- 本地 vLLM — 需填 Base URL、模型名
- Anthropic — 需填 API Key
- OpenAI — 需填 API Key
- 智谱（ZhipuAI）— 需填 API Key、模型名
- Ollama — 需填 Base URL、模型名

根据选择生成 `openclaw.json` 模型配置片段，写入 `~/.openclaw/openclaw.json`。

vLLM 示例配置：
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "vllm/Qwen/Qwen3-14B"
      },
      "models": {
        "vllm/Qwen/Qwen3-14B": {
          "provider": "vllm",
          "api": "openai-completions",
          "baseUrl": "http://地址:端口/v1"
        }
      }
    }
  }
}
```

注意：vLLM 的 api 类型必须是 `openai-completions`（不是 `openai-chat-completions`）。

### Step 6 — 飞书对接（可选，可跳过）

分两部分：

A. 图文引导（网页内展示，不生成脚本）：
1. 创建飞书企业自建应用
2. 开启机器人能力
3. 配置权限（im:message 等 5 项）
4. 配置事件订阅（长连接 + im.message.receive_v1）
5. 发布应用并审批

B. 配置生成（用户填入后生成脚本）：
- App ID（cli_xxx）
- App Secret
- Open ID（ou_xxx，用于 allowlist）
- DM 策略选择（pairing / allowlist / open）

生成飞书 channel 配置写入 `openclaw.json`。

### Step 7 — 生成脚本 & 完成

- 汇总所有选择，拼接完整安装脚本
- 一键复制按钮
- 脚本特性：
  - `set -euo pipefail` 严格模式
  - 彩色状态输出（参考官方 install.sh 的配色）
  - 每步有进度提示
  - 失败时给出明确错误提示和修复建议
  - 自动重试网络请求
- 附带常见问题速查表

## 页面布局

单页应用：
- 左侧：步骤导航条（显示步骤名称和完成状态）
- 右侧：当前步骤内容区（表单/选项/说明）
- 底部：上一步 / 下一步按钮
- 用户可来回切换步骤修改选择

## 项目结构

```
openclaw-installer/
├── index.html          # 单页应用入口
├── style.css           # 深色主题样式
├── app.js              # 步骤管理、表单收集、脚本生成
└── README.md           # 项目说明
```

脚本生成逻辑全在 app.js 中，用模板字符串 + 占位符替换。不需要单独的脚本模板文件，保持简单。

## 脚本生成逻辑

每个安装阶段对应一个生成函数：
- `generateWSLScript()` → PowerShell 脚本
- `generateDNSScript()` → Bash
- `generateNodeScript()` → Bash
- `generateOpenClawScript()` → Bash
- `generateModelConfig()` → Bash（写 JSON 到 openclaw.json）
- `generateFeishuConfig()` → Bash（写 JSON 到 openclaw.json）
- `generateStartupScript()` → Bash（gateway 启动 + doctor 验证）

最终 `generateFullScript()` 按用户选择拼接上述片段。

## 安全考虑

- 纯静态站，无后端，无数据收集
- API Key / App Secret 只在浏览器本地处理，不发送到任何服务器
- 生成的脚本包含敏感信息，页面醒目提示："脚本包含你的密钥，请勿分享给他人"

## 国内网络优化

- DNS：默认使用阿里 DNS（223.5.5.5）和 114 DNS（114.114.114.114）
- npm：自动切换到 npmmirror 镜像源
- WSL Ubuntu 安装：提供 winget 备选方案绕过 GitHub 连接问题
- NodeSource：如果 curl 失败，提示手动下载方案

## 常见问题覆盖

脚本和网页都会覆盖以下已知问题：
- WSL DNS 解析失败（Temporary failure resolving）
- npm ECONNRESET（国内网络）
- openclaw command not found（PATH 问题）
- Dashboard unauthorized（token 问题）
- WSL 中 127.0.0.1 不可访问（需用 hostname -I 获取实际 IP）
- 飞书 app do not have bot（未开启机器人能力）
- vLLM HTTP 400（未启用 tool calling 或 api 类型错误）
- 飞书插件 duplicate 警告（可忽略）
