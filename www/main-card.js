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

// Main card class
class SofabatonMainCard extends LitElement {
  
  // Define component properties
  static get properties() {
    return {
      hass: { type: Object }, // Home Assistant object
      config: { type: Object }, // Card configuration
      _selectedActivityId: { type: Number, state: true }, // Internal state: currently selected Activity ID
      _selectedDeviceId: { type: Number, state: true }, // Internal state: currently selected Device ID
      _lastCurrentActivityId: { type: Number, state: true }, // Track last activity ID
    };
  }

  // Set card configuration
  setConfig(config) {
    if (!config || !config.entity) {
      throw new Error("You need to define an entity. Please select a Sofabaton Hub remote entity in the card configuration.");
    }
    this.config = config;
  }
  
  // Called when component is connected to DOM
  connectedCallback() {
    super.connectedCallback();
    // On first load, if there's an activity, set it as selected
    if (this.hass && this.config) {
      const stateObj = this.hass.states[this.config.entity];
      if (stateObj && stateObj.attributes.current_activity_id) {
        this._selectedActivityId = stateObj.attributes.current_activity_id;
      }
      
      // Check if data needs refreshing
      this._checkAndRefreshData();
    }
  }

  // Check and refresh data
  _checkAndRefreshData() {
    if (!this.hass || !this.config) return;
    
    const stateObj = this.hass.states[this.config.entity];
    if (!stateObj) return;
    
    const attributes = stateObj.attributes;
    const activities = attributes.activities || {};
    const devices = attributes.devices || {};
    
    // If no activity or device data, or data is outdated, refresh
    const needRefresh = Object.keys(activities).length === 0 || Object.keys(devices).length === 0;
    
    if (needRefresh) {
      console.log("Main card: Requesting basic data refresh");
      this._requestBasicData();
    }
  }

  // Request basic data
  _requestBasicData() {
    if (!this.hass || !this.config) {
      console.log("Main card: Cannot request basic data - missing hass or config");
      return;
    }

    console.log("Main card: Calling request_basic_data service");
    console.log("Main card:   entity_id:", this.config.entity);

    // Use new chained request command to directly trigger basic data update
    this.hass.callService("remote", "send_command", {
      entity_id: this.config.entity,
      command: ["type:request_basic_data"],
    }).then(() => {
      console.log("Main card: request_basic_data service called successfully");
    }).catch(error => {
      console.error("Main card: Error calling request_basic_data service:", error);
    });
  }
  
  // Decide whether update is needed
  shouldUpdate(changedProperties) {
    // Always update if hass or config changes
    if (changedProperties.has('hass') || changedProperties.has('config')) {
      // Additional check: if hass changed, check if currentActivityId changed
      if (changedProperties.has('hass')) {
        const oldHass = changedProperties.get('hass');
        const newHass = this.hass;
        
        if (oldHass && newHass && this.config) {
          const oldStateObj = oldHass.states[this.config.entity];
          const newStateObj = newHass.states[this.config.entity];
          
          const oldActivityId = oldStateObj?.attributes?.current_activity_id;
          const newActivityId = newStateObj?.attributes?.current_activity_id;
          
          if (oldActivityId !== newActivityId) {
            console.log("Main card: currentActivityId changed from", oldActivityId, "to", newActivityId, "- forcing update");
          }
        }
      }
      return true;
    }
    
    // Also update if internal state changes
    if (changedProperties.has('_selectedActivityId') || 
        changedProperties.has('_selectedDeviceId') || 
        changedProperties.has('_lastCurrentActivityId')) {
      return true;
    }
    
    return super.shouldUpdate(changedProperties);
  }

