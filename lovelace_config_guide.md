# Sofabaton Hub Lovelace Card Configuration Guide
# Sofabaton Hub Lovelace 卡片配置指南

[English](#english) | [中文](#中文)

---

## English

### 📖 Overview

The Sofabaton Hub integration provides **two custom Lovelace cards** for controlling your Sofabaton Hub:

1. **Main Card** (`sofabaton-main-card`): Activity switcher and device control
2. **Detail Card** (`sofabaton-detail-card`): Detailed key control interface

Both cards are automatically registered and available in the Home Assistant card picker after installation.

---

### 🎨 Card 1: Main Card (Activity Switcher)

The main card provides a clean interface for managing activities and devices.

#### Features:
- 📋 **Activity List**: View all configured activities
- 🔄 **Activity Switching**: Toggle activities on/off with switches
- 🎯 **Current Activity Highlight**: Active activity is clearly marked
- 🔄 **Refresh Button**: Reload data from the hub
- ℹ️ **More Info Button**: Opens detail card for active activity

#### Configuration:

**Method 1: Visual Editor (Recommended)**
1. Go to your Lovelace dashboard
2. Click the three dots (⋮) → "Edit Dashboard"
3. Click "+ Add Card"
4. Search for **"Sofabaton Hub"** in the card picker
5. Select the card
6. Choose your Sofabaton Hub entity from the dropdown
7. Click "Save"

**Method 2: Manual YAML**
```yaml
type: custom:sofabaton-main-card
entity: remote.sofabaton_hub_aabbccddeeff  # Replace with your entity ID
```

#### Screenshot Description:
- **Header**: Shows "Sofabaton" with a refresh button
- **Activity Section**: Dropdown to select activity + toggle switch
- **Loading State**: Shows "Loading data in sequence... Activity List" when fetching data
- **More Info**: Opens detail card when activity is active

---

### 🎮 Card 2: Detail Card (Key Control)

The detail card provides comprehensive control over all keys assigned to an activity.

#### Features:
- 📑 **Tabbed Interface**: Three tabs for different key types
  - **Assigned Keys**: Regular IR/RF keys assigned to devices
  - **Macro Keys**: Custom macro sequences
  - **Favorite Keys**: Quick-access favorite keys
- 🎯 **Visual Key Layout**: Buttons organized by function
- 🔄 **Real-time Loading**: Shows loading states while fetching data
- 💫 **Ripple Effect**: Visual feedback on key press
- 🔍 **Smart Display**: Only shows keys that are actually assigned

#### Configuration:

**Automatic (Recommended)**
The detail card automatically opens when you click the "More Info" button on an active activity in the main card.

**Manual YAML** (if needed)
```yaml
type: custom:sofabaton-detail-card
entity: remote.sofabaton_hub_aabbccddeeff  # Replace with your entity ID
```

#### Tab 1: Assigned Keys
Displays all keys assigned to devices in the current activity:
- **Navigation**: Up, Down, Left, Right, OK
- **Media Control**: Play, Pause, Stop, Fast Forward, Rewind
- **Volume**: Volume Up/Down, Mute
- **Channel**: Channel Up/Down
- **Function Keys**: Back, Home, Menu, Guide, Exit
- **Color Keys**: Red, Green, Yellow, Blue
- **Custom Keys**: A, B, C buttons
- **Number Pad**: 0-9 (if assigned)

#### Tab 2: Macro Keys
Displays custom macro sequences created in the Sofabaton app:
- Click to execute multi-step commands
- Shows macro name and description
- Empty state if no macros configured

#### Tab 3: Favorite Keys
Displays your favorite keys for quick access:
- Quick access to most-used functions
- Customizable in Sofabaton app
- Empty state if no favorites configured

---

### 🚀 Quick Start

1. **Install the integration** (see main README)
2. **Restart Home Assistant**
3. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)
4. **Add Main Card** to your dashboard using the card picker
5. **Select an activity** and turn it on
6. **Click "More Info"** to open the detail card
7. **Control your devices** using the key buttons

