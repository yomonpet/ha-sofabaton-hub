# Sofabaton Hub for Home Assistant

[English](#english) | [中文](#中文)

---

## English

### 📖 Overview

This is a custom integration for Home Assistant that allows you to control your Sofabaton Hub remote control. It provides a beautiful, feature-rich interface with real-time updates via MQTT.

> **⚠️ Device Compatibility**
>
> This integration is designed for **Sofabaton X2** only.
>
> **NOT compatible with Sofabaton X1s** (older model).

**Key Features:**
- 🔍 **Automatic Discovery**: Automatically discovers Sofabaton Hub devices on your network via mDNS/Zeroconf
- 🎮 **Activity Control**: Switch between activities, view and control all assigned keys
- 🔑 **Key Management**: View assigned keys, macro keys, and favorite keys for each activity
- 📱 **Custom UI**: Beautiful Lovelace cards with real-time updates
- 🔄 **Real-time Updates**: MQTT-based push notifications for instant state changes
- 🌐 **Bilingual**: Supports English and Chinese

---

### ⚙️ Prerequisites

Before installing this integration, you **must** have an MQTT broker running in your Home Assistant setup.

#### Install Mosquitto Broker Add-on

1. **Go to Settings** → **Add-ons** → **Add-on Store**
2. **Search for "Mosquitto broker"**
3. **Click "Install"**
4. **After installation**, go to the **Configuration** tab:
   - Set a username and password (optional but recommended)
   - Example configuration:
     ```yaml
     logins:
       - username: mqtt_user
         password: your_secure_password
     ```
5. **Click "Save"**
6. **Go to the Info tab** and click **"Start"**
7. **Enable "Start on boot"** and **"Watchdog"**

#### Configure MQTT Integration

1. **Go to Settings** → **Devices & Services** → **Integrations**
2. **Search for "MQTT"** and add it
3. **Configure**:
   - Broker: `localhost` (or your MQTT broker IP)
   - Port: `1883`
   - Username: (the one you set in Mosquitto)
   - Password: (the one you set in Mosquitto)

**Note**: The Sofabaton Hub communicates with Home Assistant via MQTT. Without a working MQTT broker, this integration will not function.

---

### 🚀 Quick Start

1. **Install Mosquitto broker** (see Prerequisites above)
2. **Install the integration** (via HACS or manually)
3. **Restart Home Assistant**
4. **Wait for auto-discovery** or add manually via Settings → Integrations
5. **Configure MQTT connection** (use the same credentials as your MQTT integration)
6. **Add Lovelace cards** to your dashboard
7. **Start controlling your devices!**

**Typical Setup Time**: 10-15 minutes (including MQTT setup)

---

### 📸 Screenshots

> **Note**: Add screenshots of your setup here to help users visualize the interface.

**Main Card - Activity Switcher:**
- Shows all configured activities
- Toggle switches to activate/deactivate activities
- Current activity highlighted
- Refresh button to reload data

**Detail Card - Key Control:**
- Tabbed interface for different key types
- Visual key buttons with labels
- Loading states during data fetch
- Ripple effect on key press

---

### �📦 Installation

#### Method 1: HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Install"
7. Restart Home Assistant

#### Method 2: Manual Installation

1. Download this repository
2. Copy the `sofabaton_hub` folder to your Home Assistant's `custom_components` directory:
   ```
   /config/custom_components/sofabaton_hub/
   ```
3. Restart Home Assistant

---

### 🔧 Configuration

**Important**: Make sure you have completed the [Prerequisites](#️-prerequisites) section and have a working MQTT broker before proceeding.

#### Automatic Discovery (Recommended)

1. Make sure your Sofabaton Hub is connected to the same network as Home Assistant
2. Go to **Settings** → **Devices & Services** → **Integrations**
3. You should see a "Discovered" notification for Sofabaton Hub
4. Click **"Configure"** and follow the setup wizard
5. Enter your MQTT broker credentials:
   - **MQTT Host**: `localhost` (if using Mosquitto add-on) or your broker's IP
   - **MQTT Port**: `1883` (default)
   - **Username**: The username you set in Mosquitto broker
   - **Password**: The password you set in Mosquitto broker

#### Manual Configuration

If automatic discovery doesn't work, you can add the integration manually:

1. Go to **Settings** → **Devices & Services** → **Integrations**
2. Click **"+ Add Integration"**
3. Search for **"Sofabaton Hub"**
4. Enter the following information:
   - **MAC Address**: Your Sofabaton Hub's MAC address (e.g., `AA:BB:CC:DD:EE:FF`)
   - **Name**: A friendly name for your hub (default: "Sofabaton Hub")
   - **MQTT Host**: `localhost` (if using Mosquitto add-on) or your broker's IP
   - **MQTT Port**: `1883` (default)
   - **Username**: The username you set in Mosquitto broker
   - **Password**: The password you set in Mosquitto broker

**Note**: The MQTT credentials must match the ones you configured in the Mosquitto broker add-on.

---

### 🎨 Adding Lovelace Cards

After installation, you need to add the custom cards to your Lovelace dashboard.

> **⚠️ IMPORTANT: You MUST use the custom cards provided by this integration!**
>
> **DO NOT** use the default entity card, button card, or any other generic cards. They will not work properly with this integration because:
> - The custom cards handle complex MQTT communication and state management
> - They provide the proper UI for activity switching and key control
> - Generic cards cannot access the custom functionality (key requests, activity switching, etc.)

#### How to Add Cards to Dashboard

**Method 1: Visual Editor (Recommended)**

1. **Go to your dashboard** and click **"Edit Dashboard"** (top right corner)
2. **Click "+ Add Card"** button
3. **Scroll down** to the **"Custom cards"** section
4. **Look for "Custom: Sofabaton Hub"**
   - Description: "Smart remote control card for managing Sofabaton Hub activities and devices"
   - If you don't see it, try clearing browser cache (Ctrl+Shift+R or Cmd+Shift+R)
5. **Click on the card** to add it
6. **Select your remote entity** from the dropdown (e.g., `remote.sofabaton_hub_aabbccddeeff`)
7. **Click "Save"**

> **💡 Tip**: The card will automatically register as "Custom: Sofabaton Hub" in the card picker. Both the main card and detail card use the same registration name.

**Method 2: YAML Editor**

1. **Go to your dashboard** and click **"Edit Dashboard"** → **"⋮"** (three dots) → **"Raw configuration editor"**
2. **Add the following YAML**:

#### Main Card (Activity Switcher)

```yaml
type: custom:sofabaton-main-card
entity: remote.sofabaton_hub_aabbccddeeff
```

**Features:**
- Shows all configured activities
- Toggle switches to activate/deactivate activities
- Current activity highlighted
- Refresh button to reload data
- "More Info" button appears when an activity is running

#### Detail Card (Key Control)

The detail card is automatically shown when you click the "More Info" button on an active activity in the main card. You can also add it manually:

```yaml
type: custom:sofabaton-detail-card
entity: remote.sofabaton_hub_aabbccddeeff
```

**Features:**
- Tabbed interface for different key types (Assigned Keys, Macro Keys, Favorite Keys)
- Visual key buttons with labels
- Click keys to send commands
- Loading states during data fetch
- Ripple effect on key press

**Note**: Replace `aabbccddeeff` with your actual hub's MAC address (lowercase, no separators).

---

#### ❌ Common Mistakes to Avoid

**DON'T do this:**
```yaml
# ❌ This will NOT work!
type: entity
entity: remote.sofabaton_hub_aabbccddeeff
```

```yaml
# ❌ This will NOT work either!
type: button
entity: remote.sofabaton_hub_aabbccddeeff
```

**DO this:**
```yaml
# ✅ This is correct!
type: custom:sofabaton-main-card
entity: remote.sofabaton_hub_aabbccddeeff
```

---

### 🔍 How It Works

#### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Home Assistant                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Sofabaton Hub Integration                           │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │ Config Flow │  │ Coordinator  │  │   Remote   │  │  │
│  │  │  (Setup)    │  │ (Data Mgmt)  │  │  (Entity)  │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │  │
│  │         │                 │                 │        │  │
│  └─────────┼─────────────────┼─────────────────┼────────┘  │
│            │                 │                 │           │
│            │                 ▼                 │           │
│            │         ┌──────────────┐          │           │
│            │         │  MQTT Client │          │           │
│            │         └──────────────┘          │           │
│            │                 │                 │           │
│  ┌─────────┼─────────────────┼─────────────────┼────────┐  │
│  │         │                 │                 │        │  │
│  │  ┌──────▼──────┐  ┌───────▼────────┐  ┌────▼─────┐  │  │
│  │  │  Main Card  │  │  Detail Card   │  │  State   │  │  │
│  │  │ (Activity)  │  │  (Keys)        │  │  Object  │  │  │
│  │  └─────────────┘  └────────────────┘  └──────────┘  │  │
│  │   Lovelace UI                                       │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ MQTT
                            ▼
                  ┌──────────────────┐
                  │  MQTT Broker     │
                  └──────────────────┘
                            │
                            │ MQTT
                            ▼
                  ┌──────────────────┐
                  │  Sofabaton Hub   │
                  │  (Hardware)      │
                  └──────────────────┘
```

#### Component Details

##### 1. **Discovery (config_flow.py)**

- **mDNS/Zeroconf Discovery**: Listens for `_sofabaton_hub._udp.local.` service announcements
- **Automatic Configuration**: Extracts MAC address and MQTT broker information from mDNS TXT records
- **Manual Setup**: Allows users to manually enter connection details if discovery fails

##### 2. **Coordinator (coordinator.py)**

The coordinator is the central data management component:

- **MQTT Connection**: Connects to the MQTT broker and subscribes to relevant topics
- **Data Caching**: Maintains a local cache of activities, devices, and keys
- **Sequential Requests**: Implements a request queue to avoid overwhelming the hub
- **Debouncing**: Batches multiple updates within 500ms to reduce UI updates
- **State Management**: Tracks current activity and key data

**Key Features:**
- No periodic polling (MQTT push-based)
- Automatic reconnection on MQTT disconnection
- Request timeout handling (30 seconds)
- Duplicate message filtering

##### 3. **Remote Entity (remote.py)**

Implements the Home Assistant `remote` platform:

- **Entity State**: Reflects the current activity state (on/off)
- **Attributes**: Exposes activities, devices, keys, and current activity ID
- **Services**: Supports `turn_on`, `turn_off`, `send_command` services
- **Custom Commands**: Supports special commands like `request_basic_data`, `request_activity_keys`

##### 4. **Frontend Cards**

**Main Card (main-card.js):**
- Displays all activities as toggleable switches
- Shows current activity status
- Refresh button to reload data
- Opens detail card when clicking "More Info" on active activity

**Detail Card (detail-card.js):**
- Shows all keys for the selected activity
- Organized into tabs: Assigned Keys, Macro Keys, Favorite Keys
- Click keys to send commands
- Real-time loading states
- Periodic state check (every 5 seconds) when requesting data

#### Data Flow

##### Initial Setup Flow

```
1. User adds integration (auto-discovery or manual)
   ↓
2. Config Flow validates and creates config entry
   ↓
3. Integration loads → Coordinator initializes
   ↓
4. Coordinator connects to MQTT broker
   ↓
5. Coordinator subscribes to MQTT topics
   ↓
6. Coordinator requests basic data (activities + devices)
   ↓
7. Remote entity is created with initial state
   ↓
8. Frontend cards load and display data
```

##### Activity Switch Flow

```
1. User clicks activity switch in Main Card
   ↓
2. Frontend calls remote.turn_on service
   ↓
3. Remote entity publishes MQTT message to activity control topic
   ↓
4. Sofabaton Hub receives command and switches activity
   ↓
5. Hub publishes activity state change to MQTT
   ↓
6. Coordinator receives MQTT message
   ↓
7. Coordinator updates state (with 500ms debounce)
   ↓
8. Home Assistant pushes state update to frontend
   ↓
9. Main Card updates UI to reflect new state
```

##### Key Request Flow

```
1. User clicks "More Info" on active activity
   ↓
2. Detail Card opens and requests activity keys
   ↓
3. Frontend calls remote.send_command with "request_activity_keys"
   ↓
4. Coordinator clears old key data
   ↓
5. Coordinator starts sequential request:
   - Request assigned keys
   - Wait for response
   - Request macro keys
   - Wait for response
   - Request favorite keys
   - Wait for response
   ↓
6. Hub responds to each request via MQTT
   ↓
7. Coordinator receives responses and updates state
   ↓
8. Detail Card receives state updates and displays keys
   ↓
9. Periodic check (every 5 seconds) ensures data is loaded
```

##### Key Press Flow

```
1. User clicks a key in Detail Card
   ↓
2. Frontend calls remote.send_command with key ID
   ↓
3. Remote entity publishes MQTT message to key control topic
   ↓
4. Sofabaton Hub receives command and sends IR/RF signal
   ↓
5. Visual feedback shown in UI (ripple effect)
```

#### MQTT Topics

The integration uses the following MQTT topic structure (where `{mac}` is the hub's MAC address):

**Activities:**
- `activity/{mac}/list_request` - Request activity list
- `activity/{mac}/list` - Activity list response
- `activity/{mac}/activity_control_up` - Switch activity (publish)
- `activity/{mac}/activity_control_down` - Activity state change (subscribe)

**Keys:**
- `activity/{mac}/keys_request` - Request assigned keys
- `activity/{mac}/keys_list` - Assigned keys response
- `activity/{mac}/macro_keys_request` - Request macro keys
- `activity/{mac}/macro_keys_list` - Macro keys response
- `activity/{mac}/favorites_keys_request` - Request favorite keys
- `activity/{mac}/favorites_keys_list` - Favorite keys response

**Control:**
- `activity/{mac}/keys_control` - Send assigned key command
- `activity/{mac}/macro_keys_control` - Send macro key command
- `activity/{mac}/favorites_keys_control` - Send favorite key command

**Devices:**
- `device/{mac}/list_request` - Request device list
- `device/{mac}/list` - Device list response

---

### 🐛 Troubleshooting

#### Integration not discovered

1. Check that your Sofabaton Hub is on the same network
2. Verify mDNS/Zeroconf is enabled in Home Assistant
3. Try manual configuration instead

#### MQTT connection issues

1. Verify MQTT broker is running and accessible
2. Check MQTT credentials are correct
3. Check Home Assistant logs for connection errors

#### Keys not loading

1. Make sure the activity is active (turned on)
2. Check MQTT broker logs for message delivery
3. Wait up to 5 seconds for periodic state check
4. Try clicking the refresh button in Main Card

#### Cards not showing

1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Check browser console for JavaScript errors
3. Verify card resources are loaded in Developer Tools → Info

---

### ❓ FAQ

**Q: Does this integration work offline?**
A: Yes, as long as your Home Assistant, MQTT broker, and Sofabaton Hub are on the same local network. No internet connection is required.

**Q: Can I control multiple Sofabaton Hubs?**
A: Yes, you can add multiple hubs by repeating the configuration process for each device.

**Q: Why are my keys not loading immediately?**
A: The integration uses sequential requests to avoid overwhelming the hub. It may take a few seconds to load all keys (assigned, macro, and favorites). The frontend checks state every 5 seconds to ensure data is loaded.

**Q: Can I use this with Home Assistant automations?**
A: Yes! You can use the `remote.turn_on`, `remote.turn_off`, and `remote.send_command` services in your automations.

**Q: How do I send a specific key command in an automation?**
A: Use the `remote.send_command` service with the key ID:
```yaml
service: remote.send_command
target:
  entity_id: remote.sofabaton_hub_aabbccddeeff
data:
  command: "174"  # Key ID
```

**Q: What's the difference between assigned keys, macro keys, and favorite keys?**
A:
- **Assigned Keys**: Regular IR/RF keys assigned to devices in the activity
- **Macro Keys**: Custom sequences of multiple key presses
- **Favorite Keys**: Quick-access keys you've marked as favorites

**Q: Why does the integration use MQTT instead of direct HTTP API?**
A: The Sofabaton Hub uses MQTT for real-time communication. This allows for instant state updates and better responsiveness compared to polling-based HTTP APIs.

---

### 📋 Version History

**v2.3.4** (Current)
- Optimized frontend update logic to prevent duplicate renders
- Added data cleanup when requesting new activity keys
- Increased periodic state check interval from 1s to 5s
- Improved request timeout handling

**v2.3.x**
- Added sequential request mechanism for key data
- Implemented debouncing for state updates (500ms)
- Fixed dialog close issues
- Improved error handling and logging

**v2.x**
- Added custom Lovelace cards
- Implemented MQTT-based real-time updates
- Added support for macro and favorite keys

**v1.x**
- Initial release
- Basic activity control
- mDNS auto-discovery

---

### 🔧 Development

#### Project Structure

```
sofabaton_hub/
├── __init__.py              # Integration entry point
├── manifest.json            # Integration metadata
├── config_flow.py           # Configuration flow (discovery & setup)
├── coordinator.py           # Data coordinator (MQTT & state management)
├── remote.py                # Remote entity implementation
├── api.py                   # MQTT API client
├── const.py                 # Constants and MQTT topics
├── translations/            # Localization files
│   ├── en.json             # English translations
│   └── zh-Hans.json        # Simplified Chinese translations
└── www/                     # Frontend resources
    ├── cards.js            # Card registration
    ├── main-card.js        # Main activity card
    └── detail-card.js      # Detail key control card
```

#### Key Design Decisions

1. **No Periodic Polling**: The integration relies entirely on MQTT push notifications to reduce network traffic and improve responsiveness.

2. **Sequential Requests**: Key data requests are queued and executed sequentially to avoid overwhelming the hub with simultaneous requests.

3. **Debouncing**: Multiple MQTT messages within 500ms are batched into a single state update to reduce UI re-renders.

4. **Data Cleanup**: Old key data is cleared when requesting new activity keys to prevent memory growth and ensure frontend only sees current activity data.

5. **Periodic State Check**: Frontend checks state every 5 seconds when requesting keys to handle cases where MQTT push fails.

#### Debugging

Enable debug logging in Home Assistant's `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.sofabaton_hub: debug
```

Then check the logs in **Settings** → **System** → **Logs**.

---

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

#### Development Setup

1. Fork this repository
2. Clone your fork
3. Create a new branch for your feature
4. Make your changes
5. Test thoroughly
6. Submit a pull request

#### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Update documentation when adding features

---

### 📝 License

This project is licensed under the MIT License.

---

## 中文

### 📖 概述

这是一个 Home Assistant 自定义集成，允许您控制 Sofabaton Hub 万能遥控器。它提供了一个美观、功能丰富的界面，通过 MQTT 实现实时更新。

> **⚠️ 设备兼容性**
>
> 此集成仅适用于 **Sofabaton X2**。
>
> **不支持 Sofabaton X1s**（旧型号）。

**主要功能：**
- 🔍 **自动发现**：通过 mDNS/Zeroconf 自动发现网络上的 Sofabaton Hub 设备
- 🎮 **活动控制**：切换活动、查看和控制所有分配的按键
- 🔑 **按键管理**：查看每个活动的分配按键、宏按键和收藏按键
- 📱 **自定义界面**：美观的 Lovelace 卡片，实时更新
- 🔄 **实时更新**：基于 MQTT 的推送通知，即时状态变化
- 🌐 **双语支持**：支持英文和中文

---

### ⚙️ 前置条件

在安装此集成之前，您**必须**在 Home Assistant 中运行 MQTT 代理服务器。

#### 安装 Mosquitto Broker 加载项

1. **进入设置** → **加载项** → **加载项商店**
2. **搜索 "Mosquitto broker"**
3. **点击"安装"**
4. **安装完成后**，进入**配置**选项卡：
   - 设置用户名和密码（可选但推荐）
   - 配置示例：
     ```yaml
     logins:
       - username: mqtt_user
         password: your_secure_password
     ```
5. **点击"保存"**
6. **进入信息选项卡**，点击**"启动"**
7. **启用"开机启动"**和**"看门狗"**

#### 配置 MQTT 集成

1. **进入设置** → **设备与服务** → **集成**
2. **搜索 "MQTT"** 并添加
3. **配置**：
   - 代理：`localhost`（或您的 MQTT 代理 IP）
   - 端口：`1883`
   - 用户名：（您在 Mosquitto 中设置的用户名）
   - 密码：（您在 Mosquitto 中设置的密码）

**注意**：Sofabaton Hub 通过 MQTT 与 Home Assistant 通信。没有正常工作的 MQTT 代理，此集成将无法运行。

---

### 📦 安装

#### 方法 1：HACS（推荐）

1. 在 Home Assistant 中打开 HACS
2. 点击"集成"
3. 点击右上角的三个点
4. 选择"自定义存储库"
5. 添加此存储库 URL 并选择"集成"作为类别
6. 点击"安装"
7. 重启 Home Assistant

#### 方法 2：手动安装

1. 下载此存储库
2. 将 `sofabaton_hub` 文件夹复制到 Home Assistant 的 `custom_components` 目录：
   ```
   /config/custom_components/sofabaton_hub/
   ```
3. 重启 Home Assistant

---

### 🔧 配置

**重要**：在继续之前，请确保您已完成[前置条件](#️-前置条件)部分，并拥有正常工作的 MQTT 代理。

#### 自动发现（推荐）

1. 确保您的 Sofabaton Hub 与 Home Assistant 连接到同一网络
2. 进入 **设置** → **设备与服务** → **集成**
3. 您应该会看到 Sofabaton Hub 的"已发现"通知
4. 点击 **"配置"** 并按照设置向导操作
5. 输入您的 MQTT 代理凭据：
   - **MQTT 主机**：`localhost`（如果使用 Mosquitto 加载项）或您的代理 IP
   - **MQTT 端口**：`1883`（默认）
   - **用户名**：您在 Mosquitto 代理中设置的用户名
   - **密码**：您在 Mosquitto 代理中设置的密码

#### 手动配置

如果自动发现不起作用，您可以手动添加集成：

1. 进入 **设置** → **设备与服务** → **集成**
2. 点击 **"+ 添加集成"**
3. 搜索 **"Sofabaton Hub"**
4. 输入以下信息：
   - **MAC 地址**：您的 Sofabaton Hub 的 MAC 地址（例如：`AA:BB:CC:DD:EE:FF`）
   - **名称**：Hub 的友好名称（默认："Sofabaton Hub"）
   - **MQTT 主机**：`localhost`（如果使用 Mosquitto 加载项）或您的代理 IP
   - **MQTT 端口**：`1883`（默认）
   - **用户名**：您在 Mosquitto 代理中设置的用户名
   - **密码**：您在 Mosquitto 代理中设置的密码

**注意**：MQTT 凭据必须与您在 Mosquitto 代理加载项中配置的凭据匹配。

---

### 🎨 添加 Lovelace 卡片

安装后，您需要将自定义卡片添加到 Lovelace 仪表板。

> **⚠️ 重要提示：您必须使用此集成提供的自定义卡片！**
>
> **不要**使用默认的实体卡片、按钮卡片或任何其他通用卡片。它们无法正常工作，因为：
> - 自定义卡片处理复杂的 MQTT 通信和状态管理
> - 它们提供了活动切换和按键控制的专用界面
> - 通用卡片无法访问自定义功能（按键请求、活动切换等）

#### 如何添加卡片到仪表板

**方法 1：可视化编辑器（推荐）**

1. **进入您的仪表板**，点击右上角的**"编辑仪表板"**
2. **点击"+ 添加卡片"**按钮
3. **向下滚动**到**"Custom cards"（自定义卡片）**部分
4. **查找"Custom: Sofabaton Hub"**
   - 描述："Smart remote control card for managing Sofabaton Hub activities and devices"
   - 如果看不到，尝试清除浏览器缓存（Ctrl+Shift+R 或 Cmd+Shift+R）
5. **点击卡片**添加
6. **从下拉菜单选择您的遥控器实体**（例如：`remote.sofabaton_hub_aabbccddeeff`）
7. **点击"保存"**

> **💡 提示**：卡片会自动注册为"Custom: Sofabaton Hub"。主卡片和详情卡片使用相同的注册名称。

**方法 2：YAML 编辑器**

1. **进入您的仪表板**，点击**"编辑仪表板"** → **"⋮"**（三个点）→ **"原始配置编辑器"**
2. **添加以下 YAML**：

#### 主卡片（活动切换器）

```yaml
type: custom:sofabaton-main-card
entity: remote.sofabaton_hub_aabbccddeeff
```

**功能：**
- 显示所有配置的活动
- 切换开关以激活/停用活动
- 当前活动高亮显示
- 刷新按钮重新加载数据
- 活动运行时显示"更多信息"按钮

#### 详情卡片（按键控制）

详情卡片会在您点击主卡片中活动活动的"更多信息"按钮时自动显示。您也可以手动添加：

```yaml
type: custom:sofabaton-detail-card
entity: remote.sofabaton_hub_aabbccddeeff
```

**功能：**
- 不同按键类型的选项卡界面（分配按键、宏按键、收藏按键）
- 带标签的可视化按键按钮
- 点击按键发送命令
- 数据获取期间的加载状态
- 按键按下时的涟漪效果

**注意**：将 `aabbccddeeff` 替换为您实际 Hub 的 MAC 地址（小写，无分隔符）。

---

#### ❌ 常见错误避免

**不要这样做：**
```yaml
# ❌ 这样不行！
type: entity
entity: remote.sofabaton_hub_aabbccddeeff
```

```yaml
# ❌ 这样也不行！
type: button
entity: remote.sofabaton_hub_aabbccddeeff
```

**要这样做：**
```yaml
# ✅ 这样才对！
type: custom:sofabaton-main-card
entity: remote.sofabaton_hub_aabbccddeeff
```

---

### 🔍 工作原理

#### 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     Home Assistant                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Sofabaton Hub 集成                                  │  │
│  │                                                       │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │ 配置流程    │  │  协调器      │  │  遥控器    │  │  │
│  │  │  (设置)     │  │ (数据管理)   │  │  (实体)    │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │  │
│  │         │                 │                 │        │  │
│  └─────────┼─────────────────┼─────────────────┼────────┘  │
│            │                 │                 │           │
│            │                 ▼                 │           │
│            │         ┌──────────────┐          │           │
│            │         │ MQTT 客户端  │          │           │
│            │         └──────────────┘          │           │
│            │                 │                 │           │
│  ┌─────────┼─────────────────┼─────────────────┼────────┐  │
│  │         │                 │                 │        │  │
│  │  ┌──────▼──────┐  ┌───────▼────────┐  ┌────▼─────┐  │  │
│  │  │  主卡片     │  │  详情卡片      │  │  状态    │  │  │
│  │  │ (活动)      │  │  (按键)        │  │  对象    │  │  │
│  │  └─────────────┘  └────────────────┘  └──────────┘  │  │
│  │   Lovelace 界面                                     │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ MQTT
                            ▼
                  ┌──────────────────┐
                  │  MQTT 代理       │
                  └──────────────────┘
                            │
                            │ MQTT
                            ▼
                  ┌──────────────────┐
                  │  Sofabaton Hub   │
                  │  (硬件设备)      │
                  └──────────────────┘
```

#### 核心组件

##### 1. **发现机制 (config_flow.py)**

- **mDNS/Zeroconf 发现**：监听 `_sofabaton_hub._udp.local.` 服务广播
- **自动配置**：从 mDNS TXT 记录中提取 MAC 地址和 MQTT 代理信息
- **手动设置**：如果发现失败，允许用户手动输入连接详情

##### 2. **协调器 (coordinator.py)**

协调器是中央数据管理组件：

- **MQTT 连接**：连接到 MQTT 代理并订阅相关主题
- **数据缓存**：维护活动、设备和按键的本地缓存
- **串联请求**：实现请求队列以避免压垮 Hub
- **防抖处理**：将 500ms 内的多个更新批量处理以减少 UI 更新
- **状态管理**：跟踪当前活动和按键数据

**关键特性：**
- 无定期轮询（基于 MQTT 推送）
- MQTT 断开时自动重连
- 请求超时处理（30 秒）
- 重复消息过滤

##### 3. **遥控器实体 (remote.py)**

实现 Home Assistant `remote` 平台：

- **实体状态**：反映当前活动状态（开/关）
- **属性**：暴露活动、设备、按键和当前活动 ID
- **服务**：支持 `turn_on`、`turn_off`、`send_command` 服务
- **自定义命令**：支持特殊命令如 `request_basic_data`、`request_activity_keys`

##### 4. **前端卡片**

**主卡片 (main-card.js)：**
- 显示所有活动为可切换开关
- 显示当前活动状态
- 刷新按钮重新加载数据
- 点击活动活动的"更多信息"打开详情卡片

**详情卡片 (detail-card.js)：**
- 显示所选活动的所有按键
- 组织为选项卡：分配按键、宏按键、收藏按键
- 点击按键发送命令
- 实时加载状态
- 请求数据时定期状态检查（每 5 秒）

#### 数据流程

##### 初始设置流程

```
1. 用户添加集成（自动发现或手动）
   ↓
2. 配置流程验证并创建配置条目
   ↓
3. 集成加载 → 协调器初始化
   ↓
4. 协调器连接到 MQTT 代理
   ↓
5. 协调器订阅 MQTT 主题
   ↓
6. 协调器请求基础数据（活动 + 设备）
   ↓
7. 创建具有初始状态的遥控器实体
   ↓
8. 前端卡片加载并显示数据
```

##### 活动切换流程

```
1. 用户在主卡片中点击活动开关
   ↓
2. 前端调用 remote.turn_on 服务
   ↓
3. 遥控器实体发布 MQTT 消息到活动控制主题
   ↓
4. Sofabaton Hub 接收命令并切换活动
   ↓
5. Hub 发布活动状态变化到 MQTT
   ↓
6. 协调器接收 MQTT 消息
   ↓
7. 协调器更新状态（带 500ms 防抖）
   ↓
8. Home Assistant 推送状态更新到前端
   ↓
9. 主卡片更新 UI 以反映新状态
```

##### 按键请求流程

```
1. 用户点击活动活动的"更多信息"
   ↓
2. 详情卡片打开并请求活动按键
   ↓
3. 前端调用 remote.send_command 并传递 "request_activity_keys"
   ↓
4. 协调器清除旧按键数据
   ↓
5. 协调器启动串联请求：
   - 请求分配按键
   - 等待响应
   - 请求宏按键
   - 等待响应
   - 请求收藏按键
   - 等待响应
   ↓
6. Hub 通过 MQTT 响应每个请求
   ↓
7. 协调器接收响应并更新状态
   ↓
8. 详情卡片接收状态更新并显示按键
   ↓
9. 定期检查（每 5 秒）确保数据已加载
```

##### 按键按下流程

```
1. 用户在详情卡片中点击按键
   ↓
2. 前端调用 remote.send_command 并传递按键 ID
   ↓
3. 遥控器实体发布 MQTT 消息到按键控制主题
   ↓
4. Sofabaton Hub 接收命令并发送 IR/RF 信号
   ↓
5. UI 中显示视觉反馈（涟漪效果）
```

#### MQTT 主题

集成使用以下 MQTT 主题结构（其中 `{mac}` 是 Hub 的 MAC 地址）：

**活动：**
- `activity/{mac}/list_request` - 请求活动列表
- `activity/{mac}/list` - 活动列表响应
- `activity/{mac}/activity_control_up` - 切换活动（发布）
- `activity/{mac}/activity_control_down` - 活动状态变化（订阅）

**按键：**
- `activity/{mac}/keys_request` - 请求分配按键
- `activity/{mac}/keys_list` - 分配按键响应
- `activity/{mac}/macro_keys_request` - 请求宏按键
- `activity/{mac}/macro_keys_list` - 宏按键响应
- `activity/{mac}/favorites_keys_request` - 请求收藏按键
- `activity/{mac}/favorites_keys_list` - 收藏按键响应

**控制：**
- `activity/{mac}/keys_control` - 发送分配按键命令
- `activity/{mac}/macro_keys_control` - 发送宏按键命令
- `activity/{mac}/favorites_keys_control` - 发送收藏按键命令

**设备：**
- `device/{mac}/list_request` - 请求设备列表
- `device/{mac}/list` - 设备列表响应

#### 数据更新机制

- **后端**：不进行定时轮询，完全依赖 MQTT 推送（防抖延迟 500ms）
- **前端**：在请求按键数据时，每 5 秒检查一次状态（不触发后端拉取）
- **实时性**：MQTT 消息推送确保即时更新

---

### 🐛 故障排除

#### 集成未被发现

1. 检查 Sofabaton Hub 是否在同一网络
2. 验证 Home Assistant 中是否启用了 mDNS/Zeroconf
3. 尝试手动配置

#### MQTT 连接问题

1. 验证 MQTT 代理正在运行且可访问
2. 检查 MQTT 凭据是否正确
3. 检查 Home Assistant 日志中的连接错误

#### 按键未加载

1. 确保活动已激活（已打开）
2. 检查 MQTT 代理日志以查看消息传递
3. 等待最多 5 秒进行定期状态检查
4. 尝试点击主卡片中的刷新按钮

#### 卡片未显示

1. 清除浏览器缓存（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 检查浏览器控制台中的 JavaScript 错误
3. 在开发者工具 → 信息中验证卡片资源是否已加载

---

### ❓ 常见问题

**问：此集成是否可以离线工作？**
答：可以，只要您的 Home Assistant、MQTT 代理和 Sofabaton Hub 在同一本地网络上。不需要互联网连接。

**问：我可以控制多个 Sofabaton Hub 吗？**
答：可以，您可以为每个设备重复配置过程来添加多个 Hub。

**问：为什么我的按键没有立即加载？**
答：集成使用串联请求以避免压垮 Hub。加载所有按键（分配、宏和收藏）可能需要几秒钟。前端每 5 秒检查一次状态以确保数据已加载。

**问：我可以在 Home Assistant 自动化中使用此集成吗？**
答：可以！您可以在自动化中使用 `remote.turn_on`、`remote.turn_off` 和 `remote.send_command` 服务。

**问：如何在自动化中发送特定按键命令？**
答：使用 `remote.send_command` 服务并传递按键 ID：
```yaml
service: remote.send_command
target:
  entity_id: remote.sofabaton_hub_aabbccddeeff
data:
  command: "174"  # 按键 ID
```

**问：分配按键、宏按键和收藏按键有什么区别？**
答：
- **分配按键**：分配给活动中设备的常规 IR/RF 按键
- **宏按键**：多个按键按下的自定义序列
- **收藏按键**：您标记为收藏的快速访问按键

**问：为什么集成使用 MQTT 而不是直接 HTTP API？**
答：Sofabaton Hub 使用 MQTT 进行实时通信。这允许即时状态更新和比基于轮询的 HTTP API 更好的响应性。

---

### 📋 版本历史

**v2.3.4**（当前版本）
- 优化前端更新逻辑以防止重复渲染
- 请求新活动按键时添加数据清理
- 将定期状态检查间隔从 1 秒增加到 5 秒
- 改进请求超时处理

**v2.3.x**
- 添加按键数据的串联请求机制
- 实现状态更新的防抖处理（500ms）
- 修复对话框关闭问题
- 改进错误处理和日志记录

**v2.x**
- 添加自定义 Lovelace 卡片
- 实现基于 MQTT 的实时更新
- 添加对宏和收藏按键的支持

**v1.x**
- 初始版本
- 基本活动控制
- mDNS 自动发现

---

### 🔧 开发

#### 项目结构

```
sofabaton_hub/
├── __init__.py              # 集成入口点
├── manifest.json            # 集成元数据
├── config_flow.py           # 配置流程（发现和设置）
├── coordinator.py           # 数据协调器（MQTT 和状态管理）
├── remote.py                # 遥控器实体实现
├── api.py                   # MQTT API 客户端
├── const.py                 # 常量和 MQTT 主题
├── translations/            # 本地化文件
│   ├── en.json             # 英文翻译
│   └── zh-Hans.json        # 简体中文翻译
└── www/                     # 前端资源
    ├── cards.js            # 卡片注册
    ├── main-card.js        # 主活动卡片
    └── detail-card.js      # 详情按键控制卡片
```

#### 关键设计决策

1. **无定期轮询**：集成完全依赖 MQTT 推送通知以减少网络流量并提高响应性。

2. **串联请求**：按键数据请求排队并按顺序执行，以避免同时请求压垮 Hub。

3. **防抖处理**：500ms 内的多个 MQTT 消息批量处理为单个状态更新，以减少 UI 重新渲染。

4. **数据清理**：请求新活动按键时清除旧按键数据，以防止内存增长并确保前端只看到当前活动数据。

5. **定期状态检查**：请求按键时前端每 5 秒检查一次状态，以处理 MQTT 推送失败的情况。

#### 调试

在 Home Assistant 的 `configuration.yaml` 中启用调试日志：

```yaml
logger:
  default: info
  logs:
    custom_components.sofabaton_hub: debug
```

然后在 **设置** → **系统** → **日志** 中检查日志。

---

### 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

#### 开发设置

1. Fork 此存储库
2. 克隆您的 fork
3. 为您的功能创建新分支
4. 进行更改
5. 彻底测试
6. 提交 pull request

#### 代码风格

- Python 代码遵循 PEP 8
- 使用有意义的变量名
- 为复杂逻辑添加注释
- 添加功能时更新文档

---

### 📝 许可证

本项目采用 MIT 许可证。
