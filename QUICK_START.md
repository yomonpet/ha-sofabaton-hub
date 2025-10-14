# 🚀 Quick Start Guide - Publishing to GitHub
# 快速开始指南 - 发布到 GitHub

[English](#english) | [中文](#中文)

---

## English

### 📋 What You Have Now

Your Sofabaton Hub integration is **ready to publish**! Here's what has been prepared:

#### ✅ Complete Files:
- **Integration Code**: All Python files, frontend resources, translations
- **Documentation**: README.md (English + Chinese), Lovelace guide
- **Publishing Files**: LICENSE, CHANGELOG.md, CONTRIBUTING.md, hacs.json, .gitignore
- **GitHub Templates**: Issue templates, feature request templates
- **Helper Scripts**: `prepare_for_github.sh` for organizing files

---

### 🎯 Three Simple Steps to Publish

#### Step 1: Update manifest.json (2 minutes)

Edit `manifest.json` and replace placeholders:

```json
{
  "documentation": "https://github.com/YOUR_USERNAME/ha-sofabaton-hub",
  "issue_tracker": "https://github.com/YOUR_USERNAME/ha-sofabaton-hub/issues",
  "codeowners": ["@YOUR_GITHUB_USERNAME"]
}
```

Replace:
- `YOUR_USERNAME` → Your GitHub username (e.g., `johndoe`)
- `YOUR_GITHUB_USERNAME` → Your GitHub username with @ (e.g., `@johndoe`)

#### Step 2: Run Preparation Script (1 minute)

```bash
cd /Users/a1234/Desktop/sofabaton_hub
./prepare_for_github.sh
```

This script will:
- Create `custom_components/sofabaton_hub/` directory
- Copy all integration files to the correct location
- Clean up cache files
- Verify all required files exist

#### Step 3: Create GitHub Repository & Push (5 minutes)

1. **Create repository on GitHub**:
   - Go to https://github.com/new
   - Name: `ha-sofabaton-hub`
   - Description: "Home Assistant integration for Sofabaton Hub universal remote control"
   - Public repository
   - Click "Create repository"

2. **Push your code**:
```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: Sofabaton Hub integration v2.3.4"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/ha-sofabaton-hub.git
git branch -M main
git push -u origin main
```

3. **Create a release**:
   - Go to your repository → "Releases" → "Create a new release"
   - Tag: `v2.3.4`
   - Title: `v2.3.4 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

**Done! Your integration is now published! 🎉**

---

### 📦 How Users Will Install

#### Via HACS Custom Repository:

1. In Home Assistant, go to HACS
2. Click three dots (⋮) → "Custom repositories"
3. Add repository: `https://github.com/YOUR_USERNAME/ha-sofabaton-hub`
4. Category: Integration
5. Click "Add"
6. Search for "Sofabaton Hub" and install

#### Manual Installation:

1. Download the latest release
2. Extract to `config/custom_components/sofabaton_hub/`
3. Restart Home Assistant

---

### 📚 Important Documents

| Document | Purpose |
|----------|---------|
| `PUBLISHING_GUIDE.md` | **Detailed publishing instructions** |
| `PRE_RELEASE_CHECKLIST.md` | **Complete checklist before publishing** |
| `README.md` | User documentation |
| `CHANGELOG.md` | Version history |
| `CONTRIBUTING.md` | Contribution guidelines |
| `lovelace_config_guide.md` | Lovelace card configuration |

---

### ✅ Pre-Publishing Checklist

Quick checklist (see `PRE_RELEASE_CHECKLIST.md` for full list):

- [ ] Updated `manifest.json` with your GitHub URLs
- [ ] Ran `./prepare_for_github.sh` successfully
- [ ] Tested the integration works
- [ ] No sensitive data in files
- [ ] All documentation is complete

---

### 🆘 Need Help?

1. **Detailed Instructions**: Read `PUBLISHING_GUIDE.md`
2. **Full Checklist**: Check `PRE_RELEASE_CHECKLIST.md`
3. **Issues**: Create an issue on GitHub (after publishing)
4. **Community**: Ask in Home Assistant forums

---

## 中文

### 📋 您现在拥有的内容

您的 Sofabaton Hub 集成**已准备好发布**！以下是已准备的内容：

#### ✅ 完整文件：
- **集成代码**：所有 Python 文件、前端资源、翻译
- **文档**：README.md（英文 + 中文）、Lovelace 指南
- **发布文件**：LICENSE、CHANGELOG.md、CONTRIBUTING.md、hacs.json、.gitignore
- **GitHub 模板**：问题模板、功能请求模板
- **辅助脚本**：`prepare_for_github.sh` 用于组织文件

---

### 🎯 三个简单步骤发布

#### 步骤 1：更新 manifest.json（2 分钟）

编辑 `manifest.json` 并替换占位符：

```json
{
  "documentation": "https://github.com/YOUR_USERNAME/ha-sofabaton-hub",
  "issue_tracker": "https://github.com/YOUR_USERNAME/ha-sofabaton-hub/issues",
  "codeowners": ["@YOUR_GITHUB_USERNAME"]
}
```

替换：
- `YOUR_USERNAME` → 您的 GitHub 用户名（例如：`johndoe`）
- `YOUR_GITHUB_USERNAME` → 您的 GitHub 用户名带 @（例如：`@johndoe`）

#### 步骤 2：运行准备脚本（1 分钟）

```bash
cd /Users/a1234/Desktop/sofabaton_hub
./prepare_for_github.sh
```

此脚本将：
- 创建 `custom_components/sofabaton_hub/` 目录
- 将所有集成文件复制到正确位置
- 清理缓存文件
- 验证所有必需文件存在

#### 步骤 3：创建 GitHub 仓库并推送（5 分钟）

1. **在 GitHub 上创建仓库**：
   - 访问 https://github.com/new
   - 名称：`ha-sofabaton-hub`
   - 描述："Home Assistant integration for Sofabaton Hub universal remote control"
   - 公开仓库
   - 点击"Create repository"

2. **推送您的代码**：
```bash
# 初始化 git
git init
git add .
git commit -m "Initial commit: Sofabaton Hub integration v2.3.4"

# 推送到 GitHub
git remote add origin https://github.com/YOUR_USERNAME/ha-sofabaton-hub.git
git branch -M main
git push -u origin main
```

3. **创建发布**：
   - 进入您的仓库 → "Releases" → "Create a new release"
   - 标签：`v2.3.4`
   - 标题：`v2.3.4 - Initial Release`
   - 描述：从 CHANGELOG.md 复制
   - 点击"Publish release"

**完成！您的集成现已发布！🎉**

---

### 📦 用户如何安装

#### 通过 HACS 自定义仓库：

1. 在 Home Assistant 中，进入 HACS
2. 点击三个点（⋮）→ "自定义仓库"
3. 添加仓库：`https://github.com/YOUR_USERNAME/ha-sofabaton-hub`
4. 类别：集成
5. 点击"添加"
6. 搜索"Sofabaton Hub"并安装

#### 手动安装：

1. 下载最新版本
2. 解压到 `config/custom_components/sofabaton_hub/`
3. 重启 Home Assistant

---

### 📚 重要文档

| 文档 | 用途 |
|------|------|
| `PUBLISHING_GUIDE.md` | **详细发布说明** |
| `PRE_RELEASE_CHECKLIST.md` | **发布前完整检查清单** |
| `README.md` | 用户文档 |
| `CHANGELOG.md` | 版本历史 |
| `CONTRIBUTING.md` | 贡献指南 |
| `lovelace_config_guide.md` | Lovelace 卡片配置 |

---

### ✅ 发布前检查清单

快速检查清单（完整列表见 `PRE_RELEASE_CHECKLIST.md`）：

- [ ] 使用您的 GitHub URL 更新了 `manifest.json`
- [ ] 成功运行了 `./prepare_for_github.sh`
- [ ] 测试了集成正常工作
- [ ] 文件中没有敏感数据
- [ ] 所有文档都已完成

---

### 🆘 需要帮助？

1. **详细说明**：阅读 `PUBLISHING_GUIDE.md`
2. **完整检查清单**：查看 `PRE_RELEASE_CHECKLIST.md`
3. **问题**：在 GitHub 上创建问题（发布后）
4. **社区**：在 Home Assistant 论坛提问

---

### 📊 文件结构预览

发布后，您的仓库将如下所示：

```
ha-sofabaton-hub/
├── custom_components/
│   └── sofabaton_hub/          # 集成文件
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── remote.py
│       ├── api.py
│       ├── const.py
│       ├── icon.png
│       ├── translations/
│       │   ├── en.json
│       │   └── zh-Hans.json
│       └── www/
│           ├── cards.js
│           ├── main-card.js
│           └── detail-card.js
├── .github/
│   └── ISSUE_TEMPLATE/         # GitHub 模板
├── README.md                   # 主文档
├── LICENSE                     # 许可证
├── CHANGELOG.md                # 更新日志
├── CONTRIBUTING.md             # 贡献指南
├── hacs.json                   # HACS 配置
├── .gitignore                  # Git 忽略
└── lovelace_config_guide.md   # Lovelace 指南
```

---

### 🎯 下一步

发布后：

1. **测试安装**：通过 HACS 自定义仓库测试安装
2. **监控问题**：及时响应 GitHub 问题
3. **收集反馈**：向用户征求反馈
4. **计划更新**：根据反馈计划下一个版本
5. **考虑提交到 HACS 默认仓库**：2-4 周后

---

**祝您发布顺利！🚀**

