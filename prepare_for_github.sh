#!/bin/bash

# Sofabaton Hub Integration - GitHub Publishing Preparation Script
# This script helps organize files for GitHub publishing

set -e  # Exit on error

echo "🚀 Preparing Sofabaton Hub Integration for GitHub Publishing..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manifest.json" ]; then
    print_error "manifest.json not found. Please run this script from the integration directory."
    exit 1
fi

print_success "Found manifest.json"

# Create custom_components directory structure
echo ""
echo "📁 Creating directory structure..."

if [ ! -d "custom_components" ]; then
    mkdir -p custom_components/sofabaton_hub
    print_success "Created custom_components/sofabaton_hub directory"
else
    print_warning "custom_components directory already exists"
fi

# Move integration files to custom_components/sofabaton_hub
echo ""
echo "📦 Moving integration files..."

FILES_TO_MOVE=(
    "__init__.py"
    "manifest.json"
    "config_flow.py"
    "coordinator.py"
    "remote.py"
    "api.py"
    "const.py"
    "icon.png"
)

for file in "${FILES_TO_MOVE[@]}"; do
    if [ -f "$file" ] && [ ! -f "custom_components/sofabaton_hub/$file" ]; then
        cp "$file" "custom_components/sofabaton_hub/"
        print_success "Copied $file"
    elif [ -f "custom_components/sofabaton_hub/$file" ]; then
        print_warning "$file already exists in custom_components/sofabaton_hub/"
    else
        print_warning "$file not found"
    fi
done

# Move directories
DIRS_TO_MOVE=(
    "translations"
    "www"
)

for dir in "${DIRS_TO_MOVE[@]}"; do
    if [ -d "$dir" ] && [ ! -d "custom_components/sofabaton_hub/$dir" ]; then
        cp -r "$dir" "custom_components/sofabaton_hub/"
        print_success "Copied $dir directory"
    elif [ -d "custom_components/sofabaton_hub/$dir" ]; then
        print_warning "$dir already exists in custom_components/sofabaton_hub/"
    else
        print_warning "$dir not found"
    fi
done

# Check for required files in root
echo ""
echo "📋 Checking required files in root directory..."

REQUIRED_ROOT_FILES=(
    "README.md"
    "LICENSE"
    "CHANGELOG.md"
    "hacs.json"
    ".gitignore"
)

for file in "${REQUIRED_ROOT_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file is missing! Please create it."
    fi
done

# Clean up __pycache__ directories
echo ""
echo "🧹 Cleaning up __pycache__ directories..."

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
print_success "Cleaned up Python cache files"

# Check manifest.json for placeholder URLs
echo ""
echo "🔍 Checking manifest.json for placeholder URLs..."

if grep -q "YOUR_USERNAME\|your_repo\|your_github_username" custom_components/sofabaton_hub/manifest.json; then
    print_error "manifest.json contains placeholder URLs. Please update them with your actual GitHub information."
    echo ""
    echo "Update these fields in custom_components/sofabaton_hub/manifest.json:"
    echo "  - documentation: https://github.com/YOUR_USERNAME/ha-sofabaton-hub"
    echo "  - issue_tracker: https://github.com/YOUR_USERNAME/ha-sofabaton-hub/issues"
    echo "  - codeowners: [@YOUR_GITHUB_USERNAME]"
else
    print_success "manifest.json URLs look good"
fi

# Create .github directory for issue templates (optional)
echo ""
echo "📝 Creating GitHub templates directory..."

if [ ! -d ".github" ]; then
    mkdir -p .github/ISSUE_TEMPLATE
    print_success "Created .github/ISSUE_TEMPLATE directory"
else
    print_warning ".github directory already exists"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your repository structure should now look like this:"
echo ""
echo "ha-sofabaton-hub/"
echo "├── custom_components/"
echo "│   └── sofabaton_hub/"
echo "│       ├── __init__.py"
echo "│       ├── manifest.json"
echo "│       ├── config_flow.py"
echo "│       ├── coordinator.py"
echo "│       ├── remote.py"
echo "│       ├── api.py"
echo "│       ├── const.py"
echo "│       ├── icon.png"
echo "│       ├── translations/"
echo "│       └── www/"
echo "├── .github/"
echo "│   └── ISSUE_TEMPLATE/"
echo "├── README.md"
echo "├── LICENSE"
echo "├── CHANGELOG.md"
echo "├── CONTRIBUTING.md"
echo "├── hacs.json"
echo "├── .gitignore"
echo "└── lovelace_config_guide.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Update manifest.json with your GitHub repository URLs"
echo "2. Review and update README.md if needed"
echo "3. Initialize git repository:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit: Sofabaton Hub integration v2.3.4'"
echo ""
echo "4. Create GitHub repository and push:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/ha-sofabaton-hub.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "5. Create a release on GitHub (v2.3.4)"
echo ""
echo "6. Test installation via HACS custom repository"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_success "Preparation complete! 🎉"
echo ""
echo "For detailed instructions, see PUBLISHING_GUIDE.md"
echo ""

