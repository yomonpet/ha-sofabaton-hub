import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit@2.8.0/index.js?module";

// Helper function: ensure entity_id is a string
function ensureEntityIdIsString(entityId) {
  if (Array.isArray(entityId)) {
    return entityId[0];
  }
  return entityId;
}

// Check if entity is Sofabaton Hub - by entity attributes rather than ID
function checkIfSofabatonHub(entityId, hass) {
  if (!hass || !entityId) return false;
  
  const stateObj = hass.states[entityId];
  if (!stateObj) return false;
  
  // Check if entity has Sofabaton Hub specific attributes
  const attributes = stateObj.attributes;
  
  // Sofabaton Hub entity should have these specific attributes
  return (
    // Check for activities attribute
    attributes.activities !== undefined ||
    // Check for devices attribute
    attributes.devices !== undefined ||
    // Check for current_activity_id attribute
    attributes.current_activity_id !== undefined ||
    // Check for assigned_keys and other key-related attributes
    attributes.assigned_keys !== undefined ||
    attributes.macro_keys !== undefined ||
    attributes.favorite_keys !== undefined ||
    // Check integration attribute (if exists)
    attributes.integration === 'sofabaton_hub' ||
    // Check device_class or other identifiers
    attributes.device_class === 'sofabaton' ||
    // Check if friendly_name contains sofabaton keyword
    (attributes.friendly_name && 
     attributes.friendly_name.toLowerCase().includes('sofabaton'))
  );
}

// Define remote control button layout and IDs
const REMOTE_LAYOUT = {
    // D-pad - cross layout with OK button in center
    dpad: [ 
        {key: 'up', grid: '1 / 2 / 2 / 3'}, 
        {key: 'left', grid: '2 / 1 / 3 / 2'}, 
        {key: 'ok', grid: '2 / 2 / 3 / 3'}, 
        {key: 'right', grid: '2 / 3 / 3 / 4'}, 
        {key: 'down', grid: '3 / 2 / 4 / 3'} 
    ],
    // Function keys - horizontal layout
    functions: [ {key: 'back'}, {key: 'home'}, {key: 'menu'} ],
    // Volume/Channel/Mute/Guide - 2x3 grid layout
    volume_channel: [
        // First row
        {key: 'volume_up', grid: '1 / 1 / 2 / 2'},
        {key: 'guide', grid: '1 / 2 / 2 / 3'}, 
        {key: 'channel_up', grid: '1 / 3 / 2 / 4'},
        // Second row
        {key: 'volume_down', grid: '2 / 1 / 3 / 2'},
        {key: 'mute', grid: '2 / 2 / 3 / 3'},
        {key: 'channel_down', grid: '2 / 3 / 3 / 4'}
    ],
    // Media control
    transport: [ {key: 'rewind'}, {key: 'play'}, {key: 'fast_forward'} ],
    transport_extra: [ {key: 'dvr'}, {key: 'pause'}, {key: 'exit'} ],
    // Color keys
    colors: [ {key: 'red'}, {key: 'green'}, {key: 'yellow'}, {key: 'blue'} ],
    // Custom keys
    customs: [ {key: 'a'}, {key: 'b'}, {key: 'c'} ]
};

// Version identifier: Simplified version v2.0 - No cache, always fresh data
console.log("Sofabaton Detail Card - Simplified Version v2.0 loaded - No cache, always fresh data");

// Define all remote control button mappings (consistent with const.py)
const REMOTE_KEYS = {
    // Direction keys and OK
    "up": {"id": 174, "icon": "mdi:arrow-up"},
    "down": {"id": 178, "icon": "mdi:arrow-down"},
    "left": {"id": 175, "icon": "mdi:arrow-left"},
    "right": {"id": 177, "icon": "mdi:arrow-right"},
    "ok": {"id": 176, "icon": "mdi:checkbox-blank-circle-outline"},
    // Function keys
    "back": {"id": 179, "icon": "mdi:arrow-u-left-top"},
    "home": {"id": 180, "icon": "mdi:home"},
    "menu": {"id": 181, "icon": "mdi:menu"},
    // Volume and channel
    "volume_up": {"id": 182, "icon": "mdi:volume-plus"},
    "volume_down": {"id": 185, "icon": "mdi:volume-minus"},
    "channel_up": {"id": 183, "icon": "mdi:chevron-up"},
    "channel_down": {"id": 186, "icon": "mdi:chevron-down"},
    "mute": {"id": 184, "icon": "mdi:volume-mute"},
    "guide": {"id": 157, "icon": "mdi:television-guide"},
    // Media control
    "rewind": {"id": 187, "icon": "mdi:rewind"},
    "play": {"id": 156, "icon": "mdi:play"},
    "fast_forward": {"id": 189, "icon": "mdi:fast-forward"},
    "dvr": {"id": 155, "text": "DVR"},
    "pause": {"id": 188, "icon": "mdi:pause"},
    "exit": {"id": 154, "text": "Exit"},
    // Color keys
    "red": {"id": 190, "color": "red"},
    "green": {"id": 191, "color": "green"},
    "yellow": {"id": 192, "color": "yellow"},
    "blue": {"id": 193, "color": "blue"},
    // Custom keys
    "a": {"id": 153, "text": "A"},
    "b": {"id": 152, "text": "B"},
    "c": {"id": 151, "text": "C"}
};

// Detail card class
class SofabatonDetailCard extends LitElement {

