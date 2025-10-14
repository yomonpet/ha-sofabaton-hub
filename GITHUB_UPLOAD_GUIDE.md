# 🚀 GitHub 上传指南

本指南将帮助您将 Sofabaton Hub 集成上传到 GitHub 并发布到 HACS。

---

## 📋 准备工作

### 1. 检查必需文件

确保以下文件存在：

- ✅ `README.md` - 项目说明
- ✅ `LICENSE` - 许可证
- ✅ `CHANGELOG.md` - 变更日志
- ✅ `hacs.json` - HACS 配置
- ✅ `.gitignore` - Git 忽略文件
- ✅ `manifest.json` - 集成配置（codeowners 已更新为 @yomonpet）

### 2. 运行准备脚本

```bash
chmod +x prepare_for_github.sh
./prepare_for_github.sh
```

这个脚本会：
- 创建 `custom_components/sofabaton_hub/` 目录结构
- 复制所有集成文件到正确位置
- 清理 Python 缓存文件
- 检查必需文件

---

## 🌐 创建 GitHub 仓库

### 方法 1：通过 GitHub 网站

1. **登录 GitHub**
   - 访问 https://github.com
   - 使用您的账号 `yomonpet` 登录

2. **创建新仓库**
   - 点击右上角 `+` → `New repository`
   - Repository name: `ha-sofabaton-hub`
   - Description: `Sofabaton Hub integration for Home Assistant`
   - 选择 `Public`
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 `Create repository`

### 方法 2：通过 GitHub CLI（如果已安装）

```bash
gh repo create ha-sofabaton-hub --public --description "Sofabaton Hub integration for Home Assistant"
```

---

## 📤 上传代码到 GitHub

### 步骤 1：初始化 Git 仓库

```bash
cd /Users/a1234/Desktop/sofabaton_hub

# 如果还没有初始化 git
git init

# 添加所有文件
git add .

# 创建第一次提交
git commit -m "Initial commit: Sofabaton Hub integration v1.0.0"
```

### 步骤 2：连接到 GitHub 仓库

```bash
# 添加远程仓库（替换为您的实际仓库 URL）
git remote add origin https://github.com/yomonpet/ha-sofabaton-hub.git

# 设置主分支名称
git branch -M main
```

### 步骤 3：推送代码

```bash
# 推送到 GitHub
git push -u origin main
```

如果需要输入用户名和密码：
- **用户名**: `yomonpet`
- **密码**: 使用 Personal Access Token（不是账号密码）

---

## 🔑 创建 Personal Access Token（如果需要）

如果推送时需要认证：

1. **访问 GitHub Settings**
   - https://github.com/settings/tokens

2. **生成新 Token**
   - 点击 `Generate new token` → `Generate new token (classic)`
   - Note: `ha-sofabaton-hub`
   - Expiration: 选择过期时间
   - 勾选 `repo` 权限
   - 点击 `Generate token`

3. **复制 Token**
   - 复制生成的 token（只显示一次！）
   - 在 git push 时使用这个 token 作为密码

---

## 🏷️ 创建 Release

### 步骤 1：在 GitHub 网站创建 Release

1. **访问仓库页面**
   - https://github.com/yomonpet/ha-sofabaton-hub

2. **创建 Release**
   - 点击右侧 `Releases` → `Create a new release`
   - Tag version: `v1.0.0`
   - Release title: `v1.0.0 - Initial Release`
   - Description: 复制 CHANGELOG.md 中的内容
   - 点击 `Publish release`

### 步骤 2：或使用 GitHub CLI

```bash
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes "Initial release of Sofabaton Hub integration"
```

---

## 📦 添加到 HACS

### 方法 1：作为自定义仓库（推荐用于测试）

1. **打开 Home Assistant**
2. **进入 HACS**
   - 侧边栏 → HACS
3. **添加自定义仓库**
   - 点击右上角三个点 → `Custom repositories`
   - Repository: `https://github.com/yomonpet/ha-sofabaton-hub`
   - Category: `Integration`
   - 点击 `Add`
4. **安装集成**
   - 搜索 `Sofabaton Hub`
   - 点击 `Download`
   - 重启 Home Assistant

### 方法 2：提交到 HACS 默认仓库（正式发布）

1. **确保满足 HACS 要求**
   - ✅ 有 README.md
   - ✅ 有 LICENSE
   - ✅ 有 hacs.json
   - ✅ 有至少一个 Release
   - ✅ 代码在 `custom_components/sofabaton_hub/` 目录

2. **提交到 HACS**
   - Fork https://github.com/hacs/default
   - 编辑 `integration` 文件
   - 添加您的仓库 URL
   - 创建 Pull Request

---

## ✅ 验证清单

上传前请确认：

- [ ] 所有文件都在正确的位置
- [ ] `manifest.json` 中的 `codeowners` 是 `@yomonpet`
- [ ] `manifest.json` 中的 URLs 指向正确的仓库
- [ ] `hacs.json` 配置正确
- [ ] README.md 内容完整
- [ ] CHANGELOG.md 已更新
- [ ] 已清理 `__pycache__` 目录
- [ ] 已创建 `.gitignore` 文件

---

## 🔧 常见问题

### Q: 推送时提示 "Permission denied"

**A**: 使用 Personal Access Token 而不是密码

### Q: 推送时提示 "Repository not found"

**A**: 检查仓库 URL 是否正确，确保仓库已创建

### Q: HACS 找不到集成

**A**: 确保：
1. 仓库是 public
2. 已创建至少一个 release
3. `hacs.json` 配置正确
4. 代码在 `custom_components/sofabaton_hub/` 目录

### Q: 安装后 Home Assistant 报错

**A**: 检查：
1. `manifest.json` 格式正确
2. 所有必需文件都存在
3. 查看 Home Assistant 日志

---

## 📝 快速命令参考

```bash
# 1. 运行准备脚本
./prepare_for_github.sh

# 2. 初始化 Git
git init
git add .
git commit -m "Initial commit: Sofabaton Hub integration v1.0.0"

# 3. 连接 GitHub
git remote add origin https://github.com/yomonpet/ha-sofabaton-hub.git
git branch -M main

# 4. 推送代码
git push -u origin main

# 5. 创建 Release（在 GitHub 网站）
# 访问: https://github.com/yomonpet/ha-sofabaton-hub/releases/new
# Tag: v1.0.0
# Title: v1.0.0 - Initial Release
```

---

## 🎯 下一步

上传成功后：

1. ✅ 在 HACS 中测试安装
2. ✅ 验证所有功能正常
3. ✅ 分享给社区
4. ✅ 收集反馈并改进

---

**祝您上传顺利！** 🚀

如有问题，请查看：
- [GitHub 文档](https://docs.github.com/)
- [HACS 文档](https://hacs.xyz/)
- [Home Assistant 开发者文档](https://developers.home-assistant.io/)