---

### 🔧 Troubleshooting

#### Cards not appearing in picker

1. **Restart Home Assistant** and wait 1-2 minutes
2. **Force refresh browser**: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
3. **Check browser console** (F12): Should see "Sofabaton Hub cards registered for Lovelace picker"
4. **Verify resources loaded**: Visit `http://your-ha-ip:8123/sofabaton_hub/www/main-card.js`

#### Cards showing blank

1. **Check entity ID** is correct in Developer Tools → States
2. **Verify entity has data**: Check `activities` and `devices` attributes
3. **Check browser console** for JavaScript errors
4. **Clear browser cache** completely

#### Keys not loading in detail card

1. **Ensure activity is active** (turned on)
2. **Wait 5 seconds** for periodic state check
3. **Check MQTT broker** is running and connected
4. **Click refresh button** in main card

#### Detail card shows attributes instead of custom UI

1. **Update to latest version** of the integration
2. **Restart Home Assistant**
3. **Clear browser cache** (Ctrl+Shift+R)
4. **Check browser console** for errors

---

### 💡 Tips

- **Activity must be active** to see keys in detail card
- **Keys are loaded sequentially** (assigned → macro → favorites) to avoid overwhelming the hub
- **Gray keys** in detail card mean they're not assigned in the Sofabaton app
- **Loading indicators** show when data is being fetched
- **Periodic checks** every 5 seconds ensure data is loaded even if MQTT push fails

---

## 中文

### 📖 概述

Sofabaton Hub 集成提供了**两个自定义 Lovelace 卡片**来控制您的 Sofabaton Hub：

1. **主卡片** (`sofabaton-main-card`)：活动切换器和设备控制
2. **详情卡片** (`sofabaton-detail-card`)：详细的按键控制界面

两个卡片在安装后会自动注册，并在 Home Assistant 卡片选择器中可用。

---

### 🎨 卡片 1：主卡片（活动切换器）

主卡片提供了一个简洁的界面来管理活动和设备。

#### 功能：
- 📋 **活动列表**：查看所有配置的活动
- 🔄 **活动切换**：使用开关切换活动的开/关
- 🎯 **当前活动高亮**：活动的活动会清晰标记
- 🔄 **刷新按钮**：从 Hub 重新加载数据
- ℹ️ **更多信息按钮**：为活动的活动打开详情卡片

#### 配置：

**方法 1：可视化编辑器（推荐）**
1. 进入您的 Lovelace 仪表板
2. 点击三个点（⋮）→ "编辑仪表板"
3. 点击 "+ 添加卡片"
4. 在卡片选择器中搜索 **"Sofabaton Hub"**
5. 选择卡片
6. 从下拉列表中选择您的 Sofabaton Hub 实体
7. 点击"保存"

**方法 2：手动 YAML**
```yaml
type: custom:sofabaton-main-card
entity: remote.sofabaton_hub_aabbccddeeff  # 替换为您的实体 ID
```

#### 截图说明：
- **标题**：显示 "Sofabaton" 和刷新按钮
- **活动部分**：下拉选择活动 + 切换开关
- **加载状态**：获取数据时显示 "Loading data in sequence... Activity List"
- **更多信息**：活动激活时打开详情卡片

---

### 🎮 卡片 2：详情卡片（按键控制）

详情卡片提供了对分配给活动的所有按键的全面控制。

#### 功能：
- 📑 **选项卡界面**：三个选项卡用于不同的按键类型
  - **分配按键**：分配给设备的常规 IR/RF 按键
  - **宏按键**：自定义宏序列
  - **收藏按键**：快速访问的收藏按键
- 🎯 **可视化按键布局**：按功能组织的按钮
- 🔄 **实时加载**：获取数据时显示加载状态
- 💫 **涟漪效果**：按键按下时的视觉反馈
- 🔍 **智能显示**：只显示实际分配的按键

#### 配置：

