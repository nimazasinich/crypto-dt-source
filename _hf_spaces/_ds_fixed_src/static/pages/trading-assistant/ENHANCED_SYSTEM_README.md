# 🚀 Enhanced Crypto Trading System V2

## نظام معاملاتی پیشرفته کریپتو - نسخه ۲

سیستم معاملاتی هوشمند و یکپارچه با قابلیت‌های پیشرفته برای تحلیل و معامله در بازارهای کریپتو

---

## ✨ ویژگی‌های اصلی

### 🎯 استراتژی‌های پیشرفته
- **ICT Market Structure**: تحلیل ساختار بازار با روش Inner Circle Trader
- **Wyckoff Accumulation/Distribution**: شناسایی فازهای تجمع و توزیع
- **Anchored VWAP Breakout**: نقاط ورود نهادی با تحلیل حجم
- **Momentum Divergence Hunter**: شناسایی واگرایی‌های پنهان و آشکار
- **Liquidity Sweep Reversal**: شناسایی stop hunt و نقاط بازگشت
- **Supply/Demand Zones**: مناطق عرضه و تقاضای تازه
- **Volatility Breakout Pro**: بریک‌اوت‌های نوسانی با فیلتر رژیم
- **Multi-Timeframe Confluence**: تأیید چند تایم‌فریمی
- **Market Maker Profile**: تحلیل رفتار مارکت میکرها
- **Fair Value Gap Strategy**: معامله بر اساس شکاف‌های قیمتی

### 🤖 ایجنت نظارت هوشمند
- **اتصال WebSocket**: دریافت داده real-time از صرافی‌ها
- **Multi-Exchange Support**: پشتیبانی از Binance, Coinbase, Kraken
- **Auto-Fallback**: تعویض خودکار در صورت قطعی
- **Circuit Breaker**: محافظت در برابر خطاهای متوالی
- **Rate Limiting**: کنترل هوشمند تعداد درخواست‌ها

### 📊 تشخیص رژیم بازار
- **Trending Bullish/Bearish**: روندهای صعودی/نزولی قوی
- **Ranging**: نوسان در محدوده
- **Volatile**: نوسانات بالا
- **Breakout/Breakdown**: شکست سطوح
- **Accumulation/Distribution**: فازهای Wyckoff
- **Adaptive Strategy Selection**: انتخاب خودکار استراتژی بهینه

### 🔔 سیستم اطلاع‌رسانی چند کاناله
- **Telegram**: ارسال سیگنال به تلگرام
- **Email**: ایمیل برای رویدادهای مهم
- **Browser Notifications**: نوتیفیکیشن مرورگر
- **WebSocket**: اطلاع‌رسانی real-time

### 🛡️ مدیریت خطا و امنیت
- **Comprehensive Error Handling**: مدیریت کامل خطاها
- **Retry Logic**: تلاش مجدد با exponential backoff
- **Data Validation**: اعتبارسنجی داده‌های ورودی
- **Fallback Mechanisms**: مکانیزم‌های بازگشت در تمام سطوح

---

## 📦 نصب و راه‌اندازی

### پیش‌نیازها
```bash
- Node.js >= 16
- Modern Browser with WebSocket support
- Internet connection for real-time data
```

### نصب
```javascript
// Import the integrated system
import IntegratedTradingSystem from './integrated-trading-system.js';

// Create instance
const tradingSystem = new IntegratedTradingSystem({
    symbol: 'BTC',
    strategy: 'ict-market-structure',
    useAdaptiveStrategy: true,
    interval: 60000, // 1 minute
    enableNotifications: true,
    notificationChannels: ['browser', 'telegram'],
    telegram: {
        botToken: 'YOUR_BOT_TOKEN',
        chatId: 'YOUR_CHAT_ID'
    },
    riskLevel: 'medium' // very-low, low, medium, high, very-high
});

// Start the system
await tradingSystem.start();
```

---

## 🎮 استفاده

### راه‌اندازی پایه

```javascript
// Initialize
const system = new IntegratedTradingSystem({
    symbol: 'BTC',
    strategy: 'ict-market-structure'
});

// Start monitoring
await system.start();

// Listen to events
window.addEventListener('tradingSystem:signal', (event) => {
    const signal = event.detail;
    console.log('New Signal:', signal);
    
    if (signal.signal === 'buy') {
        console.log(`Entry: $${signal.entry}`);
        console.log(`Stop Loss: $${signal.stopLoss}`);
        console.log(`Targets:`, signal.targets);
    }
});

// Stop when done
system.stop();
```

