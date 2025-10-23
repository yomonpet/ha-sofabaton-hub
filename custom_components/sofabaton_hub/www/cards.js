// Registration file to ensure cards are visible in Lovelace UI

// Register main card
window.customCards = window.customCards || [];

// Add to custom card list
window.customCards.push({
  type: "sofabaton-main-card",
  name: "Sofabaton Hub",
  preview: true,
  description: "Smart remote control card for managing Sofabaton Hub activities and devices",
  configurable: true,
  documentationURL: "https://github.com/sofabaton/ha-integration"
});

console.log("Sofabaton Hub: Registering cards for Lovelace picker");

// Function to dynamically load ES6 module scripts
function loadModuleScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.type = 'module';
    script.src = url;
    script.onload = () => {
      console.log(`Sofabaton Hub: Loaded module ${url}`);
      resolve();
    };
    script.onerror = (error) => {
      console.error(`Sofabaton Hub: Failed to load module ${url}`, error);
      reject(error);
    };
    document.head.appendChild(script);
  });
}

// Load card modules
function loadCardModules() {
  console.log("Sofabaton Hub: Loading card modules...");

  Promise.all([
    loadModuleScript('/sofabaton_hub/www/main-card.js'),
    loadModuleScript('/sofabaton_hub/www/detail-card.js')
  ])
  .then(() => {
    console.log("Sofabaton Hub: All card modules loaded successfully");

    // Trigger Lovelace to rebuild card list
    const event = new Event('ll-rebuild', { bubbles: true, composed: true });
    document.dispatchEvent(event);

    // Also try to reload card helpers
    setTimeout(() => {
      if (window.loadCardHelpers) {
        window.loadCardHelpers();
      }
    }, 1000);
  })
  .catch((error) => {
    console.error("Sofabaton Hub: Failed to load card modules", error);
  });
}

// Ensure cards are loaded after DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadCardModules);
} else {
  loadCardModules();
}