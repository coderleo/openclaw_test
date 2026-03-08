# Node.js 22 安装指南（WSL/Ubuntu 环境）

## 为什么需要 Node.js 22

OpenClaw 要求 Node.js 22 或更高版本。Ubuntu 官方软件源里的 Node.js 只有 18.x，版本不够，所以不能直接 `apt install nodejs`。

需要先添加 NodeSource 的第三方软件源，再用 apt 安装。

## 什么是 NodeSource

NodeSource 是一个专门维护 Node.js 安装包的第三方源。它提供最新版本的 Node.js deb 包，Ubuntu 官方源不提供的新版本可以从这里获取。

## 安装步骤

### 1. 确保 DNS 正常

如果在 WSL 中，先确认 DNS 已修改（否则 curl 会失败）：

```bash
echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf
```

### 2. 添加 NodeSource 源并安装

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

这个脚本做了两件事：
- 把 NodeSource 的软件源添加到 `/etc/apt/sources.list.d/`
- 自动执行一次 `apt update` 刷新包索引

之后 `apt install nodejs` 装的就是 22.x 了。

### 3. 验证安装

```bash
node -v   # 应该输出 v22.x
npm -v    # npm 会随 Node.js 一起安装
```

## 为什么不能直接 `apt install nodejs`

`apt install nodejs` 只会从你已有的软件源里找包。Ubuntu 24.04 (Noble) 官方源里 Node.js 最高只有 18.19.1。

`sudo apt update` 只是刷新已有源的包索引，不会添加新的源。就像去你已经知道的几家超市看看有没有新货到，但不会帮你发现新的超市。

添加 NodeSource 源 = 告诉 apt 还有一家新的"超市"可以去，这家超市里有 Node.js 22。

## Node.js 版本说明

| 版本 | 状态 | 说明 |
|------|------|------|
| Node 18 | 维护中（2025年4月 EOL） | Ubuntu 官方源默认版本，太老 |
| Node 20 | LTS | 稳定，但 OpenClaw 推荐 22 |
| Node 22 | LTS（推荐） | 当前长期支持版本，OpenClaw 要求的最低版本 |
| Node 24 | Current | 最新版，还没进入 LTS，可能有兼容问题 |

建议用 Node 22，稳定可靠。

## Windows 上安装

### 方式一：官网下载安装包（最简单）

1. 打开 https://nodejs.org/
2. 下载 LTS 版本（22.x）的 Windows 安装包（.msi）
3. 双击运行，一路 Next 即可
4. 安装完打开 PowerShell 验证：

```powershell
node -v   # 应该输出 v22.x
npm -v
```

### 方式二：用 winget 安装

```powershell
winget install OpenJS.NodeJS.LTS
```

### 方式三：用 fnm（Fast Node Manager）

fnm 可以管理多个 Node.js 版本，方便切换：

```powershell
winget install Schniz.fnm
fnm install 22
fnm use 22
node -v
```

> 注意：如果你是在 WSL 里跑 OpenClaw，应该在 WSL（Ubuntu）里装 Node.js，不是在 Windows 侧装。Windows 侧装的 Node.js 在 WSL 里用不了。

## macOS 上安装

如果直接在 Mac 上装（不走 WSL），用 Homebrew：

```bash
brew install node@22
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `Temporary failure resolving` | DNS 解析失败，curl 下载不了脚本 | 先修 DNS（见步骤 1） |
| 装完还是 18.x | 没有添加 NodeSource 源就直接 apt install 了 | 先跑 `curl ... setup_22.x` 脚本再装 |
| `npm: command not found` | npm 没装上 | NodeSource 的 nodejs 包自带 npm，重新装一次 |

## PATH 问题

如果后续用 npm 全局安装的命令（如 `openclaw`）找不到，需要把 npm 全局目录加到 PATH：

```bash
export PATH="$(npm prefix -g)/bin:$PATH"
echo 'export PATH="$(npm prefix -g)/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```