  // Define component styles
  static get styles() {
    return css`
      /* Overall container */
      .container {
        padding: 16px;
      }
      
      /* Current activity info styles */
      .current-activity {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        padding: 12px;
        background: var(--primary-color);
        color: var(--text-primary-color);
        border-radius: 8px;
        margin-bottom: 16px;
        text-align: center;
      }
      
      /* Page navigation styles */
      .page-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 16px;
        gap: 20px;
      }
      
      .page-nav ha-icon-button {
        --mdc-icon-button-size: 40px;
      }
      
      .page-nav span {
        font-weight: 500;
        min-width: 120px;
        text-align: center;
      }
      
      /* No activity state styles */
      .no-activity {
        text-align: center;
        padding: 32px;
        color: var(--secondary-text-color);
      }
      
      .no-activity ha-icon {
        font-size: 48px;
        margin-bottom: 16px;
      }
      
      .available-activities {
        margin-top: 24px;
        text-align: left;
      }
      
      .activity-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px;
        margin: 8px 0;
        background: var(--card-background-color);
        border-radius: 8px;
      }
      
      /* Main remote control container */
      .remote-layout {
        display: flex;
        flex-direction: column;
        gap: 20px;
        align-items: center;
        background: linear-gradient(145deg, #2c2c2c, #1a1a1a);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 
          0 8px 32px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      /* Button base styles */
      .key-wrapper {
        position: relative;
      }
      
      /* Icon and content centering styles */
      .key-wrapper ha-icon-button ha-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
      }
      
      /* Ensure all content within buttons is centered */
      .key-wrapper ha-icon-button > * {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0;
      }
      
      .key-wrapper ha-icon-button {
        background: linear-gradient(145deg, #3a3a3a, #2a2a2a);
        border-radius: 50%;
        --mdc-icon-button-size: 48px;
        box-shadow: 
          0 4px 8px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.1),
          inset 0 -1px 0 rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.15s ease;
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .key-wrapper ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #4a4a4a, #3a3a3a);
        transform: translateY(-1px);
        box-shadow: 
          0 6px 12px rgba(0, 0, 0, 0.4),
          inset 0 1px 0 rgba(255, 255, 255, 0.2);
      }
      
      .key-wrapper ha-icon-button:not([disabled]):active {
        background: linear-gradient(145deg, #2a2a2a, #1a1a1a);
        transform: translateY(1px);
        box-shadow: 
          0 2px 4px rgba(0, 0, 0, 0.2),
          inset 0 2px 4px rgba(0, 0, 0, 0.3);
      }
      
      .key-wrapper ha-icon-button[disabled] {
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a);
        opacity: 0.3;
        cursor: not-allowed;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
      }
      
      /* Direction key grid - cross layout */
      .dpad-grid {
        display: grid;
        grid-template-columns: 60px 60px 60px;
        grid-template-rows: 60px 60px 60px;
        place-items: center;
        gap: 4px;
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a);
        border-radius: 16px;
        padding: 8px;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.3);
      }
      
      /* OK button special styles */
      .key-wrapper[title="ok"] ha-icon-button { 
        --mdc-icon-button-size: 56px;
        background: linear-gradient(145deg, #4CAF50, #388E3C);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .key-wrapper[title="ok"] ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #66BB6A, #4CAF50);
      }
      
      /* Function key group */
      .key-group {
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
      }
      
      /* Volume channel area - 2x3 grid symmetric layout */
      .volume-channel-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        grid-template-rows: repeat(2, 1fr);
        gap: 12px;
        width: 100%;
        max-width: 240px;
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a);
        border-radius: 12px;
        padding: 16px;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.3);
        place-items: center;
      }
      .volume-channel-grid .key-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
      }
      
      /* Function key group styles */
      .key-group:nth-of-type(2) {
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a);
        border-radius: 12px;
        padding: 12px;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.3);
      }
      
      /* Volume button special styles */
      .key-wrapper[title="volume_up"] ha-icon-button:not([disabled]),
      .key-wrapper[title="volume_down"] ha-icon-button:not([disabled]) {
        background: linear-gradient(145deg, #9C27B0, #7B1FA2);
      }
      .key-wrapper[title="volume_up"] ha-icon-button:not([disabled]):hover,
      .key-wrapper[title="volume_down"] ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #BA68C8, #9C27B0);
      }
      
      /* Channel button special styles */
      .key-wrapper[title="channel_up"] ha-icon-button:not([disabled]),
      .key-wrapper[title="channel_down"] ha-icon-button:not([disabled]) {
        background: linear-gradient(145deg, #FF5722, #D84315);
      }
      .key-wrapper[title="channel_up"] ha-icon-button:not([disabled]):hover,
      .key-wrapper[title="channel_down"] ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #FF7043, #FF5722);
      }
      
      /* Guide button special styles */
      .key-wrapper[title="guide"] ha-icon-button:not([disabled]) {
        background: linear-gradient(145deg, #607D8B, #455A64);
      }
      .key-wrapper[title="guide"] ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #78909C, #607D8B);
      }
      
      /* Mute button */
      .key-wrapper[title="mute"] ha-icon-button:not([disabled]) {
        background: linear-gradient(145deg, #F44336, #D32F2F);
      }
      .key-wrapper[title="mute"] ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #EF5350, #F44336);
      }
      
      /* Media control key styles */
      .key-wrapper[title="play"] ha-icon-button:not([disabled]) {
        background: linear-gradient(145deg, #2196F3, #1976D2);
      }
      .key-wrapper[title="play"] ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #42A5F5, #2196F3);
      }
      
      .key-wrapper[title="pause"] ha-icon-button:not([disabled]) {
        background: linear-gradient(145deg, #FF9800, #F57C00);
      }
      .key-wrapper[title="pause"] ha-icon-button:not([disabled]):hover {
        background: linear-gradient(145deg, #FFB74D, #FF9800);
      }
      
      /* Partially enabled button styles */
      .key-wrapper.partial-enabled ha-icon-button {
        background: linear-gradient(145deg, #3a3a3a, #2a2a2a);
        opacity: 0.7;
        box-shadow: 
          0 2px 4px rgba(0, 0, 0, 0.2),
          inset 0 1px 0 rgba(255, 255, 255, 0.05);
      }
      .key-wrapper.partial-enabled ha-icon-button:hover {
        background: linear-gradient(145deg, #4a4a4a, #3a3a3a);
        opacity: 0.85;
      }
      
      /* Text button styles */
      .text-key {
        font-weight: bold;
        font-size: 12px;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        width: 100%;
      }
      
      /* Color button enhancement */
      .key-wrapper[title="red"] ha-icon-button {
        position: relative;
      }
      .key-wrapper[title="green"] ha-icon-button {
        position: relative;
      }
      .key-wrapper[title="yellow"] ha-icon-button {
        position: relative;
      }
      .key-wrapper[title="blue"] ha-icon-button {
        position: relative;
      }
      
      .key-wrapper[title="red"] .color-key {
        background: linear-gradient(145deg, #f44336, #d32f2f);
        box-shadow: 0 0 8px rgba(244, 67, 54, 0.5);
      }
      .key-wrapper[title="green"] .color-key {
        background: linear-gradient(145deg, #4caf50, #388e3c);
        box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
      }
      .key-wrapper[title="yellow"] .color-key {
        background: linear-gradient(145deg, #ffeb3b, #fbc02d);
        box-shadow: 0 0 8px rgba(255, 235, 59, 0.5);
      }
      .key-wrapper[title="blue"] .color-key {
        background: linear-gradient(145deg, #2196f3, #1976d2);
        box-shadow: 0 0 8px rgba(33, 150, 243, 0.5);
      }
      
      .color-key {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
          0 2px 4px rgba(0, 0, 0, 0.3),
          inset 0 1px 2px rgba(255, 255, 255, 0.2);
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
      }
      
      /* Status message styles */
      .status-message {
        margin: 16px 0;
      }
      .warning-message, .info-message {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 8px;
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
      }
      .warning-message {
        background: rgba(244, 67, 54, 0.1);
        border-color: rgba(244, 67, 54, 0.3);
      }
      
      /* Loading hint styles */
      .loading-hint {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        margin-bottom: 12px;
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid rgba(33, 150, 243, 0.3);
        border-radius: 6px;
        font-size: 14px;
        opacity: 0.8;
      }
      .remote-layout.loading {
        opacity: 0.6;
      }
      
      /* Loading message styles */
      .loading-message {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        padding: 32px;
        text-align: center;
        color: var(--secondary-text-color);
      }
      
      .loading-message ha-icon {
        font-size: 48px;
        margin-bottom: 8px;
      }
      
      /* Rotation animation */
      .spinning {
        animation: spin 1s linear infinite;
      }
      
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      
      /* Macro and favorite command grid layout */
      .macro-grid, .favorite-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        padding: 20px;
        background: linear-gradient(145deg, #2c2c2c, #1a1a1a);
        border-radius: 16px;
        box-shadow: 
          0 8px 24px rgba(0, 0, 0, 0.3),
          inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
      }
      
      /* Macro button styles */
      .macro-button, .favorite-button {
        aspect-ratio: 2.5 / 1;  /* Rectangle aspect ratio */
        min-height: 50px;
        background: #ffffff;  /* White background */
        border: 2px solid #e0e0e0;
        border-radius: 8px;  /* Rounded rectangle */
        color: #333333;  /* Black text */
        font-weight: 500;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 
          0 2px 4px rgba(0, 0, 0, 0.1),
          0 1px 2px rgba(0, 0, 0, 0.06);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 12px 16px;
        word-wrap: break-word;
        hyphens: auto;
      }
      
      .macro-button:hover, .favorite-button:hover {
        background: #f5f5f5;  /* Light gray hover */
        border-color: #d0d0d0;
        transform: translateY(-1px);
        box-shadow: 
          0 4px 8px rgba(0, 0, 0, 0.15),
          0 2px 4px rgba(0, 0, 0, 0.1);
      }
      
      .macro-button:active, .favorite-button:active {
        background: #e8e8e8;  /* Darker gray pressed */
        border-color: #c0c0c0;
        transform: translateY(0px);
        box-shadow: 
          0 1px 2px rgba(0, 0, 0, 0.1),
          inset 0 1px 2px rgba(0, 0, 0, 0.1);
      }
      
      /* Button click ripple effect */
      .macro-button::before, .favorite-button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(0, 0, 0, 0.1);  /* Black ripple suitable for white background */
        transform: translate(-50%, -50%);
        transition: width 0.3s, height 0.3s;
      }
      
      .macro-button.ripple::before, .favorite-button.ripple::before {
        width: 100px;
        height: 100px;
      }
      
      /* Responsive design */
      @media (max-width: 480px) {
        .macro-grid, .favorite-grid {
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
          padding: 16px;
        }
        .macro-button, .favorite-button {
          min-height: 45px;
          font-size: 12px;
          padding: 8px 12px;
        }
      }
      
      @media (max-width: 320px) {
        .macro-grid, .favorite-grid {
          grid-template-columns: 1fr;
        }
        .macro-button, .favorite-button {
          min-height: 40px;
          font-size: 11px;
        }
      }
    `;
  }

  // Define component properties
  static get properties() {
    return {
      hass: { type: Object },
      stateObj: { type: Object, attribute: false }, // Entity object - disable attribute reflection (kept for initial setup)
      entityId: { type: String }, // Entity ID to track
      selectedActivityId: { type: Number }, // 从main-card传递的选中活动ID
      _currentPage: { type: Number, state: true }, // Internal state: current page
      _isRequestingPage1: { type: Boolean, state: true }, // Page 1 (assigned_keys) request state
      _isRequestingPage2: { type: Boolean, state: true }, // Page 2 (macro_keys) request state
      _isRequestingPage3: { type: Boolean, state: true }, // Page 3 (favorite_keys) request state
    };
  }

  // Constructor
  constructor() {
    super();
    this._currentPage = 1; // Default to first page
    this._isRequestingPage1 = false; // Page 1 request state
    this._isRequestingPage2 = false; // Page 2 request state
    this._isRequestingPage3 = false; // Page 3 request state
    this._isRefreshingState = false; // Flag to prevent infinite refresh loops
  }

  // Get the latest state object from hass.states
  _getLatestStateObj() {
    // If we have entityId, always get the latest state from hass.states
    if (this.entityId && this.hass && this.hass.states) {
      const latestState = this.hass.states[this.entityId];
      if (latestState) {
        return latestState;
      }
    }
    // Fallback to the static stateObj
    return this.stateObj;
  }