  // Called when properties are updated
  updated(changedProperties) {
    if (changedProperties.has('hass') && this.hass && this.config) {
      const stateObj = this.hass.states[this.config.entity];
      if (stateObj) {
        const currentActivityId = stateObj.attributes.current_activity_id;
        let needsUpdate = false; // 标记是否需要更新

        // Check if currentActivityId changed (for More Info button visibility)
        if (changedProperties.has('hass')) {
          const oldHass = changedProperties.get('hass');
          if (oldHass && this.config) {
            const oldStateObj = oldHass.states[this.config.entity];
            const oldActivityId = oldStateObj?.attributes?.current_activity_id;

            if (oldActivityId !== currentActivityId) {
              console.log("Main card: Activity state changed, currentActivityId:", oldActivityId, "→", currentActivityId);
              needsUpdate = true;
            }
          }
        }

        // If current activity ID doesn't match selected ID (e.g., switched via physical remote), sync
        if (currentActivityId && this._selectedActivityId !== currentActivityId) {
          this._selectedActivityId = currentActivityId;
          this._notifyActivityChanged(); // Notify detail-card of activity change
          needsUpdate = true;
        } else if (!currentActivityId && this._selectedActivityId) {
          // If no activity, clear selection
          this._selectedActivityId = null;
          this._notifyActivityChanged(); // Notify detail-card of activity change
          needsUpdate = true;
        }

        // Check if data changed
        const attributes = stateObj.attributes;
        const activities = attributes.activities || [];
        const hasNewData = activities.length > 0;

        if (hasNewData || this._lastCurrentActivityId !== currentActivityId) {
          this._lastCurrentActivityId = currentActivityId;
          needsUpdate = true;
        }

        // Only request update once if needed
        if (needsUpdate) {
          console.log("Main card: Requesting update due to state/data changes");
          this.requestUpdate();

          // Use updateComplete to ensure update is finished before subsequent operations
          this.updateComplete.then(() => {
            console.log("Main card: Update completed");
          });
        }
      }
    }
  }



