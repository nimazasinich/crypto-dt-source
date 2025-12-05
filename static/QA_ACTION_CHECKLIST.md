# 🚨 QA Action Checklist - Critical Fixes Required

**Date:** 2025-12-03  
**Priority:** HIGH - Must fix before production

---

## ❌ CRITICAL FIXES (Do First)

### 1. Remove Demo OHLCV Data Generation
**File:** `static/pages/trading-assistant/trading-assistant-professional.js`

**Current Code (Lines 485-520):**
```javascript
// Last resort: Generate demo OHLCV data
console.warn(`[API] All sources failed for ${symbol} OHLCV, generating demo data`);
return this.generateDemoOHLCV(crypto.demoPrice || 1000, limit);

// ... generateDemoOHLCV function exists ...
```

**Fix Required:**
- ❌ Remove `generateDemoOHLCV()` function call
- ❌ Remove `generateDemoOHLCV()` function definition
- ✅ Replace with error state:
```javascript
// All sources failed - show error
throw new Error(`Unable to fetch real OHLCV data for ${symbol} from all sources`);
```

**Status:** ❌ NOT FIXED

---

### 2. Increase Aggressive Polling Intervals

#### 2.1 Trading Assistant Ultimate
**File:** `static/pages/trading-assistant/trading-assistant-ultimate.js`
- **Current:** `updateInterval: 3000` (3 seconds)
- **Fix:** Change to `updateInterval: 30000` (30 seconds) or `60000` (60 seconds)
- **Status:** ❌ NOT FIXED

#### 2.2 Trading Assistant Real
**File:** `static/pages/trading-assistant/trading-assistant-real.js`
- **Current:** `updateInterval: 5000` (5 seconds)
- **Fix:** Change to `updateInterval: 20000` (20 seconds) or `30000` (30 seconds)
- **Status:** ❌ NOT FIXED

#### 2.3 Trading Assistant Enhanced
**File:** `static/pages/trading-assistant/trading-assistant-enhanced.js`
- **Current:** `updateInterval: 5000` (5 seconds)
- **Fix:** Change to `updateInterval: 20000` (20 seconds) or `30000` (30 seconds)
- **Status:** ❌ NOT FIXED

---

### 3. Remove Direct External API Calls
**File:** `static/pages/trading-assistant/trading-assistant-professional.js`

**Current Code (Lines 334-362):**
```javascript
// Priority 2: Try CoinGecko directly (as fallback)
try {
    const url = `${API_CONFIG.coingecko}/simple/price?ids=${coinId}&vs_currencies=usd`;
    // ... direct call ...
}

// Priority 3: Try Binance directly (last resort, may timeout - but skip if likely to fail)
// Skip direct Binance calls to avoid CORS/timeout issues - rely on server's unified API
```

**Fix Required:**
- ❌ Remove direct CoinGecko call (lines 334-362)
- ✅ Keep only server unified API call
- ✅ Throw error if server API fails (no fallback to external)

**Status:** ⚠️ PARTIALLY FIXED (Binance removed, CoinGecko still present)

---

## ⚠️ HIGH PRIORITY FIXES (Do Next)

### 4. Add Rate Limiting
**Action:** Implement client-side rate limiting
**Location:** `static/shared/js/core/api-client.js`
**Status:** ❌ NOT IMPLEMENTED

### 5. Improve Error Messages
**Action:** Add descriptive error messages with troubleshooting tips
**Status:** ⚠️ PARTIAL (some modules have good errors, others don't)

---

## ✅ COMPLETED FIXES (Already Done)

- ✅ Technical Analysis Professional - Demo data removed
- ✅ AI Analyst - Mock data removed, error states added
- ✅ Ticker speed reduced to 1/4 (480s)
- ✅ Help link added to sidebar

---

## 📋 Verification Steps

After fixes are applied, verify:

1. ✅ No `generateDemoOHLCV` function exists in codebase
2. ✅ All polling intervals are ≥ 20 seconds
3. ✅ No direct `api.binance.com` or `api.coingecko.com` calls from frontend
4. ✅ Error states show when all APIs fail (no fake data)
5. ✅ Console shows warnings for failed API calls (not errors)

---

## 🎯 Success Criteria

- [ ] Zero mock/demo data generation
- [ ] All polling intervals ≥ 20 seconds
- [ ] Zero direct external API calls from frontend
- [ ] All error states show proper messages
- [ ] No CORS errors in console
- [ ] No timeout errors from aggressive polling

---

**Last Updated:** 2025-12-03  
**Next Review:** After fixes applied