  // Called when component is connected to DOM
  connectedCallback() {
    super.connectedCallback();

    // Reset disconnected flag
    this._isDisconnected = false;

    console.log("Detail card connected - page:", this._currentPage);
    console.log("🎯 Detail card connected with selectedActivityId:", this.selectedActivityId);

    // Set entityId from stateObj if available
    if (this.stateObj && this.stateObj.entity_id) {
      this.entityId = this.stateObj.entity_id;
      console.log("📌 Set entityId:", this.entityId);
    }

    // Note: We don't need to manually subscribe to state_changed events
    // because Home Assistant automatically updates the `hass` property,
    // which triggers the `updated()` lifecycle method where we handle state changes.

    // Listen for activity change events from main-card
    this._activityChangeListener = (e) => {
      if (e.detail && e.detail.entityId === this.entityId) {
        console.log("🎯 Detail card: Received activity change event, new selectedActivityId:", e.detail.selectedActivityId);
        const oldActivityId = this.selectedActivityId;
        this.selectedActivityId = e.detail.selectedActivityId;

        // If activity changed, request fresh data for current page
        if (oldActivityId !== this.selectedActivityId) {
          console.log("🎯 Detail card: Activity changed from", oldActivityId, "to", this.selectedActivityId);
          this._requestKeysForCurrentPage();
        }
      }
    };
    document.addEventListener("sofabaton-activity-changed", this._activityChangeListener);

    // Always force refresh when dialog opens to get latest data
    this._requestKeysForCurrentPage(true);

    // Monitor hass.states changes for debugging
    this._monitorStateChanges();

    // If initial request failed due to missing hass/stateObj, retry after a short delay
    if (!this.hass || !this.stateObj) {
      console.log("⏰ Initial request failed, will retry in 100ms");
      this._retryTimeout = setTimeout(() => {
        // Skip if component is disconnected
        if (this._isDisconnected) {
          console.log("⏰ Initial retry callback - skipping, component is disconnected");
          this._retryTimeout = null;
          return;
        }

        console.log("⏰ Retry attempt - hass:", !!this.hass, "stateObj:", !!this.stateObj);
        this._requestKeysForCurrentPage();
        this._retryTimeout = null;
      }, 100);
    }
  }

  // Called when component is disconnected from DOM
  disconnectedCallback() {
    super.disconnectedCallback();

    // Set disconnected flag to prevent any further operations
    this._isDisconnected = true;

    // Clean up request state
    this._isRequestingPage1 = false;
    this._isRequestingPage2 = false;
    this._isRequestingPage3 = false;

    // Clean up activity change listener
    if (this._activityChangeListener) {
      document.removeEventListener("sofabaton-activity-changed", this._activityChangeListener);
      this._activityChangeListener = null;
    }

    // Clean up periodic state check intervals for all pages
    if (this._stateCheckIntervalPage1) {
      console.log("🧹 Clearing page 1 periodic state check interval");
      clearInterval(this._stateCheckIntervalPage1);
      this._stateCheckIntervalPage1 = null;
    }
    if (this._stateCheckIntervalPage2) {
      console.log("🧹 Clearing page 2 periodic state check interval");
      clearInterval(this._stateCheckIntervalPage2);
      this._stateCheckIntervalPage2 = null;
    }
    if (this._stateCheckIntervalPage3) {
      console.log("🧹 Clearing page 3 periodic state check interval");
      clearInterval(this._stateCheckIntervalPage3);
      this._stateCheckIntervalPage3 = null;
    }

    // Clean up state monitor interval
    if (this._stateMonitorInterval) {
      console.log("🧹 Clearing state monitor interval");
      clearInterval(this._stateMonitorInterval);
      this._stateMonitorInterval = null;
    }

    // Clean up all pending timeouts for all pages
    if (this._requestTimeoutPage1) {
      console.log("🧹 Clearing page 1 request timeout");
      clearTimeout(this._requestTimeoutPage1);
      this._requestTimeoutPage1 = null;
    }
    if (this._requestTimeoutPage2) {
      console.log("🧹 Clearing page 2 request timeout");
      clearTimeout(this._requestTimeoutPage2);
      this._requestTimeoutPage2 = null;
    }
    if (this._requestTimeoutPage3) {
      console.log("🧹 Clearing page 3 request timeout");
      clearTimeout(this._requestTimeoutPage3);
      this._requestTimeoutPage3 = null;
    }

    // Clean up retry timeout
    if (this._retryTimeout) {
      console.log("🧹 Clearing retry timeout");
      clearTimeout(this._retryTimeout);
      this._retryTimeout = null;
    }

    // Notify backend to clear _is_requesting_keys flag
    // This allows activity_list updates to proceed normally after dialog is closed
    if (this.hass && this.stateObj) {
      console.log("🔓 Notifying backend to clear _is_requesting_keys flag");
      this.hass.callService("remote", "send_command", {
        entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
        command: ["type:clear_requesting_keys_flag"],
      }).catch(error => {
        console.error("❌ Error clearing _is_requesting_keys flag:", error);
      });
    }

    console.log("🔌 Detail card disconnected - cleaned up all resources");
  }

  // Decide whether update is needed
  shouldUpdate(changedProperties) {
    // Always update if hass or stateObj changes
    if (changedProperties.has('hass') || changedProperties.has('stateObj')) {
      return true;
    }
    
    // Update if selectedActivityId changes
    if (changedProperties.has('selectedActivityId')) {
      const oldValue = changedProperties.get('selectedActivityId');
      const newValue = this.selectedActivityId;
      console.log("🎯 selectedActivityId changed:", oldValue, "→", newValue);

      // Only request fresh data if the value actually changed
      if (oldValue !== newValue && newValue) {
        console.log("🎯 Requesting fresh data for new selectedActivityId:", newValue);
        this._requestKeysForCurrentActivity();
      }
      return true;
    }
    
    // Also update if internal state changes
    if (changedProperties.has('_currentPage') ||
        changedProperties.has('_isRequestingPage1') ||
        changedProperties.has('_isRequestingPage2') ||
        changedProperties.has('_isRequestingPage3')) {
      return true;
    }
    
    return super.shouldUpdate(changedProperties);
  }

  // Helper method to get current state from hass
  _getCurrentState() {
    // Use the new method to get the latest state
    const latestState = this._getLatestStateObj();

    if (!latestState) return null;

    // Log the state retrieval for debugging
    console.log("🔍 _getCurrentState:");
    console.log("🔍   entity_id:", latestState.entity_id);
    console.log("🔍   latestState.last_changed:", latestState.last_changed);
    console.log("🔍   latestState.last_updated:", latestState.last_updated);

    // Parse the timestamp to check if it's recent
    if (latestState.last_updated) {
      const lastUpdatedTime = new Date(latestState.last_updated);
      const now = new Date();
      const ageSeconds = (now - lastUpdatedTime) / 1000;
      console.log("🔍   State age:", ageSeconds.toFixed(1), "seconds");
      console.log("🔍   Current time:", now.toISOString());
      console.log("🔍   Last updated:", lastUpdatedTime.toISOString());
    }

    console.log("🔍   latestState.attributes.assigned_keys:", latestState.attributes?.assigned_keys);

    return latestState;
  }

  // Force refresh the entity state from Home Assistant
  async _forceRefreshState() {
    if (!this.hass || !this.stateObj) return;

    // Prevent infinite refresh loops
    if (this._isRefreshingState) {
      console.log("🔄 Already refreshing state, skipping...");
      return;
    }

    this._isRefreshingState = true;

    try {
      // Method 1: Call the update_entity service
      console.log("🔄 Calling homeassistant.update_entity for:", this.stateObj.entity_id);
      await this.hass.callService('homeassistant', 'update_entity', {
        entity_id: this.stateObj.entity_id
      });
      console.log("✅ Entity state refresh requested");

      // Wait a bit for the state to update
      await new Promise(resolve => setTimeout(resolve, 300));

      // Method 2: Directly fetch the latest state from Home Assistant
      if (this.hass.connection) {
        console.log("🔄 Fetching latest state directly from Home Assistant...");
        const states = await this.hass.connection.sendMessagePromise({
          type: 'get_states'
        });

        const latestState = states.find(s => s.entity_id === this.stateObj.entity_id);
        if (latestState) {
          console.log("✅ Got latest state from Home Assistant:");
          console.log("   last_updated:", latestState.last_updated);
          console.log("   assigned_keys:", latestState.attributes?.assigned_keys);

          // Update our stateObj with the latest state
          this.stateObj = latestState;

          // Also update hass.states to keep it in sync
          this.hass.states[this.stateObj.entity_id] = latestState;
        } else {
          console.log("⚠️ Could not find entity in states response");
        }
      }

      // Trigger a re-render to pick up the new state
      this.requestUpdate();
      console.log("🔄 Re-render triggered after state refresh");
    } catch (error) {
      console.error("❌ Error refreshing entity state:", error);
    } finally {
      this._isRefreshingState = false;
    }
  }

