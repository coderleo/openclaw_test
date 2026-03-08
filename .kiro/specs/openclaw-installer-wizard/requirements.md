# 需求文档

## 简介

OpenClaw 中国用户一键安装向导是一个纯前端静态 Web 应用，面向中国社区用户。通过 7 步向导式问答收集用户的操作系统、网络环境和需求，生成定制化的 Bash 安装脚本（Windows 用户额外生成 PowerShell 脚本）。覆盖从零开始的完整安装链路：WSL 安装 → DNS 修复 → Node.js 22 → OpenClaw → 模型配置 → 飞书对接。

应用采用深色主题、OpenClaw coral 配色，部署于 GitHub Pages 或 Vercel，无后端、无数据收集。

## 术语表

- **Wizard（向导）**: 步骤式引导界面，用户逐步填写信息，最终生成安装脚本
- **Step（步骤）**: 向导中的一个页面，对应安装流程的一个阶段
- **StepNavigator（步骤导航器）**: 页面左侧的导航条组件，显示所有步骤名称和完成状态
- **ContentArea（内容区）**: 页面右侧的主内容区域，展示当前步骤的表单和说明
- **ScriptGenerator（脚本生成器）**: 根据用户选择拼接安装脚本的 JavaScript 模块
- **ConfigSnippet（配置片段）**: 生成的 JSON 配置内容，用于写入 OpenClaw 配置文件
- **CopyButton（复制按钮）**: 一键复制脚本到剪贴板的按钮组件
- **WSL**: Windows Subsystem for Linux，Windows 上运行 Linux 的子系统
- **NodeSource**: 提供最新 Node.js 安装包的第三方 apt 源
- **npmmirror**: npm 国内镜像源（registry.npmmirror.com）
- **vLLM**: 高性能 LLM 推理服务框架
- **OpenClaw**: 开源自主 AI agent 框架，通过消息平台交互
- **Feishu（飞书）**: 字节跳动的企业协作平台，OpenClaw 支持的消息渠道之一

## 需求

### 需求 1：向导整体布局与导航

**用户故事：** 作为中国社区用户，我希望看到一个清晰的步骤式引导界面，以便我能了解安装进度并在步骤间自由切换。

#### 验收标准

1. THE Wizard SHALL 以单页应用形式呈现，左侧为 StepNavigator，右侧为 ContentArea，底部为导航按钮区
2. THE StepNavigator SHALL 显示全部 7 个步骤的名称和完成状态（未开始、进行中、已完成）
3. WHEN 用户点击"下一步"按钮，THE Wizard SHALL 切换到下一个步骤并更新 StepNavigator 的状态
4. WHEN 用户点击"上一步"按钮，THE Wizard SHALL 切换到上一个步骤，保留已填写的数据
5. WHEN 用户点击 StepNavigator 中已完成的步骤，THE Wizard SHALL 跳转到该步骤并保留所有已填写的数据
6. THE Wizard SHALL 使用深色主题，主色为 OpenClaw coral（#ff4d4d），成功色为 #00e5cc，次要文字色为 #8892b0
7. THE Wizard SHALL 使用纯 HTML + CSS + JavaScript 实现，不依赖任何前端框架

### 需求 2：操作系统选择（Step 1）

**用户故事：** 作为用户，我希望选择我的操作系统，以便向导为我生成适合的安装脚本。

#### 验收标准

1. THE Wizard SHALL 在 Step 1 提供三个操作系统选项：Windows（需要 WSL）、macOS、Linux（原生）
2. WHEN 用户选择 Windows，THE Wizard SHALL 在后续步骤中包含 WSL 安装和 DNS 修复步骤
3. WHEN 用户选择 macOS，THE Wizard SHALL 在后续步骤中跳过 WSL 安装，使用 Homebrew 方式安装 Node.js
4. WHEN 用户选择 Linux，THE Wizard SHALL 在后续步骤中跳过 WSL 安装，提供可选的 DNS 修复
5. THE Wizard SHALL 在用户选择操作系统后才允许进入下一步

### 需求 3：环境准备（Step 2）

**用户故事：** 作为 Windows 用户，我希望获得 WSL 安装和 DNS 修复的引导脚本，以便我能在 Windows 上运行 OpenClaw。

#### 验收标准

