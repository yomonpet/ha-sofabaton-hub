# Home Assistant 集成首次上架准备指南
# Home Assistant Integration Publishing Guide

[English](#english) | [中文](#中文)

---

## English

### 📋 Pre-Publishing Checklist

This guide will help you prepare your Sofabaton Hub integration for publishing to GitHub and potentially to the official Home Assistant repository (HACS).

---

### 🎯 Publishing Options

You have two main options for publishing your integration:

1. **GitHub Repository (Recommended for first-time)**: Publish to your own GitHub repository and make it available via HACS custom repository
2. **Official HACS Default Repository**: Submit to HACS default repository (requires meeting strict quality standards)
3. **Home Assistant Core**: Submit to Home Assistant core (very strict requirements, not recommended for custom integrations)

**Recommendation**: Start with option 1, then consider option 2 after gathering user feedback.

---

### 📦 Step 1: Prepare Required Files

#### ✅ Essential Files (Already Complete)

- [x] `manifest.json` - Integration metadata
- [x] `__init__.py` - Integration entry point
- [x] `config_flow.py` - Configuration flow
- [x] `const.py` - Constants
- [x] `coordinator.py` - Data coordinator
- [x] `remote.py` - Remote platform
- [x] `api.py` - API client
- [x] `translations/en.json` - English translations
- [x] `translations/zh-Hans.json` - Chinese translations
- [x] `www/` - Frontend resources
- [x] `README.md` - Documentation
- [x] `icon.png` - Integration icon

#### ⚠️ Files to Create/Update

1. **LICENSE** - Required for open source
2. **CHANGELOG.md** - Version history
3. **hacs.json** - HACS configuration (if publishing to HACS)
4. **.gitignore** - Git ignore file
5. **manifest.json** - Update URLs with actual GitHub repository

---

### 📝 Step 2: Create Missing Files

#### 2.1 Create LICENSE File

Choose a license (MIT is recommended for HA integrations):

```
MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

#### 2.2 Create CHANGELOG.md

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [2.3.4] - 2025-01-10

### Added
- Custom Lovelace cards (main card and detail card)
- Visual card editor for easy configuration
- Real-time MQTT push updates
- Sequential key request mechanism
- Debouncing for state updates (500ms)

### Changed
- Optimized frontend update logic to prevent duplicate renders
- Increased periodic state check interval from 1s to 5s
- Improved request timeout handling

### Fixed
- Dialog close issues
- Data cleanup when requesting new activity keys
- WebSocket API errors

## [2.3.0] - 2024-12-XX

### Added
- Initial release with basic functionality
- mDNS auto-discovery
- Activity control
- Device management
- MQTT integration

## [2.0.0] - 2024-XX-XX

### Added
- First public release
```

#### 2.3 Create .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Home Assistant
*.log
```

#### 2.4 Create hacs.json (for HACS)

```json
{
  "name": "Sofabaton Hub",
  "render_readme": true,
  "domains": ["remote"],
  "iot_class": "Local Push",
  "homeassistant": "2023.1.0"
}
```

---

### 🔧 Step 3: Update manifest.json

Update the following fields in `manifest.json` with your actual GitHub repository information:

```json
{
  "domain": "sofabaton_hub",
  "name": "Sofabaton Hub",
  "documentation": "https://github.com/YOUR_USERNAME/ha-sofabaton-hub",
  "issue_tracker": "https://github.com/YOUR_USERNAME/ha-sofabaton-hub/issues",
  "codeowners": ["@YOUR_GITHUB_USERNAME"],
  "iot_class": "local_push",
  "version": "2.3.4",
  "config_flow": true,
  "dependencies": ["mqtt"],
  "zeroconf": ["_sofabaton_hub._udp.local."],
  "requirements": [],
  "icon": "mdi:remote",
  "logo": "icon.png",
  "frontend": {
    "resources": [
      {
        "type": "js",
        "url": "/sofabaton_hub/www/cards.js"
      },
      {
        "type": "js",
        "url": "/sofabaton_hub/www/main-card.js"
      },
      {
        "type": "js",
        "url": "/sofabaton_hub/www/detail-card.js"
      }
    ]
  }
}
```

**Replace**:
- `YOUR_USERNAME` with your GitHub username
- `YOUR_GITHUB_USERNAME` with your GitHub username (with @)

---

### 📁 Step 4: Organize Repository Structure

Your repository should have this structure:

```
ha-sofabaton-hub/                    # Repository root
├── custom_components/               # Required folder
│   └── sofabaton_hub/              # Integration folder (domain name)
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
├── README.md                        # Main documentation
├── LICENSE                          # License file
├── CHANGELOG.md                     # Version history
├── hacs.json                        # HACS configuration
├── .gitignore                       # Git ignore
└── lovelace_config_guide.md        # Optional: Lovelace guide
```

**Important**: The integration files must be inside `custom_components/sofabaton_hub/` folder!

---

### 🚀 Step 5: Create GitHub Repository

1. **Create a new repository on GitHub**:
   - Go to https://github.com/new
   - Repository name: `ha-sofabaton-hub` (or your preferred name)
   - Description: "Home Assistant integration for Sofabaton Hub universal remote control"
   - Choose: Public
   - Do NOT initialize with README (you already have one)

2. **Initialize local git repository**:

```bash
cd /Users/a1234/Desktop/sofabaton_hub

# Create custom_components folder structure
mkdir -p custom_components
mv __init__.py manifest.json config_flow.py coordinator.py remote.py api.py const.py icon.png translations www custom_components/sofabaton_hub/

# Initialize git
git init
git add .
git commit -m "Initial commit: Sofabaton Hub integration v2.3.4"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/ha-sofabaton-hub.git
git branch -M main
git push -u origin main
```

3. **Create a release**:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Tag version: `v2.3.4`
   - Release title: `v2.3.4 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"

---

### 📢 Step 6: Make it Available via HACS

#### Option A: HACS Custom Repository (Easiest)

Users can add your integration as a custom repository:

1. In Home Assistant, go to HACS
2. Click the three dots → "Custom repositories"
3. Add repository URL: `https://github.com/YOUR_USERNAME/ha-sofabaton-hub`
4. Category: Integration
5. Click "Add"

**Document this in your README** so users know how to install.

#### Option B: Submit to HACS Default Repository (More Visibility)

Requirements:
- Repository must be public
- Must have proper documentation
- Must follow HACS requirements: https://hacs.xyz/docs/publish/start
- Must have at least one release

Steps:
1. Ensure all requirements are met
2. Go to https://github.com/hacs/default
3. Fork the repository
4. Add your repository to `integration` file
5. Create a pull request
6. Wait for review (can take weeks)

---

### ✅ Step 7: Quality Checklist

Before publishing, verify:

- [ ] All Python files have proper docstrings
- [ ] No hardcoded credentials or sensitive data
- [ ] All strings are translatable (in translations/)
- [ ] Code follows Home Assistant style guide
- [ ] manifest.json has correct URLs
- [ ] README.md is comprehensive
- [ ] LICENSE file exists
- [ ] CHANGELOG.md is up to date
- [ ] .gitignore excludes unnecessary files
- [ ] No __pycache__ or .pyc files in repository
- [ ] Frontend resources load correctly
- [ ] Integration works after fresh install
- [ ] Config flow works correctly
- [ ] All features documented

---

### 📚 Step 8: Documentation

Ensure your README.md includes:

- [x] Clear description
- [x] Features list
- [x] Installation instructions (HACS + Manual)
- [x] Configuration guide
- [x] Usage examples
- [x] Troubleshooting
- [x] Screenshots (recommended)
- [x] FAQ
- [x] Contributing guidelines
- [x] License information

---

### 🎨 Step 9: Optional Enhancements

Consider adding:

1. **Screenshots**: Add images to README showing the UI
2. **Demo Video**: Create a short video showing installation and usage
3. **GitHub Actions**: Add CI/CD for automated testing
4. **Issue Templates**: Create templates for bug reports and feature requests
5. **Contributing Guide**: CONTRIBUTING.md file
6. **Code of Conduct**: CODE_OF_CONDUCT.md file

---

### 🐛 Step 10: Testing Before Release

Test the integration thoroughly:

1. **Fresh Installation Test**:
   - Remove existing installation
   - Install from GitHub
   - Verify auto-discovery works
   - Test manual configuration
   - Test all features

2. **Upgrade Test**:
   - Install old version
   - Upgrade to new version
   - Verify data migration works

3. **Multi-Device Test**:
   - Test with multiple hubs (if possible)
   - Test concurrent operations

4. **Error Handling Test**:
   - Test with MQTT broker offline
   - Test with hub offline
   - Test with invalid credentials

---

### 📊 Step 11: Post-Publishing

After publishing:

1. **Monitor Issues**: Respond to GitHub issues promptly
2. **Gather Feedback**: Ask users for feedback
3. **Update Documentation**: Based on common questions
4. **Plan Updates**: Create roadmap for future features
5. **Community Engagement**: Participate in Home Assistant forums

---

## 中文

### 📋 发布前检查清单

本指南将帮助您准备 Sofabaton Hub 集成，以便发布到 GitHub 并可能发布到官方 Home Assistant 仓库（HACS）。

---

### 🎯 发布选项

您有三个主要的发布选项：

1. **GitHub 仓库（首次推荐）**：发布到您自己的 GitHub 仓库，并通过 HACS 自定义仓库提供
2. **官方 HACS 默认仓库**：提交到 HACS 默认仓库（需要满足严格的质量标准）
3. **Home Assistant 核心**：提交到 Home Assistant 核心（非常严格的要求，不推荐用于自定义集成）

**建议**：从选项 1 开始，在收集用户反馈后再考虑选项 2。

---

### 📦 步骤 1：准备必需文件

#### ✅ 基本文件（已完成）

- [x] `manifest.json` - 集成元数据
- [x] `__init__.py` - 集成入口点
- [x] `config_flow.py` - 配置流程
- [x] `const.py` - 常量
- [x] `coordinator.py` - 数据协调器
- [x] `remote.py` - 遥控器平台
- [x] `api.py` - API 客户端
- [x] `translations/en.json` - 英文翻译
- [x] `translations/zh-Hans.json` - 中文翻译
- [x] `www/` - 前端资源
- [x] `README.md` - 文档
- [x] `icon.png` - 集成图标

#### ⚠️ 需要创建/更新的文件

1. **LICENSE** - 开源许可证（必需）
2. **CHANGELOG.md** - 版本历史
3. **hacs.json** - HACS 配置（如果发布到 HACS）
4. **.gitignore** - Git 忽略文件
5. **manifest.json** - 使用实际的 GitHub 仓库 URL 更新

---

### 📁 步骤 4：组织仓库结构

您的仓库应该具有以下结构：

```
ha-sofabaton-hub/                    # 仓库根目录
├── custom_components/               # 必需文件夹
│   └── sofabaton_hub/              # 集成文件夹（域名）
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
├── README.md                        # 主文档
├── LICENSE                          # 许可证文件
├── CHANGELOG.md                     # 版本历史
├── hacs.json                        # HACS 配置
├── .gitignore                       # Git 忽略
└── lovelace_config_guide.md        # 可选：Lovelace 指南
```

**重要**：集成文件必须在 `custom_components/sofabaton_hub/` 文件夹内！

---

### 🚀 步骤 5：创建 GitHub 仓库

详细步骤请参见英文部分。

---

### ✅ 步骤 7：质量检查清单

发布前，请验证：

- [ ] 所有 Python 文件都有适当的文档字符串
- [ ] 没有硬编码的凭据或敏感数据
- [ ] 所有字符串都可翻译（在 translations/ 中）
- [ ] 代码遵循 Home Assistant 风格指南
- [ ] manifest.json 有正确的 URL
- [ ] README.md 内容全面
- [ ] LICENSE 文件存在
- [ ] CHANGELOG.md 是最新的
- [ ] .gitignore 排除不必要的文件
- [ ] 仓库中没有 __pycache__ 或 .pyc 文件
- [ ] 前端资源正确加载
- [ ] 全新安装后集成正常工作
- [ ] 配置流程正常工作
- [ ] 所有功能都有文档

---

### 📚 相关资源

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/docs/publish/start)
- [Home Assistant Style Guide](https://developers.home-assistant.io/docs/development_guidelines)
- [Integration Quality Scale](https://www.home-assistant.io/docs/quality_scale/)

---

**祝您发布顺利！🎉**