  // Render function
  render() {
    if (!this.hass || !this.config) {
      return html``;
    }
    
    // Get entity object
    const stateObj = this.hass.states[this.config.entity];
    
    // Add debug log to track rendering
    console.log("Main card: Rendering with state", stateObj ? 'available' : 'unavailable');

    if (!stateObj) {
      return html`
        <ha-card header="Sofabaton Hub">
          <div class="card-content">
            Entity not found: ${this.config.entity}
          </div>
        </ha-card>
      `;
    }

    // Get data from entity attributes
    const attributes = stateObj.attributes;
    const activities = attributes.activities || [];
    // DEVICE_DISABLED: Temporarily disable device functionality - uncomment below line when restoring
    // const devices = attributes.devices || [];
    
    // Add detailed data monitoring logs
    console.log("Main card: Activities data", activities);
    console.log("Main card: Current activity ID", attributes.current_activity_id);
    console.log("Main card: Selected activity ID", this._selectedActivityId);
    
    // Check data loading status
    const hasActivities = Object.keys(activities).length > 0;
    // DEVICE_DISABLED: Temporarily disable device functionality - uncomment below line when restoring并启用设备检查
    // const hasDevices = Object.keys(devices).length > 0;
    // const isDataLoading = !hasActivities || !hasDevices;
    const isDataLoading = !hasActivities;
    
    // Find currently selected activity object
    const selectedActivity = activities.find(a => a.id === this._selectedActivityId);

    // Get currently running activity ID
    const currentActivityId = stateObj.attributes.current_activity_id;
    // Determine if selected activity is running
    const isSelectedActivityRunning = currentActivityId === this._selectedActivityId;

    console.log("Main card: selectedActivity object:", selectedActivity);
    console.log("Main card: isSelectedActivityRunning:", isSelectedActivityRunning);
    
    // Determine if More Info button should be shown
    // Two conditions need to be met:
    // 1. There's a running activity (based on TOPIC_ACTIVITY_CONTROL_UP data) and it's not activity ID 255
    // 2. User has selected an activity and it's in 'on' state, or no activity selected but there's a running one
    
    const hasRunningActivity = currentActivityId && currentActivityId !== 255;

    let shouldShowBasedOnSelection = false;
    if (this._selectedActivityId) {
      // If user selected an activity, check if it's running
      // ONLY use isSelectedActivityRunning (based on current_activity_id) for real-time accuracy
      // Do NOT use selectedActivity.state as it may not update immediately
      shouldShowBasedOnSelection = isSelectedActivityRunning;
    } else {
      // If no activity selected, show button only if there's a running activity
      shouldShowBasedOnSelection = hasRunningActivity;
    }

    const shouldShowMoreInfo = hasRunningActivity && shouldShowBasedOnSelection;
    
    console.log("Main card: More Info button logic - currentActivityId:", currentActivityId, 
                "selectedActivityId:", this._selectedActivityId, 
                "selectedActivityState:", selectedActivity?.state,
                "hasRunning:", hasRunningActivity, 
                "shouldShowBasedOnSelection:", shouldShowBasedOnSelection,
                "shouldShow:", shouldShowMoreInfo);

    return html`
      <ha-card>
        <div class="card-header">
            <div class="name">
                <ha-icon icon="mdi:remote-tv"></ha-icon>
                Sofabaton
            </div>
            <div class="header-buttons">
              <ha-icon-button
                .label=${"Refresh Data"}
                @click=${this._handleRefresh}
                class="refresh-button"
                title="Refresh Data"
              >
                <ha-icon icon="mdi:refresh"></ha-icon>
              </ha-icon-button>
              ${shouldShowMoreInfo ? html`
                <ha-icon-button
                  .label=${"More Info"}
                  @click=${this._handleMoreInfo}
                  class="more-info"
                >
                  <ha-icon icon="mdi:dots-vertical"></ha-icon>
                </ha-icon-button>
              ` : ''}
            </div>
        </div>
        
        <div class="card-content">
          <!-- Data loading status indicator -->
          ${isDataLoading ? html`
            <div class="loading-status">
              <ha-icon icon="mdi:loading" class="spinning"></ha-icon>
              <!-- DEVICE_DISABLED: Temporarily disable device functionality - when restoring change to: ${!hasActivities ? 'Activity List' : 'Device List'} -->
              <span>Loading data in sequence... Activity List</span>
            </div>
          ` : ''}
          
          <!-- Activity Section -->
          <div class="section">
            <div class="section-header">
                <ha-icon class="section-icon" icon="mdi:pulse"></ha-icon>
                <div class="section-title">Activity</div>
            </div>
            ${selectedActivity ? html`
              <div class="activity-control">
                <span>${selectedActivity.name}</span>
                <ha-switch
                  .checked=${isSelectedActivityRunning}
                  @change=${this._handleActivityToggle}
                ></ha-switch>
              </div>
            ` : ''}
            <ha-select
              .label=${selectedActivity ? "" : "Select Activity"}
              .value=${this._selectedActivityId || ''}
              @selected=${this._handleActivitySelect}
              @closed=${(e) => e.stopPropagation()}
            >
              ${activities.map(
                (activity) => html`
                  <ha-list-item .value=${activity.id}>
                    ${activity.name}
                  </ha-list-item>
                `
              )}
            </ha-select>
          </div>

          ${/* DEVICE_DISABLED: 暂时屏蔽设备功能 - 恢复时需要:
             1. 取消注释 devices 变量定义
             2. 取消注释 hasDevices 检查
             3. 恢复下面的HTML代码:
             
          <div class="section">
            <div class="section-header">
                <ha-icon class="section-icon" icon="mdi:remote"></ha-icon>
                <div class="section-title">Device</div>
            </div>
            <ha-select
              label="Select Device"
              .value=${this._selectedDeviceId || ''}
              @selected=${this._handleDeviceSelect}
              @closed=${(e) => e.stopPropagation()}
            >
              ${devices.map(
                (device) => html`
                  <ha-list-item .value=${device.id}>
                    ${device.name}
                  </ha-list-item>
                `
              )}
            </ha-select>
          </div>
          */ ''}
        </div>
      </ha-card>
    `;
  }
  
