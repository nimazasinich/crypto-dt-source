/**
 * Trading Pairs Loader
 * Loads trading pairs from trading_pairs.txt and populates comboboxes
 */

let tradingPairs = [];

// Load trading pairs on page load
async function loadTradingPairs() {
    try {
        const response = await fetch('/trading_pairs.txt');
        const text = await response.text();
        tradingPairs = text.trim().split('\n').filter(pair => pair.trim());
        console.log(`Loaded ${tradingPairs.length} trading pairs`);
        return tradingPairs;
    } catch (error) {
        console.error('Error loading trading pairs:', error);
        // Fallback to common pairs
        tradingPairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT'];
        return tradingPairs;
    }
}

// Create a combobox (select with datalist) for trading pairs
function createTradingPairCombobox(id, placeholder = 'Select trading pair', selectedPair = 'BTCUSDT') {
    const datalistId = `${id}-datalist`;
    const options = tradingPairs.map(pair => `<option value="${pair}">`).join('');
    
    return `
        <input 
            type="text" 
            id="${id}" 
            class="form-input trading-pair-input"
            list="${datalistId}"
            placeholder="${placeholder}"
            value="${selectedPair}"
            autocomplete="off"
            style="padding: 10px 15px; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-primary); border-radius: 8px; font-size: 14px; width: 100%;"
        />
        <datalist id="${datalistId}">
            ${options}
        </datalist>
    `;
}

// Create a styled select dropdown
function createTradingPairSelect(id, selectedPair = 'BTCUSDT', className = 'form-select') {
    const options = tradingPairs.map(pair => 
        `<option value="${pair}" ${pair === selectedPair ? 'selected' : ''}>${pair}</option>`
    ).join('');
    
    return `
        <select 
            id="${id}" 
            class="${className}"
            style="padding: 10px 15px; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-primary); border-radius: 8px; font-size: 14px; width: 100%; cursor: pointer;"
        >
            ${options}
        </select>
    `;
}

// Get SVG icon HTML
function getSvgIcon(iconId, size = 20, className = '') {
    return `<svg width="${size}" height="${size}" class="${className}"><use href="#icon-${iconId}"></use></svg>`;
}

// Replace emoji with SVG icon
function replaceEmojiWithSvg(text, emojiMap) {
    let result = text;
    for (const [emoji, iconId] of Object.entries(emojiMap)) {
        result = result.replace(new RegExp(emoji, 'g'), getSvgIcon(iconId));
    }
    return result;
}

// Common emoji to SVG icon mappings
const emojiToSvg = {
    '📊': 'market',
    '🔄': 'refresh',
    '✅': 'check',
    '❌': 'close',
    '⚠️': 'warning',
    '💰': 'diamond',
    '🚀': 'rocket',
    '📈': 'trending-up',
    '📉': 'trending-down',
    '🐋': 'whale',
    '💎': 'diamond',
    '🔥': 'fire',
    '🎯': 'fire',
    '📱': 'monitor',
    '⚙️': 'settings',
    '🏠': 'home',
    '📰': 'news',
    '😊': 'sentiment',
    '🧠': 'brain',
    '🔗': 'link',
    '💾': 'database',
    '₿': 'bitcoin'
};

// Initialize trading pairs on page load
document.addEventListener('DOMContentLoaded', async function() {
    await loadTradingPairs();
    console.log('Trading pairs loaded and ready');
    
    // Dispatch custom event
    document.dispatchEvent(new CustomEvent('tradingPairsLoaded', { detail: { pairs: tradingPairs } }));
});

// Export for use in other scripts
window.TradingPairsLoader = {
    loadTradingPairs,
    createTradingPairCombobox,
    createTradingPairSelect,
    getSvgIcon,
    replaceEmojiWithSvg,
    emojiToSvg,
    getTradingPairs: () => tradingPairs
};