  // Called when properties are updated
  updated(changedProperties) {
    super.updated(changedProperties);

    console.log("🔍 updated() called - changed properties:", Array.from(changedProperties.keys()));

    if (changedProperties.has('stateObj')) {
      console.log("� Frontend received stateObj update");
      console.log("� stateObj reference:", this.stateObj);
      console.log("� stateObj.entity_id:", this.stateObj?.entity_id);
      console.log("� stateObj.state:", this.stateObj?.state);
      console.log("� stateObj.attributes:", this.stateObj?.attributes);
      console.log("📥 Current stateObj.attributes.assigned_keys:", this.stateObj?.attributes?.assigned_keys);
      console.log("� Current stateObj.attributes.macro_keys:", this.stateObj?.attributes?.macro_keys);
      console.log("� Current stateObj.attributes.favorite_keys:", this.stateObj?.attributes?.favorite_keys);
    }

    if (changedProperties.has('hass')) {
      console.log("📥 Frontend received hass update");
      console.log("📥 hass timestamp:", new Date().toISOString());

      // Get the latest state from hass.states
      const currentState = this._getCurrentState();
      if (currentState) {
        console.log("📥 Current state from hass.states:");
        console.log("📥   last_updated:", currentState.last_updated);
        console.log("📥   assigned_keys:", currentState.attributes?.assigned_keys);
        console.log("📥   macro_keys:", currentState.attributes?.macro_keys);
        console.log("📥   favorite_keys:", currentState.attributes?.favorite_keys);

        // Update stateObj with the latest state from hass.states
        // This ensures we always have the most up-to-date data
        if (this.stateObj && currentState.entity_id === this.stateObj.entity_id) {
          const oldLastUpdated = this.stateObj.last_updated;
          const newLastUpdated = currentState.last_updated;
          const oldAssignedKeys = this.stateObj.attributes?.assigned_keys;
          const newAssignedKeys = currentState.attributes?.assigned_keys;

          console.log("📥 Comparing states:");
          console.log("📥   Old last_updated:", oldLastUpdated);
          console.log("📥   New last_updated:", newLastUpdated);
          console.log("📥   Old assigned_keys:", oldAssignedKeys);
          console.log("📥   New assigned_keys:", newAssignedKeys);

          // Check if state has actually changed
          if (newLastUpdated !== oldLastUpdated ||
              JSON.stringify(oldAssignedKeys) !== JSON.stringify(newAssignedKeys)) {
            console.log("� Frontend: State changed! Updating stateObj");
            console.log("�   last_updated changed:", newLastUpdated !== oldLastUpdated);
            console.log("�   assigned_keys changed:", JSON.stringify(oldAssignedKeys) !== JSON.stringify(newAssignedKeys));

            // Update stateObj with the latest state
            this.stateObj = currentState;
          } else {
            console.log("⏰ No state change detected in hass update");
          }
        }
      } else {
        console.warn("⚠️ Entity state not found in hass.states");
      }

      // Check request completion whenever hass updates
      const isRequesting = this._isRequestingPage1 || this._isRequestingPage2 || this._isRequestingPage3;
      if (isRequesting) {
        console.log("📥 hass updated while requesting - checking completion");
        this._checkRequestCompletion();
      }
    }
  }

  // Check if request is completed
  async _checkRequestCompletion() {
    // Skip if component is disconnected
    if (this._isDisconnected) {
      console.log("🔍 _checkRequestCompletion - skipping, component is disconnected");
      return;
    }

    console.log("🔍 _checkRequestCompletion called");
    const isRequesting = this._isRequestingPage1 || this._isRequestingPage2 || this._isRequestingPage3;
    console.log("🔍   isRequesting:", isRequesting, "page:", this._currentPage);

    if (!isRequesting) {
      console.log("🔍   Skipping - not requesting");
      return;
    }

    // Get the latest state from hass.states (no need to force refresh, hass updates automatically)
    const currentState = this._getCurrentState();
    if (!currentState) {
      console.log("�   Skipping - no current state");
      return;
    }

    console.log("�   Current state:", currentState);
    console.log("Checking request completion - page:", this._currentPage);

    const attributes = currentState.attributes;
    console.log("🔍   attributes:", attributes);
    console.log("🔍   attributes.assigned_keys:", attributes.assigned_keys);

    const currentActivityId = attributes.current_activity_id;
    const activities = attributes.activities || [];

    // Check if there's a running activity
    const activeActivity = activities.find(a => a.state === 'on');
    // 优先使用从main-card传递的selectedActivityId，其次使用currentActivityId，最后使用运行中的活动
    const effectiveActivityId = this.selectedActivityId || currentActivityId || (activeActivity ? activeActivity.id : null);

    console.log("Request completion check - selectedActivityId:", this.selectedActivityId, "effectiveActivityId:", effectiveActivityId);

    if (effectiveActivityId) {
      const assignedKeys = attributes.assigned_keys?.[effectiveActivityId];
      const macroKeys = attributes.macro_keys?.[effectiveActivityId];
      const favoriteKeys = attributes.favorite_keys?.[effectiveActivityId];

      console.log("Checking completion for activity", effectiveActivityId, "page", this._currentPage);
      console.log("  assigned_keys:", assignedKeys?.length || 0, "keys");
      console.log("  macro_keys:", macroKeys?.length || 0, "keys");
      console.log("  favorite_keys:", favoriteKeys?.length || 0, "keys");

      // Check completion based on current page
      // Must check both: data exists AND data was updated after request was sent
      let hasResponse = false;
      let keyType = '';

      if (this._currentPage === 1) {
        const hasData = attributes.assigned_keys && attributes.assigned_keys.hasOwnProperty(effectiveActivityId);
        const requestTimestamp = this._requestTimestampPage1;
        const dataUpdatedAfterRequest = requestTimestamp && currentState.last_updated > requestTimestamp;
        hasResponse = hasData && dataUpdatedAfterRequest;
        keyType = 'assigned_keys';
        console.log(`🔍 Page 1 completion check:`, {
          'hasData': hasData,
          'requestTimestamp': requestTimestamp,
          'last_updated': currentState.last_updated,
          'dataUpdatedAfterRequest': dataUpdatedAfterRequest,
          'hasResponse': hasResponse
        });
      } else if (this._currentPage === 2) {
        const hasData = attributes.macro_keys && attributes.macro_keys.hasOwnProperty(effectiveActivityId);
        const requestTimestamp = this._requestTimestampPage2;
        const dataUpdatedAfterRequest = requestTimestamp && currentState.last_updated > requestTimestamp;
        hasResponse = hasData && dataUpdatedAfterRequest;
        keyType = 'macro_keys';
        console.log(`🔍 Page 2 completion check:`, {
          'hasData': hasData,
          'requestTimestamp': requestTimestamp,
          'last_updated': currentState.last_updated,
          'dataUpdatedAfterRequest': dataUpdatedAfterRequest,
          'hasResponse': hasResponse
        });
      } else if (this._currentPage === 3) {
        const hasData = attributes.favorite_keys && attributes.favorite_keys.hasOwnProperty(effectiveActivityId);
        const requestTimestamp = this._requestTimestampPage3;
        const dataUpdatedAfterRequest = requestTimestamp && currentState.last_updated > requestTimestamp;
        hasResponse = hasData && dataUpdatedAfterRequest;
        keyType = 'favorite_keys';
        console.log(`🔍 Page 3 completion check:`, {
          'hasData': hasData,
          'requestTimestamp': requestTimestamp,
          'last_updated': currentState.last_updated,
          'dataUpdatedAfterRequest': dataUpdatedAfterRequest,
          'hasResponse': hasResponse
        });
      }

      console.log(`Check completion - page ${this._currentPage}, keyType: ${keyType}, hasResponse: ${hasResponse}`);

      if (hasResponse) {
        console.log(`✅ Frontend: Page ${this._currentPage} request completed for activity ${effectiveActivityId}`);

        // Clear requesting state for current page
        if (this._currentPage === 1) {
          this._isRequestingPage1 = false;
        } else if (this._currentPage === 2) {
          this._isRequestingPage2 = false;
        } else if (this._currentPage === 3) {
          this._isRequestingPage3 = false;
        }

        // Clean up periodic state check for this page
        const intervalKey = `_stateCheckIntervalPage${this._currentPage}`;
        if (this[intervalKey]) {
          console.log(`🔄 Cleaning up periodic state check for page ${this._currentPage}`);
          clearInterval(this[intervalKey]);
          this[intervalKey] = null;
        }

        this.requestUpdate(); // Trigger re-render
      } else {
        console.log(`⏳ Frontend: Still waiting for ${keyType} response for activity ${effectiveActivityId}`);
      }
    } else {
      console.log("❌ No effective activity ID found, cannot complete request");
    }
  }