  // Handle activity selection change event
  _handleActivitySelect(e) {
    let value = e.target.value;
    // Ensure value is a string, not an array
    if (Array.isArray(value)) {
      value = value[0];
    }
    
    const selectedId = parseInt(value, 10);
    if (!selectedId || selectedId === this._selectedActivityId) return;

    this._selectedActivityId = selectedId;
    this._notifyActivityChanged(); // Notify detail-card of activity change

    // Manually trigger re-render to update switch state
    this.requestUpdate();

    // When selecting a new activity, automatically request its key list
    // this.hass.callService("remote", "send_command", {
    //   entity_id: ensureEntityIdIsString(this.config.entity),
    //   command: [`type:request_keys`, `activity_id:${selectedId}`],
    // });
  }

  // DEVICE_DISABLED: Temporarily disable device functionality - uncomment below when restoring
  /*
  // Handle device selection change event
  _handleDeviceSelect(e) {
    let value = e.target.value;
    // Ensure value is a string, not an array
    if (Array.isArray(value)) {
      value = value[0];
    }
    
    const selectedId = parseInt(value, 10);
    if (!selectedId || selectedId === this._selectedDeviceId) return;

    this._selectedDeviceId = selectedId;
    
    // When selecting a device, request its command list
    this.hass.callService("remote", "send_command", {
      entity_id: ensureEntityIdIsString(this.config.entity),
      command: [`type:request_device_keys`, `device_id:${selectedId}`],
    });
  }
  */
  
  // Handle activity switch toggle event
  _handleActivityToggle(e) {
    if (!this._selectedActivityId) return;
    
    const turnOn = e.target.checked;
    const command = turnOn ? "start_activity" : "stop_activity";
    
    this.hass.callService("remote", "send_command", {
      entity_id: ensureEntityIdIsString(this.config.entity),
      command: [`type:${command}`, `activity_id:${this._selectedActivityId}`],
    });
  }
  
  // Handle more info button click
  _handleMoreInfo() {
    const event = new Event("hass-more-info", {
      bubbles: true,
      composed: true,
    });
    event.detail = {
      entityId: this.config.entity,
      selectedActivityId: this._selectedActivityId  // 传递当前选中的活动ID
    };
    console.log("🎯 Main card: Triggering more-info with selectedActivityId:", this._selectedActivityId);
    this.dispatchEvent(event);
  }

  // Notify detail-card of activity change
  _notifyActivityChanged() {
    const event = new CustomEvent("sofabaton-activity-changed", {
      bubbles: true,
      composed: true,
      detail: {
        entityId: this.config.entity,
        selectedActivityId: this._selectedActivityId
      }
    });
    console.log("🎯 Main card: Notifying activity changed to:", this._selectedActivityId);
    document.dispatchEvent(event);
  }

  // Handle refresh button click
  _handleRefresh() {
    console.log("Main card: Manual refresh requested");
    this._requestBasicData();
    
    // Add visual feedback
    const refreshButton = this.shadowRoot.querySelector('.refresh-button');
    if (refreshButton) {
      refreshButton.classList.add('spinning');
      setTimeout(() => {
        refreshButton.classList.remove('spinning');
      }, 2000); // Stop spinning after 2 seconds
    }
  }

  // Define card styles
  static get styles() {
    return css`
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px;
      }
      .name {
        display: flex;
        align-items: center;
        font-size: 1.2rem;
        font-weight: 500;
      }
      .name ha-icon {
        margin-right: 8px;
        color: var(--state-icon-color);
      }
      .header-buttons {
        display: flex;
        align-items: center;
        gap: 4px;
      }
      .refresh-button ha-icon {
        transition: transform 0.3s ease;
      }
      .refresh-button.spinning ha-icon {
        animation: spin 1s linear infinite;
      }
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      .loading-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid rgba(33, 150, 243, 0.3);
        border-radius: 6px;
        margin: 8px 16px;
        font-size: 14px;
        opacity: 0.8;
      }
      .loading-status ha-icon {
        color: var(--primary-color);
      }
      .spinning {
        animation: spin 1s linear infinite;
      }
      .section {
        padding: 8px 16px;
      }
      .section-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
      }
      .section-icon {
        color: var(--secondary-text-color);
      }
      .section-title {
        font-weight: 500;
        margin-left: 8px;
      }
      ha-select {
        width: 100%;
        margin-top: 8px;
      }
      .activity-control {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        font-size: 1rem;
      }
    `;
  }