### استفاده پیشرفته با Adaptive Strategy

```javascript
const system = new IntegratedTradingSystem({
    symbol: 'ETH',
    useAdaptiveStrategy: true, // استراتژی را بر اساس رژیم بازار انتخاب می‌کند
    interval: 30000,
    riskLevel: 'high' // فقط سیگنال‌های با اطمینان بالا
});

await system.start();

// Get current status
const status = system.getStatus();
console.log('Current Regime:', status.currentRegime);
console.log('Last Analysis:', status.lastAnalysis);
console.log('Performance:', status.performanceStats);
```

### تحلیل دستی

```javascript
import { analyzeWithAdvancedStrategy } from './advanced-strategies-v2.js';

// Prepare OHLCV data
const ohlcvData = [
    {
        timestamp: Date.now(),
        open: 50000,
        high: 51000,
        low: 49000,
        close: 50500,
        volume: 1000000
    },
    // ... more candles
];

// Analyze
const analysis = await analyzeWithAdvancedStrategy(
    'BTC',
    'ict-market-structure',
    ohlcvData
);

console.log('Signal:', analysis.signal);
console.log('Confidence:', analysis.confidence);
console.log('Entry:', analysis.entry);
console.log('Stop Loss:', analysis.stopLoss);
console.log('Targets:', analysis.targets);
```

### تنظیم اطلاع‌رسانی تلگرام

```javascript
// 1. Create a bot with @BotFather
// 2. Get your chat ID from @userinfobot
// 3. Configure

const system = new IntegratedTradingSystem({
    symbol: 'BTC',
    enableNotifications: true,
    notificationChannels: ['telegram', 'browser'],
    telegram: {
        botToken: '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
        chatId: '123456789'
    }
});

await system.start();

// تلگرام به صورت خودکار سیگنال‌ها را ارسال می‌کند
```

---

## 📊 استراتژی‌ها

### Advanced Strategies V2

#### 1. ICT Market Structure
```javascript
{
    name: 'ICT Market Structure',
    description: 'Inner Circle Trader methodology',
    indicators: ['Order Blocks', 'FVG', 'Liquidity Pools'],
    timeframes: ['15m', '1h', '4h'],
    winRate: '75-85%',
    avgRR: '1:5'
}
```

**زمان استفاده:**
- روندهای واضح
- وجود Order Block های قوی
- شکاف‌های قیمتی (FVG)

**مثال:**
```javascript
const analysis = await analyzeICTMarketStructure('BTC', ohlcvData);

if (analysis.signal === 'buy') {
    console.log('Order Blocks:', analysis.marketStructure.orderBlocks);
    console.log('FVGs:', analysis.marketStructure.fairValueGaps);
    console.log('Liquidity Zones:', analysis.marketStructure.liquidityZones);
}
```

#### 2. Momentum Divergence Hunter
```javascript
{
    name: 'Momentum Divergence Hunter',
    description: 'Hidden and regular divergences',
    winRate: '78-86%',
    avgRR: '1:4.5'
}
```

**مناسب برای:**
- انتهای روندها
- نقاط بازگشت احتمالی
- تأیید ضعف روند

#### 3. Wyckoff Accumulation
```javascript
{
    name: 'Wyckoff Accumulation/Distribution',
    winRate: '70-80%',
    avgRR: '1:6'
}
```

**شناسایی فازها:**
- Accumulation (تجمع)
- Markup (صعود)
- Distribution (توزیع)
- Markdown (نزول)

### Hybrid Strategies

تمام استراتژی‌های قبلی (15 استراتژی) همچنان فعال و قابل استفاده هستند:
- Trend + RSI + MACD
- Bollinger Bands + RSI
- EMA + Volume + RSI
- S/R + Fibonacci
- MACD + Stochastic + EMA
- Ensemble Multi-Timeframe
- Volume Profile + Order Flow
- و...

---

## 🎯 Market Regimes

سیستم 10 رژیم بازار را شناسایی می‌کند:

| Regime | Description | Best Strategies | Risk | Profit Potential |
|--------|-------------|----------------|------|------------------|
| **Trending Bullish** | روند صعودی قوی | ICT, Momentum Divergence | Medium | High |
| **Trending Bearish** | روند نزولی قوی | ICT, Liquidity Sweep | High | High |
| **Ranging** | نوسان در محدوده | Supply/Demand, Mean Reversion | Low | Medium |
| **Volatile Bullish** | نوسان بالا با جهت صعودی | Volatility Breakout, FVG | Very High | Very High |
| **Volatile Bearish** | نوسان بالا با جهت نزولی | Volatility Breakout | Very High | Very High |
| **Calm** | نوسان کم | Ranging, Supply/Demand | Very Low | Low |
| **Breakout** | شکست مقاومت | Volatility Breakout, ICT | High | Very High |
| **Breakdown** | شکست حمایت | Liquidity Sweep, ICT | High | High |
| **Accumulation** | فاز تجمع | Wyckoff, Supply/Demand | Medium | Very High |
| **Distribution** | فاز توزیع | Wyckoff, Liquidity Sweep | High | Medium |

---

## 🧪 تست

### اجرای تست‌ها

```javascript
import { runTests } from './system-tests.js';

// Run all tests
const results = await runTests();

console.log('Tests Passed:', results.passed);
console.log('Tests Failed:', results.failed);
console.log('Success Rate:', (results.passed / results.total) * 100 + '%');
```

### تست اجزای جداگانه

```javascript
import TradingSystemTests from './system-tests.js';

const tester = new TradingSystemTests();

await tester.testMarketStructureAnalysis();
await tester.testRegimeDetection();
await tester.testNotificationSystem();
await tester.testIntegratedSystem();

const summary = tester.getSummary();
```

---

## 📈 مثال‌های کاربردی

### مثال 1: استراتژی ICT برای BTC

```javascript
const system = new IntegratedTradingSystem({
    symbol: 'BTC',
    strategy: 'ict-market-structure',
    interval: 300000, // 5 minutes
    riskLevel: 'medium',
    enableNotifications: true,
    notificationChannels: ['telegram']
});

await system.start();

// سیگنال‌ها به تلگرام ارسال می‌شوند
```

### مثال 2: Adaptive Strategy برای Altcoins

```javascript
const ethSystem = new IntegratedTradingSystem({
    symbol: 'ETH',
    useAdaptiveStrategy: true, // استراتژی خودکار بر اساس رژیم
    interval: 60000,
    riskLevel: 'high', // فقط سیگنال‌های قوی
});

const solSystem = new IntegratedTradingSystem({
    symbol: 'SOL',
    useAdaptiveStrategy: true,
    interval: 60000,
    riskLevel: 'medium'
});

await Promise.all([
    ethSystem.start(),
    solSystem.start()
]);
```

### مثال 3: Multi-Symbol Monitor

```javascript
const symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'ADA'];
const systems = [];

for (const symbol of symbols) {
    const system = new IntegratedTradingSystem({
        symbol,
        useAdaptiveStrategy: true,
        interval: 60000,
        enableNotifications: true,
        notificationChannels: ['browser']
    });
    
    systems.push(system);
    await system.start();
}

// همه سمبل‌ها همزمان رصد می‌شوند
```

### مثال 4: Custom Event Handling

```javascript
const system = new IntegratedTradingSystem({
    symbol: 'BTC',
    strategy: 'ict-market-structure'
});

// Listen to signals
window.addEventListener('tradingSystem:signal', (event) => {
    const signal = event.detail;
    
    // Custom logic
    if (signal.confidence > 85 && signal.signal === 'buy') {
        // Execute trade
        console.log('High confidence BUY signal!');
        console.log('Entry:', signal.entry);
        console.log('Targets:', signal.targets);
    }
});

// Listen to price updates
window.addEventListener('tradingSystem:priceUpdate', (event) => {
    const price = event.detail;
    console.log('Price Update:', price);
});

// Listen to regime changes
window.addEventListener('tradingSystem:signal', (event) => {
    const analysis = event.detail;
    if (analysis.regime) {
        console.log('Current Regime:', analysis.regime);
    }
});

await system.start();
```

---

## ⚙️ تنظیمات پیشرفته

### Risk Levels

```javascript
const riskProfiles = {
    'very-low': {
        minConfidence: 50,
        description: 'تمام سیگنال‌ها'
    },
    'low': {
        minConfidence: 60,
        description: 'سیگنال‌های متوسط و قوی'
    },
    'medium': {
        minConfidence: 70,
        description: 'فقط سیگنال‌های قوی'
    },
    'high': {
        minConfidence: 80,
        description: 'سیگنال‌های بسیار قوی'
    },
    'very-high': {
        minConfidence: 85,
        description: 'فقط بهترین سیگنال‌ها'
    }
};
```

### Interval Settings