  // Monitor hass.states changes for debugging
  _monitorStateChanges() {
    if (!this.hass || !this.stateObj) {
      return;
    }

    const entityId = this.stateObj.entity_id;
    const initialState = this.hass.states[entityId];
    const initialLastUpdated = initialState?.last_updated;

    console.log(`🔍 Starting state monitoring for ${entityId}`);
    console.log(`🔍 Initial last_updated: ${initialLastUpdated}`);

    // Check every 1 second for state changes
    this._stateMonitorInterval = setInterval(() => {
      if (this._isDisconnected) {
        clearInterval(this._stateMonitorInterval);
        return;
      }

      const currentState = this.hass.states[entityId];
      const currentLastUpdated = currentState?.last_updated;

      if (currentLastUpdated !== initialLastUpdated) {
        console.log(`🎉 STATE CHANGED! last_updated changed from ${initialLastUpdated} to ${currentLastUpdated}`);
        console.log(`🎉 New assigned_keys:`, currentState.attributes.assigned_keys);
        clearInterval(this._stateMonitorInterval);
      }
    }, 1000);
  }

  // Request key data for current page (on-demand loading)
  _requestKeysForCurrentPage(forceRefresh = false) {
    // Skip if component is disconnected
    if (this._isDisconnected) {
      console.log("🔍 _requestKeysForCurrentPage - skipping, component is disconnected");
      return;
    }

    console.log("🔍 _requestKeysForCurrentPage called - page:", this._currentPage, "forceRefresh:", forceRefresh, "hass:", !!this.hass, "stateObj:", !!this.stateObj);

    if (!this.hass || !this.stateObj) {
      console.log("❌ Cannot request keys - missing hass or stateObj");
      return;
    }

    const attributes = this.stateObj.attributes;
    const currentActivityId = attributes.current_activity_id;
    const activities = attributes.activities || [];

    // Check if there's a running activity
    const activeActivity = activities.find(a => a.state === 'on');
    // 优先使用从main-card传递的selectedActivityId，其次使用currentActivityId，最后使用运行中的活动
    const effectiveActivityId = this.selectedActivityId || currentActivityId || (activeActivity ? activeActivity.id : null);

    console.log("🔍 Activity check - selectedActivityId:", this.selectedActivityId, "currentActivityId:", currentActivityId, "effectiveActivityId:", effectiveActivityId);

    if (!effectiveActivityId) {
      console.log("❌ No active activity, skipping key request");
      return;
    }

    // Determine which request to make based on current page
    let requestType, isRequesting, hasData;
    if (this._currentPage === 1) {
      requestType = 'request_assigned_keys';
      isRequesting = this._isRequestingPage1;
      hasData = attributes.assigned_keys && attributes.assigned_keys.hasOwnProperty(effectiveActivityId);
      console.log(`🔍 Page 1 check - hasData: ${hasData}, assigned_keys:`, attributes.assigned_keys, `effectiveActivityId: ${effectiveActivityId}`);
    } else if (this._currentPage === 2) {
      requestType = 'request_macro_keys';
      isRequesting = this._isRequestingPage2;
      hasData = attributes.macro_keys && attributes.macro_keys.hasOwnProperty(effectiveActivityId);
      console.log(`🔍 Page 2 check - hasData: ${hasData}, macro_keys:`, attributes.macro_keys, `effectiveActivityId: ${effectiveActivityId}`);
    } else if (this._currentPage === 3) {
      requestType = 'request_favorite_keys';
      isRequesting = this._isRequestingPage3;
      hasData = attributes.favorite_keys && attributes.favorite_keys.hasOwnProperty(effectiveActivityId);
      console.log(`🔍 Page 3 check - hasData: ${hasData}, favorite_keys:`, attributes.favorite_keys, `effectiveActivityId: ${effectiveActivityId}`);
    }

    // Skip if data already exists for this page (unless force refresh)
    if (hasData && !forceRefresh) {
      console.log(`✅ Page ${this._currentPage} data already exists for activity ${effectiveActivityId}, skipping request`);
      return;
    }

    if (forceRefresh && hasData) {
      console.log(`🔄 Force refresh - requesting fresh data even though cache exists`);
    }

    // Skip if already requesting for this page
    if (isRequesting) {
      console.log(`❌ Page ${this._currentPage} request already in progress, skipping duplicate request`);
      return;
    }

    console.log(`🚀 Frontend: Requesting ${requestType} for activity ${effectiveActivityId} (page ${this._currentPage})`);

    // Set requesting state for current page and record request timestamp
    if (this._currentPage === 1) {
      this._isRequestingPage1 = true;
      this._requestTimestampPage1 = new Date().toISOString();
      console.log(`📝 Recording request timestamp for page 1: ${this._requestTimestampPage1}`);
    } else if (this._currentPage === 2) {
      this._isRequestingPage2 = true;
      this._requestTimestampPage2 = new Date().toISOString();
      console.log(`📝 Recording request timestamp for page 2: ${this._requestTimestampPage2}`);
    } else if (this._currentPage === 3) {
      this._isRequestingPage3 = true;
      this._requestTimestampPage3 = new Date().toISOString();
      console.log(`📝 Recording request timestamp for page 3: ${this._requestTimestampPage3}`);
    }

    this.requestUpdate(); // Trigger re-render to show loading state

    // Start periodic state checking while request is active
    this._startPeriodicStateCheck(effectiveActivityId, this._currentPage);

    // Send request
    console.log("📤 Frontend: Calling send_command service");
    console.log("📤   entity_id:", ensureEntityIdIsString(this.stateObj.entity_id));
    console.log("📤   command:", [`type:${requestType}`, `activity_id:${effectiveActivityId}`]);

    this.hass.callService("remote", "send_command", {
      entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
      command: [`type:${requestType}`, `activity_id:${effectiveActivityId}`],
    }).then(() => {
      console.log(`✅ ${requestType} service called successfully`);
    }).catch(error => {
      console.error(`❌ Error calling ${requestType} service:`, error);
      // Clear requesting state on error
      if (this._currentPage === 1) {
        this._isRequestingPage1 = false;
      } else if (this._currentPage === 2) {
        this._isRequestingPage2 = false;
      } else if (this._currentPage === 3) {
        this._isRequestingPage3 = false;
      }
      this.requestUpdate();
    });

    // Set a timeout to stop requesting state after 30 seconds
    const timeoutKey = `_requestTimeoutPage${this._currentPage}`;
    if (this[timeoutKey]) {
      clearTimeout(this[timeoutKey]);
    }

    this[timeoutKey] = setTimeout(() => {
      if (this._isDisconnected) {
        console.log(`⏰ Page ${this._currentPage} timeout callback - skipping, component is disconnected`);
        this[timeoutKey] = null;
        return;
      }

      const stillRequesting = (this._currentPage === 1 && this._isRequestingPage1) ||
                              (this._currentPage === 2 && this._isRequestingPage2) ||
                              (this._currentPage === 3 && this._isRequestingPage3);

      if (stillRequesting) {
        console.warn(`⏰ Page ${this._currentPage} request timeout after 15 seconds - giving up`);
        if (this._currentPage === 1) {
          this._isRequestingPage1 = false;
        } else if (this._currentPage === 2) {
          this._isRequestingPage2 = false;
        } else if (this._currentPage === 3) {
          this._isRequestingPage3 = false;
        }
        this.requestUpdate();
      }
      this[timeoutKey] = null;
    }, 15000); // 15 seconds timeout (reduced from 30s with faster 2s refresh interval)
  }
  
