# Pre-Release Checklist for Sofabaton Hub Integration
# 发布前检查清单

## 📋 Before Publishing to GitHub

### 1. File Structure ✅
- [ ] All files are in `custom_components/sofabaton_hub/` directory
- [ ] Root directory contains: README.md, LICENSE, CHANGELOG.md, hacs.json, .gitignore
- [ ] No `__pycache__` directories or `.pyc` files
- [ ] No sensitive data (passwords, IPs, tokens) in any files
- [ ] All necessary files are present (see list below)

### 2. Required Files Checklist ✅

#### Root Directory:
- [ ] `README.md` - Comprehensive documentation (English + Chinese)
- [ ] `LICENSE` - MIT License
- [ ] `CHANGELOG.md` - Version history
- [ ] `CONTRIBUTING.md` - Contribution guidelines
- [ ] `hacs.json` - HACS configuration
- [ ] `.gitignore` - Git ignore file
- [ ] `PUBLISHING_GUIDE.md` - Publishing instructions
- [ ] `lovelace_config_guide.md` - Lovelace card guide (optional)

#### custom_components/sofabaton_hub/:
- [ ] `__init__.py` - Integration entry point
- [ ] `manifest.json` - Integration metadata
- [ ] `config_flow.py` - Configuration flow
- [ ] `coordinator.py` - Data coordinator
- [ ] `remote.py` - Remote platform
- [ ] `api.py` - API client
- [ ] `const.py` - Constants
- [ ] `icon.png` - Integration icon
- [ ] `translations/en.json` - English translations
- [ ] `translations/zh-Hans.json` - Chinese translations
- [ ] `www/cards.js` - Card registration
- [ ] `www/main-card.js` - Main card
- [ ] `www/detail-card.js` - Detail card

#### .github/ (Optional but Recommended):
- [ ] `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] `.github/ISSUE_TEMPLATE/config.yml`

### 3. manifest.json Updates ✅
- [ ] `documentation` URL updated with actual GitHub repository
- [ ] `issue_tracker` URL updated with actual GitHub repository
- [ ] `codeowners` updated with actual GitHub username
- [ ] `version` is correct (currently 2.3.4)
- [ ] No placeholder text (YOUR_USERNAME, your_repo, etc.)

### 4. Code Quality ✅
- [ ] All Python files have proper docstrings
- [ ] No hardcoded credentials or sensitive data
- [ ] All strings are translatable (in translations/)
- [ ] Code follows Home Assistant style guide
- [ ] No obvious bugs or errors
- [ ] Error handling is implemented
- [ ] Logging is appropriate (not too verbose, not too quiet)

### 5. Documentation ✅
- [ ] README.md is comprehensive and up-to-date
- [ ] Installation instructions are clear (HACS + Manual)
- [ ] Configuration guide is complete
- [ ] Troubleshooting section is helpful
- [ ] Screenshots or examples are included (recommended)
- [ ] FAQ section addresses common questions
- [ ] Both English and Chinese versions are complete

### 6. Testing ✅
- [ ] Fresh installation works
- [ ] Auto-discovery works (mDNS)
- [ ] Manual configuration works
- [ ] All features work as expected:
  - [ ] Activity switching
  - [ ] Key control (assigned, macro, favorite)
  - [ ] Main card displays correctly
  - [ ] Detail card displays correctly
  - [ ] MQTT communication works
  - [ ] Real-time updates work
- [ ] Error handling works:
  - [ ] MQTT broker offline
  - [ ] Hub offline
  - [ ] Invalid credentials
  - [ ] Network issues
- [ ] Upgrade from previous version works (if applicable)
- [ ] Multiple hubs work (if applicable)

### 7. Frontend ✅
- [ ] Cards load correctly in Lovelace
- [ ] Card picker shows "Sofabaton Hub"
- [ ] Visual editor works
- [ ] Cards work in different browsers:
  - [ ] Chrome/Edge
  - [ ] Firefox
  - [ ] Safari
  - [ ] Mobile browsers
- [ ] No JavaScript errors in console
- [ ] CSS styles are applied correctly
- [ ] Responsive design works on mobile

### 8. Translations ✅
- [ ] All UI strings are in translations files
- [ ] English translations are complete
- [ ] Chinese translations are complete
- [ ] No hardcoded strings in code
- [ ] Translation keys are descriptive

### 9. HACS Compatibility ✅
- [ ] `hacs.json` is present and correct
- [ ] Repository structure follows HACS requirements
- [ ] `manifest.json` follows HACS requirements
- [ ] README.md renders correctly on GitHub
- [ ] At least one release is created

### 10. Git & GitHub ✅
- [ ] `.gitignore` excludes unnecessary files
- [ ] No large files (>1MB) unless necessary
- [ ] Commit messages are clear and descriptive
- [ ] No sensitive data in git history
- [ ] Repository is public
- [ ] Repository has a clear description
- [ ] Repository has topics/tags (home-assistant, hacs, integration, etc.)

---

## 🚀 Publishing Steps

### Step 1: Prepare Local Repository
```bash
# Run the preparation script
chmod +x prepare_for_github.sh
./prepare_for_github.sh