1. WHEN 用户在 Step 1 选择 Windows，THE ScriptGenerator SHALL 生成 PowerShell 脚本，包含 WSL 功能启用（`wsl --install`）和 Ubuntu 安装（`winget install Canonical.Ubuntu.2404` 作为备选方案）
2. WHEN 用户在 Step 1 选择 Windows，THE ScriptGenerator SHALL 生成 Bash 脚本，包含 DNS 修复（设置阿里 DNS 223.5.5.5 和 114 DNS 114.114.114.114）和永久生效配置（写入 /etc/wsl.conf）
3. WHEN 用户在 Step 1 选择 Linux，THE Wizard SHALL 提供"国内网络环境"勾选项，勾选后生成 DNS 修复脚本
4. WHEN 用户在 Step 1 选择 macOS，THE Wizard SHALL 显示 Homebrew 检测提示信息
5. THE ContentArea SHALL 对 Windows 用户分别标注哪些命令在 PowerShell 中执行、哪些在 WSL 终端中执行

### 需求 4：Node.js 22 安装（Step 3）

**用户故事：** 作为用户，我希望获得正确安装 Node.js 22 的脚本，因为 OpenClaw 要求 Node.js 22 或更高版本。

#### 验收标准

1. WHEN 用户在 Step 1 选择 Windows 或 Linux，THE ScriptGenerator SHALL 生成通过 NodeSource 源安装 Node.js 22 的 Bash 脚本（`curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -` 和 `sudo apt install -y nodejs`）
2. WHEN 用户在 Step 1 选择 macOS，THE ScriptGenerator SHALL 生成通过 Homebrew 安装 Node.js 22 的脚本（`brew install node@22`）
3. THE ScriptGenerator SHALL 在 Node.js 安装脚本中包含版本验证命令（`node -v` 和 `npm -v`）
4. THE ContentArea SHALL 说明为什么不能直接使用 `apt install nodejs`（Ubuntu 官方源只有 18.x）

### 需求 5：OpenClaw 安装（Step 4）

**用户故事：** 作为中国用户，我希望安装脚本自动处理国内网络问题，以便我能顺利安装 OpenClaw。

#### 验收标准

1. THE ScriptGenerator SHALL 在 OpenClaw 安装脚本中先切换 npm 镜像源为 npmmirror（`npm config set registry https://registry.npmmirror.com`）
2. THE ScriptGenerator SHALL 生成 OpenClaw 安装命令（`curl -fsSL https://openclaw.ai/install.sh | bash`）
3. THE ScriptGenerator SHALL 在安装脚本中包含 PATH 配置（将 npm 全局目录加入 PATH 并写入 ~/.bashrc）
4. THE ContentArea SHALL 提示用户安装完成后运行 `openclaw doctor` 验证安装

### 需求 6：模型配置（Step 5）

**用户故事：** 作为用户，我希望选择我的 LLM 提供商并填入连接信息，以便向导为我生成正确的模型配置。

#### 验收标准

1. THE Wizard SHALL 在 Step 5 提供以下 LLM 提供商选项：本地 vLLM、Anthropic、OpenAI、智谱（ZhipuAI）、Ollama
2. WHEN 用户选择本地 vLLM，THE Wizard SHALL 要求填写 Base URL 和模型名称，并生成 api 类型为 `openai-completions` 的配置
3. WHEN 用户选择 Anthropic 或 OpenAI，THE Wizard SHALL 要求填写 API Key
4. WHEN 用户选择智谱（ZhipuAI），THE Wizard SHALL 要求填写 API Key 和模型名称
5. WHEN 用户选择 Ollama，THE Wizard SHALL 要求填写 Base URL 和模型名称
6. THE ScriptGenerator SHALL 根据用户选择生成写入 `~/.openclaw/openclaw.json` 的模型配置 Bash 脚本
7. IF 用户选择 vLLM 但 api 类型填写为 `openai-chat-completions`，THEN THE Wizard SHALL 显示警告提示正确的 api 类型为 `openai-completions`

### 需求 7：飞书对接（Step 6，可选）

**用户故事：** 作为用户，我希望获得飞书对接的完整引导，以便我能让 OpenClaw 通过飞书接收和回复消息。

#### 验收标准