  // Start periodic state checking to catch async updates
  _startPeriodicStateCheck(activityId, page) {
    // Skip if component is disconnected
    if (this._isDisconnected) {
      console.log("🔄 _startPeriodicStateCheck - skipping, component is disconnected");
      return;
    }

    // Clear any existing interval for this page
    const intervalKey = `_stateCheckIntervalPage${page}`;
    if (this[intervalKey]) {
      clearInterval(this[intervalKey]);
    }

    console.log(`🔄 Starting periodic state check for activity ${activityId}, page ${page}`);

    this[intervalKey] = setInterval(async () => {
      // Stop if component is disconnected
      if (this._isDisconnected) {
        console.log(`🔄 Component disconnected, stopping periodic state check for page ${page}`);
        clearInterval(this[intervalKey]);
        this[intervalKey] = null;
        return;
      }

      // Check if request for this page is still active
      const isRequesting = (page === 1 && this._isRequestingPage1) ||
                           (page === 2 && this._isRequestingPage2) ||
                           (page === 3 && this._isRequestingPage3);

      if (!isRequesting) {
        console.log(`🔄 Page ${page} request completed, stopping periodic state check`);
        clearInterval(this[intervalKey]);
        this[intervalKey] = null;
        return;
      }

      console.log("🔄 Periodic state check - forcing state refresh");

      // Force refresh the entity state from backend
      // Add a small delay (1 second) to allow backend sequential requests to complete
      // This prevents activity_list updates from overwriting favorite_keys
      await new Promise(resolve => setTimeout(resolve, 1000));

      this._forceRefreshState().then(() => {
        // After forcing refresh, check if state has changed
        if (this.hass && this.stateObj && this.stateObj.entity_id) {
          const latestState = this.hass.states[this.stateObj.entity_id];
          if (latestState) {
            const latestAssignedKeys = latestState.attributes?.assigned_keys;
            const currentAssignedKeys = this.stateObj.attributes?.assigned_keys;
            const latestMacroKeys = latestState.attributes?.macro_keys;
            const currentMacroKeys = this.stateObj.attributes?.macro_keys;
            const latestFavoriteKeys = latestState.attributes?.favorite_keys;
            const currentFavoriteKeys = this.stateObj.attributes?.favorite_keys;

            console.log("🔄 Comparing keys:");
            console.log("🔄   assigned_keys - Current:", currentAssignedKeys, "Latest:", latestAssignedKeys);
            console.log("🔄   macro_keys - Current:", currentMacroKeys, "Latest:", latestMacroKeys);
            console.log("🔄   favorite_keys - Current:", currentFavoriteKeys, "Latest:", latestFavoriteKeys);
            console.log("🔄   Current last_updated:", this.stateObj.last_updated);
            console.log("🔄   Latest last_updated:", latestState.last_updated);

            // Check if any keys have been updated
            const assignedKeysChanged = JSON.stringify(latestAssignedKeys) !== JSON.stringify(currentAssignedKeys);
            const macroKeysChanged = JSON.stringify(latestMacroKeys) !== JSON.stringify(currentMacroKeys);
            const favoriteKeysChanged = JSON.stringify(latestFavoriteKeys) !== JSON.stringify(currentFavoriteKeys);

            if (assignedKeysChanged || macroKeysChanged || favoriteKeysChanged) {
              console.log("Detected keys update via periodic check!");
              if (assignedKeysChanged) console.log("assigned_keys changed");
              if (macroKeysChanged) console.log("macro_keys changed");
              if (favoriteKeysChanged) console.log("favorite_keys changed");

              // Update stateObj and trigger completion check
              this.stateObj = latestState;
              this._checkRequestCompletion();
            } else if (latestState.last_updated !== this.stateObj.last_updated) {
              console.log("🔔 Detected state update (last_updated changed)");
              this.stateObj = latestState;
              this._checkRequestCompletion();
            } else {
              console.log("⏰ No state change detected yet");
              // Even if no change, check if we already have the data we need
              // This handles the case where data was loaded before the dialog opened
              this._checkRequestCompletion();
            }
          }
        }
      });
    }, 2000); // Check every 2 seconds (with _is_requesting_keys protection, we can check more frequently)
  }
  
  // Render function
  render() {
    // Skip rendering if component is disconnected
    if (this._isDisconnected) {
      console.log("🎨 Detail card render() - skipping, component is disconnected");
      return html``;
    }

    const isRequesting = (this._currentPage === 1 && this._isRequestingPage1) ||
                         (this._currentPage === 2 && this._isRequestingPage2) ||
                         (this._currentPage === 3 && this._isRequestingPage3);
    console.log("🎨 Detail card render() called - isRequesting:", isRequesting, "currentPage:", this._currentPage);

    if (!this.hass || !this.stateObj) {
      console.log("🎨 Detail card render() - missing hass or stateObj");
      return html``;
    }

    // Get the latest state from hass.states
    const currentState = this._getCurrentState();
    if (!currentState) {
      console.log("🎨 Detail card render() - no current state");
      return html``;
    }

    console.log("🎨   currentState:", currentState);
    console.log("🎨   currentState.entity_id:", currentState.entity_id);
    console.log("🎨   currentState.attributes.assigned_keys:", currentState.attributes?.assigned_keys);

    const attributes = currentState.attributes;
    const currentActivityId = attributes.current_activity_id;
    const activities = attributes.activities || [];

    // Check if there's a running activity（state为'on'的活动）
    const activeActivity = activities.find(a => a.state === 'on');
    // 优先使用从main-card传递的selectedActivityId，其次使用currentActivityId，最后使用运行中的活动
    const effectiveActivityId = this.selectedActivityId || currentActivityId || (activeActivity ? activeActivity.id : null);

    // 确定显示状态和用于按键匹配的Activity ID
    const showStatusMessage = !effectiveActivityId;
    const hasActivities = activities.length > 0;
    
    // 用于按键匹配的Activity ID（优先使用选中的活动，其次使用运行中的，最后使用第一个可用的）
    const keyMatchActivityId = this.selectedActivityId || effectiveActivityId || (activities.length > 0 ? activities[0].id : null);
    
    // 根据当前页面渲染不同的内容（始终使用keyMatchActivityId进行按键匹配）
    let pageContent;
    switch(this._currentPage) {
        case 1:
            pageContent = this._renderAssignedKeys(attributes, keyMatchActivityId, effectiveActivityId);
            break;
        case 2:
            pageContent = this._renderMacroKeys(attributes, keyMatchActivityId, effectiveActivityId);
            break;
        case 3:
            pageContent = this._renderFavoriteKeys(attributes, keyMatchActivityId, effectiveActivityId);
            break;
        default:
            pageContent = this._renderAssignedKeys(attributes, keyMatchActivityId, effectiveActivityId);
    }

    // 获取当前活动名称和状态
    const currentActivity = activities.find(a => a.id === effectiveActivityId);
    const keyMatchActivity = activities.find(a => a.id === keyMatchActivityId);
    
    let activityName, activityStatus;
    if (currentActivity) {
        activityName = currentActivity.name;
        activityStatus = currentActivity.state === 'on' ? 'Running' : 'Selected';
    } else if (keyMatchActivity && !effectiveActivityId) {
        activityName = keyMatchActivity.name;
        activityStatus = 'Not Started';
    } else {
        activityName = keyMatchActivityId ? `Activity ${keyMatchActivityId}` : 'No Activity';
        activityStatus = 'Unknown Status';
    }

    return html`
      <div class="container">
        <!-- Current activity info -->
        <div class="current-activity">
            <ha-icon icon="${currentActivity && currentActivity.state === 'on' ? 'mdi:play-circle' : 'mdi:pause-circle'}"></ha-icon>
            <span>${activityName} - ${activityStatus}</span>
            <!-- Start/stop button removed, please manage activity status on main card -->
        </div>
        
        <!-- Page navigation -->
        <div class="page-nav">
          <ha-icon-button @click=${() => this._changePage(-1)} .disabled=${this._currentPage === 1}>
            <ha-icon icon="mdi:chevron-left"></ha-icon>
          </ha-icon-button>
          <span>${this._getPageTitle()} (${this._currentPage}/3)</span>
          <ha-icon-button @click=${() => this._changePage(1)} .disabled=${this._currentPage === 3}>
            <ha-icon icon="mdi:chevron-right"></ha-icon>
          </ha-icon-button>
        </div>
        <!-- Status message -->
        ${showStatusMessage ? html`
          <div class="status-message">
            ${!hasActivities ? html`
              <div class="warning-message">
                <ha-icon icon="mdi:alert-circle-outline"></ha-icon>
                <span>No activities found, please check Hub connection</span>
                <ha-button @click=${this._refreshData} size="small">
                  <ha-icon icon="mdi:refresh"></ha-icon>
                  Refresh
                </ha-button>
              </div>
            ` : html`
              <div class="info-message">
                <ha-icon icon="mdi:information-outline"></ha-icon>
                <span>Please start an activity on the main card to fully control corresponding keys</span>
                <!-- Quick start button removed, please manage activity status on main card -->
              </div>
            `}
          </div>
        ` : ''}

        <!-- Page content -->
        <div class="page-content">
          ${pageContent}
        </div>
      </div>
    `;
  }

