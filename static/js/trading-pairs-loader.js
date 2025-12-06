/**
 * Trading Pairs Loader - Provides cryptocurrency list for combo boxes
 * Version: 1.0.0
 * Updated: 2025-12-06
 */

class TradingPairsLoader {
    constructor() {
        this.pairs = null;
        this.loaded = false;
        this.loading = false;
        this.loadPromise = null;
    }

    /**
     * Load cryptocurrency pairs from JSON file
     * @returns {Promise<Array>} Array of cryptocurrency objects
     */
    async load() {
        // Return cached data if already loaded
        if (this.loaded && this.pairs) {
            return this.pairs;
        }

        // Return existing promise if already loading
        if (this.loading && this.loadPromise) {
            return this.loadPromise;
        }

        // Start loading
        this.loading = true;
        this.loadPromise = this._fetchPairs();

        try {
            this.pairs = await this.loadPromise;
            this.loaded = true;
            console.log(`✅ [TradingPairs] Loaded ${this.pairs.length} cryptocurrencies`);
            return this.pairs;
        } catch (error) {
            console.error('❌ [TradingPairs] Failed to load:', error);
            this.loaded = false;
            // Return fallback data
            return this._getFallbackPairs();
        } finally {
            this.loading = false;
        }
    }

    /**
     * Fetch pairs from JSON file
     */
    async _fetchPairs() {
        const response = await fetch('/static/data/cryptocurrencies.json');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        return data.cryptocurrencies || [];
    }

    /**
     * Get fallback pairs if loading fails
     */
    _getFallbackPairs() {
        return [
            {id: "bitcoin", symbol: "BTC", name: "Bitcoin", pair: "BTCUSDT", rank: 1},
            {id: "ethereum", symbol: "ETH", name: "Ethereum", pair: "ETHUSDT", rank: 2},
            {id: "binancecoin", symbol: "BNB", name: "BNB", pair: "BNBUSDT", rank: 3},
            {id: "solana", symbol: "SOL", name: "Solana", pair: "SOLUSDT", rank: 4},
            {id: "ripple", symbol: "XRP", name: "XRP", pair: "XRPUSDT", rank: 5},
            {id: "cardano", symbol: "ADA", name: "Cardano", pair: "ADAUSDT", rank: 6},
            {id: "dogecoin", symbol: "DOGE", name: "Dogecoin", pair: "DOGEUSDT", rank: 7},
            {id: "matic-network", symbol: "MATIC", name: "Polygon", pair: "MATICUSDT", rank: 8},
            {id: "polkadot", symbol: "DOT", name: "Polkadot", pair: "DOTUSDT", rank: 9},
            {id: "avalanche", symbol: "AVAX", name: "Avalanche", pair: "AVAXUSDT", rank: 10}
        ];
    }

    /**
     * Get all pairs
     */
    async getPairs() {
        return await this.load();
    }

    /**
     * Get top N pairs by rank
     */
    async getTopPairs(n = 50) {
        const pairs = await this.load();
        return pairs.slice(0, n);
    }

    /**
     * Search pairs by symbol, name, or id
     */
    async searchPairs(query) {
        const pairs = await this.load();
        const lowerQuery = query.toLowerCase();
        return pairs.filter(p => 
            p.symbol.toLowerCase().includes(lowerQuery) ||
            p.name.toLowerCase().includes(lowerQuery) ||
            p.id.toLowerCase().includes(lowerQuery)
        );
    }

    /**
     * Get pair by symbol
     */
    async getPairBySymbol(symbol) {
        const pairs = await this.load();
        return pairs.find(p => p.symbol.toUpperCase() === symbol.toUpperCase());
    }