**自动（推荐）**
当您在主卡片中点击活动活动的"更多信息"按钮时，详情卡片会自动打开。

**手动 YAML**（如果需要）
```yaml
type: custom:sofabaton-detail-card
entity: remote.sofabaton_hub_aabbccddeeff  # 替换为您的实体 ID
```

#### 选项卡 1：分配按键
显示当前活动中分配给设备的所有按键：
- **导航**：上、下、左、右、确定
- **媒体控制**：播放、暂停、停止、快进、快退
- **音量**：音量增/减、静音
- **频道**：频道增/减
- **功能键**：返回、主页、菜单、指南、退出
- **彩色键**：红、绿、黄、蓝
- **自定义键**：A、B、C 按钮
- **数字键盘**：0-9（如果已分配）

#### 选项卡 2：宏按键
显示在 Sofabaton 应用中创建的自定义宏序列：
- 点击执行多步命令
- 显示宏名称和描述
- 如果未配置宏，则显示空状态

#### 选项卡 3：收藏按键
显示您的收藏按键以便快速访问：
- 快速访问最常用的功能
- 可在 Sofabaton 应用中自定义
- 如果未配置收藏，则显示空状态

---

### 🚀 快速开始

1. **安装集成**（参见主 README）
2. **重启 Home Assistant**
3. **清除浏览器缓存**（Ctrl+Shift+R 或 Cmd+Shift+R）
4. **使用卡片选择器添加主卡片**到您的仪表板
5. **选择一个活动**并打开它
6. **点击"更多信息"**打开详情卡片
7. **使用按键按钮控制您的设备**

---

### 🔧 故障排除

#### 卡片未出现在选择器中

1. **重启 Home Assistant** 并等待 1-2 分钟
2. **强制刷新浏览器**：Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac)
3. **检查浏览器控制台**（F12）：应该看到 "Sofabaton Hub cards registered for Lovelace picker"
4. **验证资源已加载**：访问 `http://your-ha-ip:8123/sofabaton_hub/www/main-card.js`

#### 卡片显示为空白

1. **检查实体 ID** 在开发者工具 → 状态中是否正确
2. **验证实体有数据**：检查 `activities` 和 `devices` 属性
3. **检查浏览器控制台**是否有 JavaScript 错误
4. **完全清除浏览器缓存**

#### 详情卡片中按键未加载

1. **确保活动已激活**（已打开）
2. **等待 5 秒**进行定期状态检查
3. **检查 MQTT 代理**是否正在运行并已连接
4. **点击主卡片中的刷新按钮**

#### 详情卡片显示属性而不是自定义 UI

1. **更新到最新版本**的集成
2. **重启 Home Assistant**
3. **清除浏览器缓存**（Ctrl+Shift+R）
4. **检查浏览器控制台**是否有错误

---

### 💡 提示

- **活动必须激活**才能在详情卡片中看到按键
- **按键按顺序加载**（分配 → 宏 → 收藏）以避免压垮 Hub
- **详情卡片中的灰色按键**表示它们未在 Sofabaton 应用中分配
- **加载指示器**显示何时正在获取数据
- **定期检查**每 5 秒一次，确保即使 MQTT 推送失败也能加载数据

---

### 📋 卡片功能对比

| 功能 | 主卡片 | 详情卡片 |
|------|--------|----------|
| 活动切换 | ✅ | ❌ |
| 活动列表 | ✅ | ❌ |
| 刷新数据 | ✅ | ❌ |
| 分配按键控制 | ❌ | ✅ |
| 宏按键控制 | ❌ | ✅ |
| 收藏按键控制 | ❌ | ✅ |
| 可视化按键布局 | ❌ | ✅ |
| 自动打开详情 | ✅ | N/A |

---

### � 自定义样式

两个卡片都使用 Home Assistant 的主题系统，会自动适应您的主题颜色。