  // Render assigned keys page (remote control)
  _renderAssignedKeys(attributes, keyMatchActivityId, effectiveActivityId) {
    const assignedKeyIds = attributes.assigned_keys?.[keyMatchActivityId] || [];
    console.log("🎨 Frontend: Rendering assigned keys for activity", keyMatchActivityId, "assigned keys:", assignedKeyIds);
    console.log("🎨 Frontend: _isRequestingPage1 =", this._isRequestingPage1);

    // Whether there's a running activity (to determine if keys are fully available)
    const hasActiveActivity = !!effectiveActivityId;

    // Show loading hint when requesting OR when no data and no previous response received
    // Check if we have ever received a response for this activity
    const hasReceivedResponse = attributes.assigned_keys &&
                               attributes.assigned_keys.hasOwnProperty(keyMatchActivityId);

    console.log(`Render logic - keyMatchActivityId: ${keyMatchActivityId}, hasReceivedResponse: ${hasReceivedResponse}, assignedKeyIds.length: ${assignedKeyIds.length}, _isRequestingPage1: ${this._isRequestingPage1}`);
    console.log("🔍 Full attributes.assigned_keys:", attributes.assigned_keys);

    const showLoadingHint = (assignedKeyIds.length === 0) &&
                           (this._isRequestingPage1 || !hasReceivedResponse);

    // Use page 1 request status
    const isRequesting = this._isRequestingPage1;

    // Render a group of keys
    const renderKeyGroup = (group) => html`
        <div class="key-group">
            ${group.map(k => {
                const key_info = REMOTE_KEYS[k.key];
                const is_assigned = assignedKeyIds.includes(key_info.id);
                // Key availability condition: assigned and activity running, or at least assigned (show but limited function)
                const is_enabled = is_assigned && hasActiveActivity;
                const is_partial = is_assigned && !hasActiveActivity;
                
                return html`
                <div class="key-wrapper ${is_partial ? 'partial-enabled' : ''}" style="grid-area: ${k.grid || 'auto'};">
                    <ha-icon-button 
                        @click=${(e) => this._sendAssignedKey(keyMatchActivityId, key_info.id, e)}
                        .disabled=${!is_assigned}
                        class="${is_partial ? 'partial' : ''}"
                        title="${k.key}${is_partial ? ' (Activity needs to be started)' : ''}"
                    >
                        ${key_info.icon ? html`<ha-icon icon="${key_info.icon}"></ha-icon>` : ''}
                        ${key_info.text ? html`<span class="text-key">${key_info.text}</span>` : ''}
                        ${key_info.color ? html`<div class="color-key" style="background-color: ${key_info.color};"></div>` : ''}
                    </ha-icon-button>
                </div>
                `
            })}
        </div>
    `;
    
    return html`
        ${showLoadingHint ? html`
            <div class="loading-hint">
                <ha-icon icon="${isRequesting ? 'mdi:loading' : 'mdi:information-outline'}" 
                         class="${isRequesting ? 'spinning' : ''}"></ha-icon>
                <span>${isRequesting ? 
                  'Loading remote control data...' : 
                  'No remote control keys available for this activity'}</span>
            </div>
        ` : ''}
        
        ${hasReceivedResponse && assignedKeyIds.length > 0 ? html`
        <div class="remote-layout">
            <!-- Direction keys - cross layout -->
            <div class="dpad-grid">
                ${REMOTE_LAYOUT.dpad.map(k => {
                    const key_info = REMOTE_KEYS[k.key];
                    if (!key_info) {
                        console.warn('Key info not found for:', k.key);
                        return '';
                    }
                    const is_assigned = assignedKeyIds.includes(key_info.id);
                    const is_enabled = is_assigned && hasActiveActivity;
                    const is_partial = is_assigned && !hasActiveActivity;
                    
                    return html`
                    <div class="key-wrapper ${is_partial ? 'partial-enabled' : ''}" style="grid-area: ${k.grid};">
                        <ha-icon-button 
                            @click=${(e) => this._sendAssignedKey(keyMatchActivityId, key_info.id, e)}
                            .disabled=${!is_assigned}
                            class="${is_partial ? 'partial' : ''}"
                            title="${k.key}${is_partial ? ' (Activity needs to be started)' : ''}"
                        >
                            ${key_info.icon ? html`<ha-icon icon="${key_info.icon}"></ha-icon>` : ''}
                            ${key_info.text ? html`<span class="text-key">${key_info.text}</span>` : ''}
                            ${key_info.color ? html`<div class="color-key" style="background-color: ${key_info.color};"></div>` : ''}
                        </ha-icon-button>
                    </div>
                    `;
                })}
            </div>
            
            <!-- Function keys - horizontal layout -->
            ${renderKeyGroup(REMOTE_LAYOUT.functions)}
            
            <!-- Volume channel area - 2x3 grid symmetric layout -->
            <div class="volume-channel-grid">
                ${REMOTE_LAYOUT.volume_channel.map(k => {
                    const key_info = REMOTE_KEYS[k.key];
                    if (!key_info) {
                        console.warn('Key info not found for:', k.key);
                        return '';
                    }
                    const is_assigned = assignedKeyIds.includes(key_info.id);
                    const is_enabled = is_assigned && hasActiveActivity;
                    const is_partial = is_assigned && !hasActiveActivity;
                    
                    return html`
                    <div class="key-wrapper ${is_partial ? 'partial-enabled' : ''}" style="grid-area: ${k.grid};">
                        <ha-icon-button 
                            @click=${(e) => this._sendAssignedKey(keyMatchActivityId, key_info.id, e)}
                            .disabled=${!is_assigned}
                            class="${is_partial ? 'partial' : ''}"
                            title="${k.key}${is_partial ? ' (Activity needs to be started)' : ''}"
                        >
                            ${key_info.icon ? html`<ha-icon icon="${key_info.icon}"></ha-icon>` : ''}
                            ${key_info.text ? html`<span class="text-key">${key_info.text}</span>` : ''}
                            ${key_info.color ? html`<div class="color-key" style="background-color: ${key_info.color};"></div>` : ''}
                        </ha-icon-button>
                    </div>
                    `;
                })}
            </div>
            
            <!-- Media control keys -->
            ${renderKeyGroup(REMOTE_LAYOUT.transport)}
            ${renderKeyGroup(REMOTE_LAYOUT.transport_extra)}
            
            <!-- Color keys -->
            ${renderKeyGroup(REMOTE_LAYOUT.colors)}
            
            <!-- Custom keys -->
            ${renderKeyGroup(REMOTE_LAYOUT.customs)}
        </div>
        ` : hasReceivedResponse ? html`
            <div class="info-message">
                <ha-icon icon="mdi:information-outline"></ha-icon>
                <span>No remote control keys available for this activity</span>
            </div>
        ` : ''}
    `;
  }

  // Render macro commands page
  _renderMacroKeys(attributes, keyMatchActivityId, effectiveActivityId) {
    const macroKeys = attributes.macro_keys?.[keyMatchActivityId] || [];
    console.log("Rendering macro keys for activity", keyMatchActivityId, ":", macroKeys);
    console.log("🎨 Frontend: _isRequestingPage2 =", this._isRequestingPage2);

    // Use page 2 request status
    const isRequesting = this._isRequestingPage2;

    if (macroKeys.length === 0) {
        return html`
            <div class="loading-message">
                <ha-icon icon="${isRequesting ? 'mdi:loading' : 'mdi:information-outline'}" 
                         class="${isRequesting ? 'spinning' : ''}"></ha-icon>
                <p>${isRequesting ? 'Loading macro commands...' : 'No macro commands available for this activity'}</p>
                ${isRequesting ? html`<p>Please wait while macro commands are being loaded.</p>` : ''}
            </div>
        `;
    }

    return html`
      <div class="macro-grid">
        ${macroKeys.map(key => html`
          <button
            class="macro-button"
            @click=${(e) => this._sendMacroKey(keyMatchActivityId, key.id, e)}
            title="${key.name}"
          >
            ${key.name}
          </button>
        `)}
      </div>
    `;
  }

  // Render favorite commands page
  _renderFavoriteKeys(attributes, keyMatchActivityId, effectiveActivityId) {
    const favoriteKeys = attributes.favorite_keys?.[keyMatchActivityId] || [];
    console.log("Rendering favorite keys for activity", keyMatchActivityId, ":", favoriteKeys);
    console.log("🎨 Frontend: _isRequestingPage3 =", this._isRequestingPage3);

    // Use page 3 request status
    const isRequesting = this._isRequestingPage3;

    if (favoriteKeys.length === 0) {
        return html`
            <div class="loading-message">
                <ha-icon icon="${isRequesting ? 'mdi:loading' : 'mdi:information-outline'}" 
                         class="${isRequesting ? 'spinning' : ''}"></ha-icon>
                <p>${isRequesting ? 'Loading favorite commands...' : 'No favorite commands available for this activity'}</p>
                ${isRequesting ? html`<p>Please wait while favorite commands are being loaded.</p>` : ''}
            </div>
        `;
    }

     return html`
      <div class="favorite-grid">
        ${favoriteKeys.map(key => html`
          <button
            class="favorite-button"
            @click=${(e) => this._sendFavoriteKey(keyMatchActivityId, key.id, key.device_id, e)}
            title="${key.name}"
          >
            ${key.name}
          </button>
        `)}
      </div>
    `;
  }
  
  // Switch page
  _changePage(direction) {
    const newPage = this._currentPage + direction;
    if (newPage >= 1 && newPage <= 3) {
      this._currentPage = newPage;
      // Request data for the new page
      console.log(`📄 Page changed to ${newPage}, requesting data`);
      this._requestKeysForCurrentPage();
    }
  }

  // Get page title
  _getPageTitle() {
    switch(this._currentPage) {
        case 1: return "Assigned Keys";
        case 2: return "Macro Commands";
        case 3: return "Favorite Commands";
        default: return "";
    }
  }

  // Send assigned key command
  _sendAssignedKey(activityId, keyId, event) {
    // Add ripple effect
    this._addRippleEffect(event);
    
    this.hass.callService("remote", "send_command", {
        entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
        command: [`type:send_assigned_key`, `activity_id:${activityId}`, `key_id:${keyId}`],
    });
  }

  // Add ripple effect
  _addRippleEffect(event) {
    const button = event.target.closest('.key-wrapper');
    if (!button) return;
    
    // Remove previous ripple effect
    button.classList.remove('ripple');
    
    // Force redraw
    button.offsetHeight;
    
    // Add ripple effect
    button.classList.add('ripple');
    
    // Remove ripple effect class
    setTimeout(() => {
      button.classList.remove('ripple');
    }, 600);
  }