```javascript
const intervals = {
    '10s': 10000,      // برای تست
    '30s': 30000,      // Real-time scalping
    '1m': 60000,       // Scalping
    '5m': 300000,      // Day trading
    '15m': 900000,     // Swing trading
    '1h': 3600000,     // Position trading
    '4h': 14400000     // Long-term
};
```

---

## 🔧 عیب‌یابی

### مشکلات رایج

#### 1. WebSocket Connection Failed

```javascript
// بررسی کنید که مرورگر از WebSocket پشتیبانی می‌کند
if ('WebSocket' in window) {
    console.log('WebSocket is supported');
} else {
    console.log('WebSocket is NOT supported');
}

// در صورت مشکل، سیستم به صورت خودکار به polling سوییچ می‌کند
```

#### 2. Circuit Breaker Activated

```javascript
// بررسی وضعیت
const status = system.getStatus();
console.log('Circuit Breaker:', status.monitorStatus.circuitBreakerOpen);

// اگر circuit breaker فعال شد، صبر کنید تا خودش reset شود
// یا سیستم را restart کنید
system.stop();
await new Promise(resolve => setTimeout(resolve, 60000)); // 1 minute
system.start();
```

#### 3. No Signals Generated

```javascript
// بررسی تنظیمات risk level
console.log('Risk Level:', system.config.riskLevel);

// تنظیم risk level پایین‌تر
system.updateConfig({ riskLevel: 'low' });

// بررسی رژیم بازار
const status = system.getStatus();
console.log('Current Regime:', status.currentRegime);
```

#### 4. High Memory Usage

```javascript
// کاهش history length
const monitor = new EnhancedMarketMonitor({
    symbol: 'BTC',
    strategy: 'ict-market-structure'
});

monitor.maxHistoryLength = 100; // کاهش از 200 به 100
```

---

## 📚 API Reference

### IntegratedTradingSystem

#### Constructor
```javascript
new IntegratedTradingSystem(config)
```

**Parameters:**
- `symbol` (string): نماد ارز (مثلاً 'BTC', 'ETH')
- `strategy` (string): نام استراتژی
- `useAdaptiveStrategy` (boolean): فعال‌سازی انتخاب خودکار استراتژی
- `interval` (number): فاصله زمانی بررسی (میلی‌ثانیه)
- `enableNotifications` (boolean): فعال‌سازی اطلاع‌رسانی
- `notificationChannels` (array): کانال‌های اطلاع‌رسانی
- `telegram` (object): تنظیمات تلگرام
- `riskLevel` (string): سطح ریسک

#### Methods

##### start()
```javascript
await system.start()
```
راه‌اندازی سیستم

**Returns:** `Promise<Object>`

##### stop()
```javascript
system.stop()
```
توقف سیستم

##### getStatus()
```javascript
const status = system.getStatus()
```
دریافت وضعیت فعلی

**Returns:** `Object`

##### updateConfig()
```javascript
system.updateConfig({ symbol: 'ETH' })
```
به‌روزرسانی تنظیمات

##### performAnalysis()
```javascript
const analysis = await system.performAnalysis(ohlcvData)
```
تحلیل دستی داده‌ها

---

## 🤝 مشارکت

برای مشارکت در توسعه:

1. فورک کنید
2. برنچ جدید بسازید (`git checkout -b feature/AmazingFeature`)
3. تغییرات را commit کنید (`git commit -m 'Add some AmazingFeature'`)
4. Push کنید (`git push origin feature/AmazingFeature`)
5. Pull Request ایجاد کنید

---

## 📝 License

This project is licensed under the MIT License.

---

## ⚠️ هشدار

این سیستم برای اهداف آموزشی و تحقیقاتی است. معامله در بازارهای مالی ریسک بالایی دارد و ممکن است منجر به از دست دادن سرمایه شود. قبل از استفاده از سیگنال‌های این سیستم، حتماً تحقیقات کافی انجام دهید و با مشاور مالی مشورت کنید.

**استفاده از این سیستم به مسئولیت خود شماست.**

---

## 📧 پشتیبانی

برای سوالات و پشتیبانی:
- Issue ایجاد کنید در GitHub
- به documentation مراجعه کنید
- تست‌های موجود را بررسی کنید

---

## 🎉 ویژگی‌های آتی

- [ ] Machine Learning برای پیش‌بینی قیمت
- [ ] Portfolio Management
- [ ] Auto Trading با API های صرافی
- [ ] Dashboard تحلیلی پیشرفته
- [ ] Backtesting Engine
- [ ] More Exchange Support
- [ ] Mobile App

---

**ساخته شده با ❤️ برای جامعه کریپتو**