1. THE Wizard SHALL 在 Step 6 提供"跳过飞书配置"选项，允许用户跳过此步骤
2. THE ContentArea SHALL 以图文形式展示飞书应用创建的完整步骤：创建企业自建应用、开启机器人能力、配置 5 项权限（im:message、im:message:send_as_bot、im:message.p2p_msg:readonly、im:message.group_at_msg:readonly、im:resource）、配置事件订阅（长连接 + im.message.receive_v1）、发布应用并审批
3. WHEN 用户选择配置飞书，THE Wizard SHALL 要求填写 App ID（cli_xxx 格式）、App Secret、Open ID（ou_xxx 格式）
4. THE Wizard SHALL 提供 DM 策略选择：pairing（默认）、allowlist（推荐）、open
5. THE ScriptGenerator SHALL 根据用户填写的信息生成飞书 channel 配置写入 `~/.openclaw/openclaw.json` 的 Bash 脚本
6. THE ContentArea SHALL 提醒用户配置长连接时 Gateway 必须在运行状态

### 需求 8：脚本生成与输出（Step 7）

**用户故事：** 作为用户，我希望获得一个完整的、可直接执行的安装脚本，以便我能一键完成所有安装配置。

#### 验收标准

1. THE ScriptGenerator SHALL 汇总用户在所有步骤中的选择，拼接生成完整的 Bash 安装脚本
2. WHEN 用户在 Step 1 选择 Windows，THE ScriptGenerator SHALL 额外生成一个 PowerShell 脚本用于 WSL 安装
3. THE ScriptGenerator SHALL 生成的 Bash 脚本包含 `set -euo pipefail` 严格模式
4. THE ScriptGenerator SHALL 生成的脚本包含彩色状态输出（参考 OpenClaw 官方 install.sh 的配色：coral #ff4d4d、cyan #00e5cc、amber 警告色）
5. THE ScriptGenerator SHALL 生成的脚本在每个安装阶段包含进度提示
6. IF 脚本执行中某步骤失败，THEN THE ScriptGenerator 生成的脚本 SHALL 输出明确的错误提示和修复建议
7. THE Wizard SHALL 提供 CopyButton，点击后将脚本内容复制到剪贴板
8. WHEN 用户点击 CopyButton，THE Wizard SHALL 显示复制成功的视觉反馈
9. THE ContentArea SHALL 在脚本输出区域醒目提示："脚本包含你的密钥，请勿分享给他人"

### 需求 9：安全与隐私

**用户故事：** 作为用户，我希望我的 API Key 和 App Secret 不会被发送到任何服务器，以保护我的账户安全。

#### 验收标准

1. THE Wizard SHALL 作为纯静态站点运行，不向任何后端服务器发送数据
2. THE Wizard SHALL 仅在浏览器本地处理用户填写的 API Key、App Secret 等敏感信息
3. THE ContentArea SHALL 在涉及敏感信息输入的步骤（Step 5 模型配置、Step 6 飞书对接）显示安全提示，说明数据仅在本地处理
4. THE Wizard SHALL 对敏感信息输入框使用 `type="password"` 属性

### 需求 10：常见问题覆盖

**用户故事：** 作为用户，我希望在安装过程中遇到问题时能快速找到解决方案，以减少排查时间。

#### 验收标准

1. THE ContentArea SHALL 在 Step 7 脚本输出页面附带常见问题速查表
2. THE ContentArea SHALL 覆盖以下已知问题的解决方案：WSL DNS 解析失败、npm ECONNRESET（国内网络）、`openclaw` 命令找不到（PATH 问题）、Dashboard unauthorized（token 问题）、WSL 中 127.0.0.1 不可访问、飞书 `app do not have bot`、vLLM HTTP 400（未启用 tool calling 或 api 类型错误）
3. WHEN 用户在 Step 2 勾选"国内网络环境"，THE ScriptGenerator SHALL 在生成的脚本中自动包含 DNS 修复和 npm 镜像源切换

### 需求 11：响应式布局

**用户故事：** 作为用户，我希望在手机或平板上也能正常使用安装向导，以便我在不同设备上查看和复制脚本。

#### 验收标准

1. WHILE 浏览器窗口宽度小于 768px，THE Wizard SHALL 将 StepNavigator 折叠为顶部水平进度条
2. WHILE 浏览器窗口宽度大于等于 768px，THE Wizard SHALL 以左右分栏布局展示 StepNavigator 和 ContentArea
3. THE Wizard SHALL 确保 CopyButton 和脚本输出区域在移动端可正常操作