  // Send macro command
  _sendMacroKey(activityId, keyId, event) {
    if (event) this._addRippleEffect(event);
    
    this.hass.callService("remote", "send_command", {
        entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
        command: [`type:send_macro_key`, `activity_id:${activityId}`, `key_id:${keyId}`],
    });
  }

  // Send favorite command
  _sendFavoriteKey(activityId, keyId, deviceId, event) {
    if (event) this._addRippleEffect(event);

     this.hass.callService("remote", "send_command", {
        entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
        command: [`type:send_favorite_key`, `activity_id:${activityId}`, `key_id:${keyId}`, `device_id:${deviceId}`],
    });
  }

  // Start activity
  _startActivity(activityId) {
    this.hass.callService("remote", "send_command", {
        entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
        command: [`type:start_activity`, `activity_id:${activityId}`],
    });
  }

  // Stop current activity
  _stopCurrentActivity() {
    this.hass.callService("remote", "send_command", {
        entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
        command: [`type:stop_activity`, `activity_id:${this.stateObj.attributes.current_activity_id}`],
    });
  }

  // Refresh data
  _refreshData() {
    // Trigger entity data refresh
    this.hass.callService("homeassistant", "update_entity", {
        entity_id: ensureEntityIdIsString(this.stateObj.entity_id),
    });
  }

}

// Register custom elements
customElements.define("sofabaton-detail-card", SofabatonDetailCard);

// Global dialog management - ensure only one Sofabaton dialog is open
let currentSofabatonDialog = null;

// Add global click listener to close non-Sofabaton dialogs
document.addEventListener("click", (e) => {
    // If clicked on Sofabaton-related three-dot button
    if (e.target && e.target.closest && e.target.closest("ha-icon-button") && 
        e.target.closest(".more-info")) {
        // Check if in Sofabaton card
        const sofabatonCard = e.target.closest("sofabaton-main-card");
        if (sofabatonCard) {
            // Delayed close other dialogs
            setTimeout(() => {
                const otherDialogs = document.querySelectorAll("ha-more-info-dialog:not([data-sofabaton-dialog])");
                otherDialogs.forEach(dialog => {
                    if (dialog.close) dialog.close();
                });
            }, 50);
        }
    }
});

// Listen for hass-more-info event, replace default popup content with our card
document.addEventListener("hass-more-info", (e) => {
    const entityId = e.detail.entityId;
    const selectedActivityId = e.detail.selectedActivityId;  // 接收选中的活动ID
    console.log("More info requested for entity:", entityId, "selectedActivityId:", selectedActivityId);
    
    // Check if it's a Sofabaton Hub related remote entity
    // Judge by checking entity attributes, not relying on entity ID naming
    const isSofabatonHub = entityId?.startsWith("remote.") && 
                          checkIfSofabatonHub(entityId, document.querySelector("home-assistant")?.hass);
    
    if (isSofabatonHub) {
        console.log("Intercepting more-info for Sofabaton Hub:", entityId);
        
        // Immediately prevent default behavior
        e.stopPropagation();
        e.stopImmediatePropagation();
        e.preventDefault();
        
        // Get Home Assistant instance
        const homeAssistant = document.querySelector("home-assistant");
        if (!homeAssistant || !homeAssistant.hass) {
            console.error("Could not find Home Assistant instance");
            return false;
        }
        
        const hass = homeAssistant.hass;
        const stateObj = hass.states[entityId];
        
        if (!stateObj) {
            console.error("Could not find state object for entity:", entityId);
            return false;
        }
        
        // Immediately create custom dialog
        showSofabatonDialog(hass, stateObj, selectedActivityId);
        
        return false; // Prevent event propagation
    }
}, true); // Use capture mode to catch events earlier

// Another listener to ensure no default dialog appears
document.addEventListener("show-dialog", (e) => {
    if (e.detail && e.detail.dialogTag === "ha-more-info-dialog") {
        const entityId = e.detail.dialogParams?.entityId;
        const isSofabatonHub = entityId?.startsWith("remote.") && 
                              checkIfSofabatonHub(entityId, document.querySelector("home-assistant")?.hass);
        
        if (isSofabatonHub) {
            console.log("Blocking default more-info dialog for:", entityId);
            e.stopPropagation();
            e.stopImmediatePropagation();
            e.preventDefault();
            return false;
        }
    }
}, true);

// Create and show Sofabaton Hub dialog
function showSofabatonDialog(hass, stateObj, selectedActivityId) {
    console.log("Creating Sofabaton remote control dialog for:", stateObj.entity_id, "with selectedActivityId:", selectedActivityId);
    
    // Close current Sofabaton dialog (if exists)
    if (currentSofabatonDialog && currentSofabatonDialog.close) {
        currentSofabatonDialog.close();
        currentSofabatonDialog = null;
    }
    
    // 强制清理所有可能存在的 Sofabaton 对话框
    const existingDialogs = document.querySelectorAll('ha-dialog[data-sofabaton-dialog="true"]');
    console.log("🎯 Force cleaning", existingDialogs.length, "existing Sofabaton dialogs");
    existingDialogs.forEach(dialog => {
        if (dialog.close) dialog.close();
        if (dialog.parentNode) dialog.parentNode.removeChild(dialog);
    });
    
    // Create dialog container
    const dialog = document.createElement("ha-dialog");
    dialog.setAttribute("open", "");
    dialog.setAttribute("hide-actions", "");
    dialog.setAttribute("data-sofabaton-dialog", "true");
    
    // Set dialog title
    dialog.heading = `${stateObj.attributes.friendly_name || "Sofabaton Hub"} - Remote Control`;
    
    // Create detail card
    const card = document.createElement("sofabaton-detail-card");
    card.hass = hass;
    card.stateObj = stateObj;
    card.entityId = stateObj.entity_id;  // Set entityId for dynamic state updates
    card.selectedActivityId = selectedActivityId;  // 传递选中的活动ID
    console.log("🎯 Creating detail card with selectedActivityId:", selectedActivityId);
    console.log("🎯 Creating detail card with entityId:", stateObj.entity_id);
    
    // Set dialog content
    dialog.appendChild(card);
    
    // Add close button - using more robust method
    const closeButton = document.createElement("ha-icon-button");
    closeButton.setAttribute("slot", "heading");
    closeButton.setAttribute("title", "Close");
    closeButton.style.marginLeft = "auto";
    closeButton.style.cursor = "pointer";
    
    const closeIcon = document.createElement("ha-icon");
    closeIcon.setAttribute("icon", "mdi:close");
    closeButton.appendChild(closeIcon);
    
    // Multiple event listening methods to ensure close functionality
    const closeHandler = (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        console.log("Close button clicked - closing dialog");
        
        // Reset request state when closing dialog
        const detailCard = dialog.querySelector("sofabaton-detail-card");
        if (detailCard) {
            console.log("Resetting detail card request state on close");
            detailCard._isRequesting = false;
            detailCard.requestUpdate(); // Trigger re-render to reflect state change
        }
        
        dialog.close();
        return false;
    };
    
    // Add multiple event listeners
    closeButton.addEventListener("click", closeHandler, true);
    closeButton.addEventListener("mousedown", closeHandler, true);
    closeButton.addEventListener("touchstart", closeHandler, true);
    
    // Also add event listeners on icon
    closeIcon.addEventListener("click", closeHandler, true);
    closeIcon.addEventListener("mousedown", closeHandler, true);
    
    dialog.appendChild(closeButton);
    
    
    // Set dialog styles
    dialog.style.setProperty("--mdc-dialog-min-width", "400px");
    dialog.style.setProperty("--mdc-dialog-max-width", "90vw");
    dialog.style.setProperty("--mdc-dialog-min-height", "60vh");
    dialog.style.setProperty("z-index", "9999");
    
    // When dialog is closed, remove it from DOM
    dialog.addEventListener("closed", () => {
        // Reset request state when dialog is closed
        const detailCard = dialog.querySelector("sofabaton-detail-card");
        if (detailCard) {
            console.log("Dialog closed - resetting detail card request state");
            detailCard._isRequesting = false;
        }
        
        if (dialog.parentNode) {
            dialog.parentNode.removeChild(dialog);
        }
        if (currentSofabatonDialog === dialog) {
            currentSofabatonDialog = null;
        }
    });
    
    // Support ESC key to close
    dialog.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            e.preventDefault();
            
            // Reset request state when ESC is pressed
            const detailCard = dialog.querySelector("sofabaton-detail-card");
            if (detailCard) {
                console.log("ESC key pressed - resetting detail card request state");
                detailCard._isRequesting = false;
                detailCard.requestUpdate(); // Trigger re-render to reflect state change
            }
            
            dialog.close();
        }
    });
    
    // Set global reference
    currentSofabatonDialog = dialog;
    
    // Add to page
    document.body.appendChild(dialog);
    
    console.log("Sofabaton remote dialog shown");
}