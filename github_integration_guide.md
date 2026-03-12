# GitHub 集成安装指南

## 步骤 1: 生成 GitHub Personal Access Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)" 或 "Generate new token"
3. 填写备注：`OpenClaw Integration`
4. 选择以下权限 scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `read:org` (Read org membership)
   - ✅ `read:user` (Read user profile)
   - ✅ `user:email` (Read user emails)
5. 点击 "Generate token"
6. **重要：** 立即复制 token（只会显示一次）
   - 格式：`ghp_xxxxxxxxxxxxxxxxxxxx`

## 步骤 2: 配置到 OpenClaw

### 方法 A: 通过配置文件

编辑 `~/.openclaw/openclaw.json`，添加 GitHub 配置：

```json
{
  "integrations": {
    "github": {
      "token": "ghp_your_token_here",
      "username": "your_github_username",
      "defaultRepo": "owner/repo"
    }
  }
}
```

### 方法 B: 通过环境变量

在 Gateway 环境变量中添加：

```bash
export GITHUB_TOKEN=ghp_your_token_here
export GITHUB_USERNAME=your_github_username
```

编辑 systemd 服务文件：
```bash
systemctl --user edit openclaw-gateway
```

添加：
```ini
[Service]
Environment="GITHUB_TOKEN=ghp_your_token_here"
Environment="GITHUB_USERNAME=your_github_username"
```

重启 Gateway：
```bash
openclaw gateway restart
```

## 步骤 3: 测试连接

```bash
# 测试 GitHub API 连接
curl -H "Authorization: token ghp_your_token_here" \
     https://api.github.com/user
```

预期返回：
```json
{
  "login": "your_username",
  "id": 123456,
  ...
}
```

## 步骤 4: 使用 GitHub 功能

安装完成后，你可以：

1. **克隆仓库到 workspace**
   ```bash
   cd ~/.openclaw/workspace
   git clone https://github.com/username/repo.git
   ```

2. **配置 Git 用户信息**
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your@email.com"
   ```

3. **使用 Git 命令**
   ```bash
   git status
   git add .
   git commit -m "message"
   git push
   ```

## 安全提示

- ⚠️ **不要**将 token 提交到 Git 仓库
- ⚠️ **不要**在日志中暴露 token
- ✅ 将 token 添加到 `.gitignore`
- ✅ 定期轮换 token（建议每 90 天）
- ✅ 使用最小权限原则

## 故障排查

### 问题 1: Token 无效
- 检查 token 是否正确复制（无空格）
- 确认 token 未过期
- 确认 scopes 权限足够

### 问题 2: 权限不足
- 重新生成 token，确保勾选所有必要 scopes
- 检查仓库权限设置

### 问题 3: 连接超时
- 检查网络连接
- 检查防火墙设置
- 尝试使用代理

## 高级配置

### 配置多个 GitHub 账号

```json
{
  "integrations": {
    "github": {
      "accounts": [
        {
          "name": "personal",
          "token": "ghp_xxx",
          "username": "user1"
        },
        {
          "name": "work",
          "token": "ghp_yyy",
          "username": "user2"
        }
      ],
      "default": "personal"
    }
  }
}
```

### 配置 SSH Key（可选）

```bash
# 生成 SSH key
ssh-keygen -t ed25519 -C "your@email.com"

# 添加到 GitHub
# 访问 https://github.com/settings/keys
# 点击 "New SSH key"
# 粘贴 ~/.ssh/id_ed25519.pub 内容

# 测试连接
ssh -T git@github.com
```

---

**下一步:**
1. 生成 GitHub Token
2. 选择配置方法（配置文件或环境变量）
3. 重启 Gateway
4. 测试连接

**需要我帮你执行哪个步骤？**