**支持的主题变量：**
- `--primary-color`: 主要颜色（按钮、开关）
- `--primary-text-color`: 主要文本颜色
- `--secondary-text-color`: 次要文本颜色
- `--disabled-text-color`: 禁用文本颜色
- `--card-background-color`: 卡片背景颜色
- `--divider-color`: 分隔线颜色

---

### � 数据更新机制

#### 主卡片：
- **初始加载**：打开仪表板时自动加载活动列表
- **MQTT 推送**：活动状态变化时实时更新（500ms 防抖）
- **手动刷新**：点击刷新按钮重新加载所有数据

#### 详情卡片：
- **打开时加载**：打开详情卡片时自动请求按键数据
- **串联请求**：按顺序请求分配按键 → 宏按键 → 收藏按键
- **定期检查**：每 5 秒检查一次状态，确保数据已加载
- **MQTT 推送**：按键数据变化时实时更新（500ms 防抖）

---

### 📱 移动端支持

两个卡片都针对移动设备进行了优化：
- ✅ 响应式布局
- ✅ 触摸友好的按钮大小
- ✅ 滑动手势支持（详情卡片）
- ✅ 自适应字体大小

---

### 🆕 新功能：可视化卡片编辑器

现在您可以：
- ✅ 直接在 Home Assistant 的卡片选择器中找到 "Sofabaton Hub" 卡片
- ✅ 使用可视化编辑器选择实体，无需手写 YAML
- ✅ 智能实体识别：自动识别所有 Sofabaton Hub 实体（不依赖实体 ID 命名）
- ✅ 友好的实体显示：Sofabaton 实体显示 🎮 图标，其他 remote 实体显示 📡 图标
- ✅ 优先排序：Sofabaton Hub 实体优先显示在列表顶部

---

### � 常见问题

**问：为什么详情卡片中的某些按键是灰色的？**
答：灰色按键表示它们未在 Sofabaton 应用中分配给当前活动。您需要在 Sofabaton 应用中配置这些按键。

**问：按键数据需要多长时间加载？**
答：通常需要 2-5 秒。系统按顺序请求分配按键、宏按键和收藏按键，以避免压垮 Hub。

**问：我可以自定义按键布局吗？**
答：目前不支持自定义布局。按键布局是固定的，但只显示实际分配的按键。

**问：详情卡片可以独立使用吗？**
答：可以，您可以手动添加详情卡片到仪表板。但建议通过主卡片的"更多信息"按钮打开，这样可以确保活动已激活。

**问：为什么点击"更多信息"显示的是属性列表而不是详情卡片？**
答：这可能是因为：
1. 浏览器缓存未清除
2. JavaScript 文件未正确加载
3. 集成版本过旧

解决方法：清除浏览器缓存（Ctrl+Shift+R），重启 Home Assistant，检查浏览器控制台错误。

**问：卡片支持哪些浏览器？**
答：支持所有现代浏览器：
- ✅ Chrome/Edge (推荐)
- ✅ Firefox
- ✅ Safari
- ✅ 移动浏览器（iOS Safari、Chrome Mobile）

---

### 🔍 调试

如果遇到问题，请按以下步骤调试：

1. **打开浏览器控制台**（F12）
2. **查看 Console 标签页**，寻找错误消息
3. **查看 Network 标签页**，检查资源是否加载
4. **启用 Home Assistant 调试日志**：

```yaml
logger:
  default: info
  logs:
    custom_components.sofabaton_hub: debug
```

5. **检查 Home Assistant 日志**：设置 → 系统 → 日志

---

### 📚 相关文档

- [主 README](README.md) - 集成安装和配置
- [MQTT 主题文档](const.py) - MQTT 主题列表
- [协调器文档](coordinator.py) - 数据管理机制

---

### 🤝 贡献

如果您发现问题或有改进建议，请：
1. 在 GitHub 上提交 Issue
2. 提交 Pull Request
3. 在社区论坛讨论

---

现在您可以享受完全可视化的卡片配置体验，无需手动编写任何 YAML 代码！🎉