  // Add card editor support
  static getConfigElement() {
    return document.createElement("sofabaton-main-card-editor");
  }

  // Add stub configuration (for card picker preview)
  static getStubConfig() {
    return {
      type: "custom:sofabaton-main-card",
      entity: ""
    };
  }
}

// Card editor class
class SofabatonMainCardEditor extends LitElement {
  static get properties() {
    return {
      hass: {},
      config: {},
    };
  }

  setConfig(config) {
    this.config = config || {};
    // Ensure config has basic structure
    if (!this.config.entity) {
      this.config.entity = "";
    }
  }

  get _entity() {
    return this.config.entity || "";
  }

  render() {
    if (!this.hass) {
      return html``;
    }

    // Get all remote entities, prioritize Sofabaton Hub entities
    const allRemoteEntities = Object.keys(this.hass.states).filter((eid) =>
      eid.startsWith("remote.")
    );
    
    // Separate Sofabaton Hub entities and other remote entities
    const sofabatonEntities = allRemoteEntities.filter((eid) =>
      checkIfSofabatonHub(eid, this.hass)
    );
    
    const otherRemoteEntities = allRemoteEntities.filter((eid) =>
      !checkIfSofabatonHub(eid, this.hass)
    );
    
    // Prioritize Sofabaton entities, then other remote entities
    const entities = [...sofabatonEntities, ...otherRemoteEntities];
    
    console.log("Available remote entities:", entities);
    console.log("Current entity value:", this._entity);

    return html`
      <div class="card-config">
        <div class="option">
          <ha-select
            label="Entity (Required)"
            .value=${this._entity}
            .configValue=${"entity"}
            @selected=${this._valueChanged}
            @closed=${(ev) => ev.stopPropagation()}
          >
            ${entities.length === 0 
              ? html`<ha-list-item disabled>No remote entities found</ha-list-item>`
              : entities.map((entity) => {
                  const isSofabaton = checkIfSofabatonHub(entity, this.hass);
                  const friendlyName = this.hass.states[entity]?.attributes?.friendly_name || entity;
                  return html`
                    <ha-list-item .value=${entity}>
                      ${isSofabaton ? '🎮 ' : '📡 '}${friendlyName}
                      <span slot="secondary">${entity}</span>
                    </ha-list-item>
                  `;
                })
            }
          </ha-select>
        </div>
        ${entities.length === 0 
          ? html`<div class="warning">
              <ha-icon icon="mdi:alert"></ha-icon>
              No Sofabaton Hub entities found. Please ensure your integration is properly configured.
            </div>`
          : ''
        }
      </div>
    `;
  }

  _valueChanged(ev) {
    if (!this.config || !this.hass) {
      return;
    }
    const target = ev.target;
    const configValue = target.configValue;
    
    // Ensure value is a string, not an array
    let value = target.value;
    if (Array.isArray(value)) {
      value = value[0]; // If it's an array, take the first element
    }
    
    if (this[`_${configValue}`] === value) {
      return;
    }
    
    const newConfig = {
      ...this.config,
      [configValue]: value,
    };
    
    const messageEvent = new Event("config-changed", {
      bubbles: true,
      composed: true,
    });
    messageEvent.detail = { config: newConfig };
    this.dispatchEvent(messageEvent);
  }

  static get styles() {
    return css`
      .card-config {
        padding: 16px;
      }
      .option {
        padding: 4px 0;
      }
      ha-select {
        width: 100%;
      }
      .warning {
        padding: 12px;
        margin: 8px 0;
        background: var(--warning-color, #ff9800);
        color: var(--text-primary-color);
        border-radius: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
    `;
  }
}

// Register custom elements
customElements.define("sofabaton-main-card", SofabatonMainCard);
customElements.define("sofabaton-main-card-editor", SofabatonMainCardEditor);

// Add this card to Lovelace card picker
// Register custom card - moved to cards.js for unified management
