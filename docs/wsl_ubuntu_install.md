# WSL + Ubuntu 安装指南

## 背景

OpenClaw 在原生 Windows 上运行不稳定，官方推荐使用 WSL2（Windows Subsystem for Linux）+ Ubuntu 环境。

## 什么是 WSL

WSL（Windows Subsystem for Linux）是微软在 Windows 里内置的功能，让你不用装虚拟机、不用双系统，就能直接在 Windows 上跑 Linux 命令行。WSL2 是第二代，跑的是真正的 Linux 内核，兼容性和性能都比 WSL1 好。现在默认装的就是 WSL2。

## 安装步骤

### 第一步：启用 WSL 功能

PowerShell（管理员）运行：

```powershell
wsl --install
```

如果提示「请求的操作成功。直到重新启动系统前更改将不会生效」，重启电脑。

### 第二步：安装 Ubuntu 分发版

正常情况下用：

```powershell
wsl --install -d Ubuntu
```

#### 如果报错 `WININET_E_NAME_NOT_RESOLVED`

这是因为国内网络连不上 GitHub（`raw.githubusercontent.com` 被墙或 DNS 污染）。

解决方案：用 winget 从微软商店安装，绕过 GitHub：

```powershell
winget install Canonical.Ubuntu.2404
```

> `winget` 是 Windows 自带的包管理器，Windows 10（1809+）和 Windows 11 一般都有。
> `Canonical` 是开发 Ubuntu 的公司，`2404` 是 Ubuntu 24.04 版本号。

如果 winget 也不行，直接打开电脑上的 Microsoft Store 应用，搜索 "Ubuntu"，点安装。

### 第三步：初始化 Ubuntu

winget 安装完后，Ubuntu 还没初始化。需要手动启动一次：

```powershell
ubuntu2404
```

或者在开始菜单搜 "Ubuntu 24.04" 点击打开。

它会花几分钟初始化，然后要求设置：
- UNIX 用户名（跟 Windows 账号无关，随便取）
- 密码（输入时不会显示字符，这是正常的）

看到类似 `leo@P184:~$` 的提示符就说明成功了。

### 第四步：验证安装

在 PowerShell 里跑：

```powershell
wsl -l -v
```

应该能看到 Ubuntu 在列表中，VERSION 为 2。

以后进入 WSL 只需要：

```powershell
wsl
```

### 第五步：修 DNS（国内环境必做）

WSL 默认 DNS 配置经常有问题，进入 Ubuntu 后第一件事改 DNS：

```bash
echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf
```

永久生效（防止 WSL 重启后被重置）：

```bash
sudo bash -c 'echo -e "[network]\ngenerateResolvConf = false" > /etc/wsl.conf'
echo -e "nameserver 223.5.5.5\nnameserver 114.114.114.114" | sudo tee /etc/resolv.conf
```

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `没有已安装的分发` | WSL 功能有了但没装 Ubuntu | 用 winget 或微软商店装 Ubuntu |
| `WININET_E_NAME_NOT_RESOLVED` | 国内网络连不上 GitHub | 用 `winget install Canonical.Ubuntu.2404` 绕过 |
| `chdir failed 95` 错误 | 从 Windows 路径启动 WSL 时的路径兼容问题 | 不影响使用，忽略即可 |
| `Temporary failure resolving` | WSL 内 DNS 解析失败 | 改 DNS 为 223.5.5.5 / 114.114.114.114 |
| `HCS_E_HYPERV_NOT_INSTALLED` | WSL2 需要 Hyper-V 虚拟化，Parallels 虚拟机不支持嵌套虚拟化 | 用 WSL1 即可，或直接在 Mac 上装 OpenClaw |

## Parallels 虚拟机用户注意

如果你是在 Mac 上用 Parallels 跑 Windows，WSL2 大概率用不了（Apple Silicon Mac 上 Parallels 不支持嵌套虚拟化）。VERSION 会显示为 1。

WSL1 也能正常跑 OpenClaw，不影响功能，只是文件 I/O 性能差一些。

更好的方案是直接在 Mac 上装 Node.js + OpenClaw，不需要绕 Windows + WSL 这一圈。

## 安装完成后

WSL + Ubuntu 就绪后，就可以继续安装 Node.js 22 和 OpenClaw 了，参考 `openclaw-guide` steering 文件。
