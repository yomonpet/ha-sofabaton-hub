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

// Ensure cards are registered after DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', registerCards);
} else {
  registerCards();
}

function registerCards() {
  // Force trigger card registration event
  const event = new Event('ll-rebuild', { bubbles: true });
  document.dispatchEvent(event);
  
  // Delayed trigger to ensure all resources are loaded
  setTimeout(() => {
    if (window.loadCardHelpers) {
      window.loadCardHelpers();
    }
  }, 1000);
}

console.log("Sofabaton Hub cards registered for Lovelace picker"); 