    /**
     * Populate a select element with trading pairs
     * @param {HTMLSelectElement} selectElement - The select element to populate
     * @param {Object} options - Configuration options
     */
    async populateSelect(selectElement, options = {}) {
        const {
            limit = null,
            placeholder = "Select a cryptocurrency...",
            selectedValue = null,
            showRank = true,
            showSymbol = true,
            addAllOption = false
        } = options;

        // Add placeholder option
        if (placeholder) {
            const placeholderOption = document.createElement('option');
            placeholderOption.value = '';
            placeholderOption.textContent = placeholder;
            placeholderOption.disabled = true;
            placeholderOption.selected = !selectedValue;
            selectElement.appendChild(placeholderOption);
        }

        // Add "All" option if requested
        if (addAllOption) {
            const allOption = document.createElement('option');
            allOption.value = 'all';
            allOption.textContent = '🌐 All Cryptocurrencies';
            selectElement.appendChild(allOption);
        }

        // Load pairs
        const pairs = limit ? await this.getTopPairs(limit) : await this.getPairs();

        // Populate options
        pairs.forEach(pair => {
            const option = document.createElement('option');
            option.value = pair.symbol;
            option.dataset.pair = pair.pair;
            option.dataset.id = pair.id;
            
            // Build option text
            let text = '';
            if (showRank) text += `#${pair.rank} `;
            text += pair.name;
            if (showSymbol) text += ` (${pair.symbol})`;
            
            option.textContent = text;
            
            // Set selected if matches
            if (selectedValue && (
                pair.symbol.toUpperCase() === selectedValue.toUpperCase() ||
                pair.pair === selectedValue ||
                pair.id === selectedValue
            )) {
                option.selected = true;
            }
            
            selectElement.appendChild(option);
        });

        console.log(`✅ [TradingPairs] Populated select with ${pairs.length} options`);
    }

    /**
     * Create a searchable dropdown with autocomplete
     * @param {HTMLElement} container - Container element
     * @param {Object} options - Configuration options
     */
    async createSearchableDropdown(container, options = {}) {
        const {
            limit = null,
            placeholder = "Search cryptocurrency...",
            onSelect = null,
            className = 'crypto-searchable-dropdown'
        } = options;

        // Load pairs
        const allPairs = limit ? await this.getTopPairs(limit) : await this.getPairs();

        // Create HTML structure
        container.innerHTML = `
            <div class="${className}">
                <div class="crypto-search-input-wrapper">
                    <input 
                        type="text" 
                        class="crypto-search-input form-input" 
                        placeholder="${placeholder}"
                        autocomplete="off"
                    />
                    <div class="crypto-dropdown-icon">▼</div>
                </div>
                <div class="crypto-dropdown-list" style="display: none;">
                    <div class="crypto-dropdown-items"></div>
                </div>
            </div>
        `;

        const input = container.querySelector('.crypto-search-input');
        const dropdownList = container.querySelector('.crypto-dropdown-list');
        const dropdownItems = container.querySelector('.crypto-dropdown-items');

        let filteredPairs = allPairs;

        // Render dropdown items
        const renderItems = (pairs) => {
            dropdownItems.innerHTML = '';
            pairs.forEach(pair => {
                const item = document.createElement('div');
                item.className = 'crypto-dropdown-item';
                item.dataset.symbol = pair.symbol;
                item.dataset.pair = pair.pair;
                item.dataset.id = pair.id;
                item.innerHTML = `
                    <span class="crypto-rank">#${pair.rank}</span>
                    <span class="crypto-name">${pair.name}</span>
                    <span class="crypto-symbol">${pair.symbol}</span>
                `;
                item.addEventListener('click', () => {
                    input.value = `${pair.name} (${pair.symbol})`;
                    dropdownList.style.display = 'none';
                    if (onSelect) onSelect(pair);
                });
                dropdownItems.appendChild(item);
            });
        };

        // Initial render
        renderItems(filteredPairs);

        // Search functionality
        input.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            filteredPairs = allPairs.filter(p =>
                p.name.toLowerCase().includes(query) ||
                p.symbol.toLowerCase().includes(query)
            );
            renderItems(filteredPairs);
            dropdownList.style.display = 'block';
        });

        // Show/hide dropdown
        input.addEventListener('focus', () => {
            dropdownList.style.display = 'block';
        });

        document.addEventListener('click', (e) => {
            if (!container.contains(e.target)) {
                dropdownList.style.display = 'none';
            }
        });

        console.log(`✅ [TradingPairs] Created searchable dropdown with ${allPairs.length} items`);
    }
}

// Create singleton instance
const tradingPairsLoader = new TradingPairsLoader();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TradingPairsLoader, tradingPairsLoader };
}

// Make available globally
window.tradingPairsLoader = tradingPairsLoader;
window.TradingPairsLoader = TradingPairsLoader;

console.log('✅ [TradingPairs] Loader initialized');
