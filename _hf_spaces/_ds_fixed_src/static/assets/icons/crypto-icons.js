/**
 * Crypto SVG Icons Library
 * Digital cryptocurrency icons for use throughout the application
 */

const CryptoIcons = {
  // Major Cryptocurrencies
  BTC: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#f7931a">
    <path d="M23.638 14.904c-1.602 6.43-8.113 10.34-14.542 8.736C2.67 22.05-1.243 15.525.362 9.105 1.962 2.67 8.475-1.243 14.9.358c6.43 1.605 10.342 8.115 8.738 14.546z"/>
    <path fill="#fff" d="M17.027 10.703c.147-1.003-.607-1.542-1.64-1.902l.335-1.344-1.64-.41-.326 1.308c-.43-.107-.872-.208-1.31-.307l.328-1.315-1.64-.41-.335 1.344c-.357-.082-.708-.16-1.05-.24l.001-.004-1.128-.282-.217.87s.607.14.594.148c.33.083.39.302.38.476l-.383 1.536c.023.005.053.013.086.025l-.087-.022-.537 2.15c-.04.1-.14.25-.367.193.008.011-.595-.148-.595-.148l-.406 1.63 1.64.41.335-1.344c.446.121.875.232 1.297.337l-.338 1.355 1.64.41.335-1.344c2.78.526 4.87.314 5.748-2.2.7-2.01-.035-3.17-1.478-3.926 1.052-.243 1.844-1.003 1.644-2.54zm-2.44 3.35c-.497 1.992-3.858.917-4.947.647l.882-3.537c1.09.27 4.48.808 4.065 2.89zm.495-3.62c-.453 1.816-3.26.893-4.17.666l.8-3.205c.91.227 3.84.648 3.37 2.54z"/>
  </svg>`,
  
  ETH: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#627EEA">
    <path d="M12 0L5.372 12.165 12 16.164l6.628-3.999L12 0z"/>
    <path d="M12 17.984l-6.628-4.001L12 24l6.628-6.017L12 17.984z"/>
  </svg>`,
  
  SOL: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#14F195">
    <path d="M12 0L5.372 12.165 12 16.164l6.628-3.999L12 0z"/>
    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
    <path d="M8 12l4-4 4 4-4 4-4-4z"/>
  </svg>`,
  
  USDT: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#26A17B">
    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0z"/>
    <path fill="#fff" d="M12.87 8.25v-.87h2.898V6h-7.536v1.38h2.898v.87c-2.604.174-4.548.87-4.548 1.74 0 .87 1.944 1.566 4.548 1.74v5.82h2.74v-5.82c2.604-.174 4.548-.87 4.548-1.74 0-.87-1.944-1.566-4.548-1.74zm0 2.898c-2.088-.116-3.624-.522-3.624-1.008 0-.486 1.536-.892 3.624-1.008v2.016zm2.74 0V9.132c2.088.116 3.624.522 3.624 1.008 0 .486-1.536.892-3.624 1.008z"/>
  </svg>`,
  
  BNB: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#F3BA2F">
    <path d="M12 0L8.5 3.5 12 7l3.5-3.5L12 0z"/>
    <path d="M8.5 3.5L5 7l3.5 3.5L12 7 8.5 3.5z"/>
    <path d="M12 7l3.5 3.5L19 7l-3.5-3.5L12 7z"/>
    <path d="M8.5 10.5L5 14l3.5 3.5L12 14l-3.5-3.5z"/>
    <path d="M12 14l3.5 3.5L19 14l-3.5-3.5L12 14z"/>
    <path d="M12 17l3.5 3.5L19 17l-3.5-3.5L12 17z"/>
  </svg>`,
  
  ADA: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0033AD">
    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0z"/>
    <path fill="#fff" d="M12 2L6 7l6 5-6 5 6 5 6-5-6-5 6-5-6-5z"/>
  </svg>`,
  
  XRP: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#23292F">
    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0z"/>
    <path fill="#fff" d="M17.302 4.5h-2.4L12 8.4 9.098 4.5H6.698L12 12.6l5.302-8.1zm-10.604 15h2.4L12 15.6l2.902 3.9h2.4L12 11.4 6.698 19.5z"/>
  </svg>`,
  
  DOGE: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#C2A633">
    <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0z"/>
    <path fill="#fff" d="M8.5 7h7v2h-5v2h4v2h-4v4h-2V7z"/>
  </svg>`,
  
  // Generic crypto icon
  CRYPTO: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="10"/>
    <path d="M8 12h8M12 8v8"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>`,
  
  // Get icon by symbol
  getIcon(symbol) {
    const upperSymbol = (symbol || '').toUpperCase();
    return this[upperSymbol] || this.CRYPTO;
  },
  
  // Render icon as HTML
  render(symbol, size = 24) {
    const icon = this.getIcon(symbol);
    return icon.replace('viewBox="0 0 24 24"', `viewBox="0 0 24 24" width="${size}" height="${size}"`);
  }
};

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CryptoIcons;
}

// Make available globally
window.CryptoIcons = CryptoIcons;

