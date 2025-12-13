/**
 * Telegram Notification Service
 * Handles sending trading signals to Telegram with error handling
 */

export class TelegramService {
  constructor() {
    this.botToken = null;
    this.chatId = null;
    this.enabled = false;
    this.errorCount = 0;
    this.maxErrors = 3;
  }

  /**
   * Initializes Telegram service from settings
   */
  async init() {
    try {
      const settings = await this.loadSettings();
      this.botToken = settings.telegram?.botToken || null;
      this.chatId = settings.telegram?.chatId || null;
      this.enabled = settings.notifications?.telegramEnabled || false;
      
      if (this.botToken && this.chatId) {
        console.log('[TelegramService] Initialized');
      } else {
        console.log('[TelegramService] Not configured');
      }
    } catch (error) {
      console.warn('[TelegramService] Init error (non-critical):', error);
      this.enabled = false;
    }
  }

  /**
   * Loads settings from localStorage or API
   */
  async loadSettings() {
    try {
      const stored = localStorage.getItem('app_settings');
      if (stored) {
        return JSON.parse(stored);
      }
      
      const response = await fetch('/api/settings');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('[TelegramService] Could not load settings:', error);
    }
    
    return {};
  }

  /**
   * Sends trading signal to Telegram
   * @param {Object} signalData - Signal data to send
   * @returns {Promise<boolean>} Success status
   */
  async sendSignal(signalData) {
    if (!this.enabled || !this.botToken || !this.chatId) {
      return false;
    }

    try {
      const message = this.formatSignalMessage(signalData);
      
      const response = await fetch(`https://api.telegram.org/bot${this.botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: this.chatId,
          text: message,
          parse_mode: 'Markdown',
          disable_web_page_preview: true,
        }),
        signal: AbortSignal.timeout(10000),
      });

      const data = await response.json();
      
      if (data.ok) {
        this.errorCount = 0;
        console.log('[TelegramService] Signal sent successfully');
        return true;
      } else {
        throw new Error(data.description || 'Telegram API error');
      }
    } catch (error) {
      this.errorCount++;
      console.error('[TelegramService] Send error:', error.message);
      
      if (this.errorCount >= this.maxErrors) {
        console.warn('[TelegramService] Too many errors, disabling temporarily');
        this.enabled = false;
      }
      
      return false;
    }
  }

  /**
   * Formats signal data into Telegram message
   */
  formatSignalMessage(signalData) {
    const { symbol, signal, strategy, confidence, price, takeProfitLevels, stopLoss, levels, riskReward } = signalData;
    
    const signalEmoji = signal === 'buy' ? '🟢' : signal === 'sell' ? '🔴' : '🟡';
    const signalText = signal.toUpperCase();
    
    let message = `${signalEmoji} *${symbol} Trading Signal*\n\n`;
    message += `📊 *Strategy:* ${strategy}\n`;
    message += `🎯 *Signal:* ${signalText}\n`;
    message += `💪 *Confidence:* ${confidence}%\n`;
    message += `💰 *Price:* $${price.toLocaleString()}\n\n`;
    
    if (takeProfitLevels && takeProfitLevels.length > 0) {
      message += `*Take Profit Levels:*\n`;
      takeProfitLevels.forEach((tp, idx) => {
        const profit = ((tp.level / price - 1) * 100).toFixed(2);
        message += `  ${tp.type}: $${tp.level.toLocaleString()} (+${profit}%)\n`;
      });
      message += `\n`;
    }
    
    if (stopLoss) {
      const risk = Math.abs(((stopLoss / price - 1) * 100)).toFixed(2);
      message += `🛑 *Stop Loss:* $${stopLoss.toLocaleString()} (-${risk}%)\n`;
    }
    
    if (riskReward) {
      message += `⚖️ *Risk/Reward:* ${riskReward.riskRewardRatio}\n`;
    }
    
    if (levels) {
      if (levels.resistance && levels.resistance.length > 0) {
        message += `\n*Resistance Levels:*\n`;
        levels.resistance.slice(0, 2).forEach(r => {
          message += `  $${r.level.toLocaleString()} (${r.strength})\n`;
        });
      }
      
      if (levels.support && levels.support.length > 0) {
        message += `\n*Support Levels:*\n`;
        levels.support.slice(0, 2).forEach(s => {
          message += `  $${s.level.toLocaleString()} (${s.strength})\n`;
        });
      }
    }
    
    message += `\n_Time: ${new Date().toLocaleString()}_`;
    
    return message;
  }

  /**
   * Tests Telegram connection
   */
  async testConnection(botToken, chatId) {
    try {
      const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: '🧪 *Test Message*\n\nTelegram integration is working correctly!',
          parse_mode: 'Markdown',
        }),
        signal: AbortSignal.timeout(10000),
      });

      const data = await response.json();
      return data.ok;
    } catch (error) {
      console.error('[TelegramService] Test error:', error);
      return false;
    }
  }

  /**
   * Updates Telegram configuration
   */
  updateConfig(botToken, chatId, enabled) {
    this.botToken = botToken;
    this.chatId = chatId;
    this.enabled = enabled && botToken && chatId;
    this.errorCount = 0;
  }

  /**
   * Checks if Telegram is properly configured
   */
  isConfigured() {
    return !!(this.botToken && this.chatId);
  }

  /**
   * Gets service status
   */
  getStatus() {
    return {
      enabled: this.enabled,
      configured: this.isConfigured(),
      errorCount: this.errorCount,
    };
  }
}