# Review the output and fix any issues
```

### Step 2: Update manifest.json
```bash
# Edit custom_components/sofabaton_hub/manifest.json
# Replace YOUR_USERNAME with your actual GitHub username
```

### Step 3: Initialize Git
```bash
git init
git add .
git commit -m "Initial commit: Sofabaton Hub integration v2.3.4"
```

### Step 4: Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `ha-sofabaton-hub`
3. Description: "Home Assistant integration for Sofabaton Hub universal remote control"
4. Public repository
5. Do NOT initialize with README (you already have one)
6. Create repository

### Step 5: Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/ha-sofabaton-hub.git
git branch -M main
git push -u origin main
```

### Step 6: Create Release
1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Tag version: `v2.3.4`
4. Release title: `v2.3.4 - Initial Release`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

### Step 7: Test Installation
1. In Home Assistant, go to HACS
2. Click three dots → "Custom repositories"
3. Add: `https://github.com/YOUR_USERNAME/ha-sofabaton-hub`
4. Category: Integration
5. Install and test

### Step 8: Update Repository Settings
1. Add topics: `home-assistant`, `hacs`, `integration`, `sofabaton`, `remote-control`
2. Add description
3. Add website (if you have one)
4. Enable Issues
5. Enable Discussions (recommended)

---

## 📊 Post-Publishing

### Immediate Actions:
- [ ] Test installation via HACS custom repository
- [ ] Verify all features work after installation
- [ ] Check that documentation renders correctly on GitHub
- [ ] Monitor for any immediate issues

### Within First Week:
- [ ] Respond to any issues or questions
- [ ] Gather user feedback
- [ ] Update documentation based on feedback
- [ ] Consider creating a discussion thread

### Within First Month:
- [ ] Evaluate if ready for HACS default repository submission
- [ ] Plan next version features
- [ ] Update CHANGELOG.md for next release
- [ ] Consider creating a roadmap

---

## 🎯 HACS Default Repository Submission (Optional)

If you want to submit to HACS default repository later:

### Requirements:
- [ ] Repository has been public for at least 2 weeks
- [ ] At least one release
- [ ] No major issues reported
- [ ] Documentation is comprehensive
- [ ] Code quality is high
- [ ] Active maintenance

### Submission Process:
1. Go to https://github.com/hacs/default
2. Fork the repository
3. Add your repository to the `integration` file
4. Create a pull request
5. Wait for review (can take weeks)

---

## ✅ Final Checklist

Before clicking "Publish":

- [ ] All items in "Before Publishing to GitHub" are checked
- [ ] manifest.json URLs are updated
- [ ] No placeholder text anywhere
- [ ] All tests pass
- [ ] Documentation is complete
- [ ] You're ready to support users!

---

## 📞 Need Help?

- Review `PUBLISHING_GUIDE.md` for detailed instructions
- Check Home Assistant developer docs: https://developers.home-assistant.io/
- Ask in Home Assistant Discord: https://discord.gg/home-assistant
- Post in Home Assistant forums: https://community.home-assistant.io/

---

**Good luck with your release! 🎉**

