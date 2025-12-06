/**
 * Futures Tab - Futures Trading Interface
 * 
 * Contains:
 * - Positions display and management
 * - Order book
 * - Balance and margin information
 * - Entry plan calculator
 * - Futures order form
 * - Leverage adjustment
 * - SL/TP configuration
 * 
 * Source: FuturesTradingView.tsx
 * 
 * @version 1.0.0
 * @since Phase 1
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2, TrendingUp, TrendingDown, Wallet, BarChart3 } from 'lucide-react';
import { showToast } from '../../../components/ui/Toast';
import { useConfirmModal } from '../../../components/ui/ConfirmModal';
import { Logger } from '../../../core/Logger';

const logger = Logger.getInstance();

interface FuturesTabProps {
    selectedSymbol: string;
    onSymbolChange: (symbol: string) => void;
    wsData?: any;
}

const SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT'];

export const FuturesTab: React.FC<FuturesTabProps> = ({
    selectedSymbol,
    onSymbolChange,
    wsData
}) => {
    const { confirm, ModalComponent } = useConfirmModal();

    const [symbol, setSymbol] = useState(selectedSymbol.replace('BINANCE:', ''));
    const [positions, setPositions] = useState<any[]>([]);
    const [orders, setOrders] = useState<any[]>([]);
    const [balance, setBalance] = useState<any>(null);
    const [orderbook, setOrderbook] = useState<any>(null);
    const [entryPlan, setEntryPlan] = useState<any>(null);
    const [snapshot, setSnapshot] = useState<any>(null);
    const [currentPrice, setCurrentPrice] = useState(0);

    // Order form states
    const [leverage, setLeverage] = useState(5);
    const [orderSize, setOrderSize] = useState('0.1');
    const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
    const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
    const [orderPrice, setOrderPrice] = useState('');
    const [stopLoss, setStopLoss] = useState('');
    const [takeProfit, setTakeProfit] = useState('');
    const [loading, setLoading] = useState(false);

    // Load data periodically
    useEffect(() => {
        loadData();
        loadSnapshot();
        loadEntryPlan();

        const interval = setInterval(loadData, 5000);
        const snapshotInterval = setInterval(loadSnapshot, 15000);
        const planInterval = setInterval(loadEntryPlan, 15000);

        return () => {
            clearInterval(interval);
            clearInterval(snapshotInterval);
            clearInterval(planInterval);
        };
    }, [symbol]);

    // Update from WebSocket
    useEffect(() => {
        if (wsData?.positionsUpdate) {
            setPositions(wsData.positionsUpdate);
        }
    }, [wsData]);

    const loadData = async () => {
        try {
            const backendPort = import.meta.env.VITE_BACKEND_PORT || '3001';
            const baseUrl = `http://localhost:${backendPort}/api`;

            const [posRes, ordersRes, balanceRes, orderbookRes] = await Promise.all([
                fetch(`${baseUrl}/futures/positions`, { mode: "cors", headers: { "Content-Type": "application/json" } })
                    .catch(() => ({ json: async () => ({ positions: [] }) })),
                fetch(`${baseUrl}/futures/orders`, { mode: "cors", headers: { "Content-Type": "application/json" } })
                    .catch(() => ({ json: async () => ({ orders: [] }) })),
                fetch(`${baseUrl}/futures/balance`, { mode: "cors", headers: { "Content-Type": "application/json" } })
                    .catch(() => ({ json: async () => ({ balance: null }) })),
                fetch(`${baseUrl}/futures/orderbook?symbol=${symbol}`, { mode: "cors", headers: { "Content-Type": "application/json" } })
                    .catch(() => ({ json: async () => ({ orderbook: null }) }))
            ]);

            const posData = await posRes.json();
            const ordersData = await ordersRes.json();
            const balanceData = await balanceRes.json();
            const orderbookData = await orderbookRes.json();

            setPositions(posData.positions || []);
            setOrders(ordersData.orders || []);
            setBalance(balanceData.balance);
            setOrderbook(orderbookData.orderbook);
        } catch (error) {
            logger.error('Failed to load trading data', {}, error as Error);
        }
    };

    const loadSnapshot = async () => {
        try {
            const response = await fetch(
                `http://localhost:${import.meta.env.VITE_BACKEND_PORT || '8001'}/api/scoring/snapshot?symbol=${symbol}&tfs=15m&tfs=1h&tfs=4h`,
                { mode: "cors", headers: { "Content-Type": "application/json" } }
            );

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.snapshot) {
                    setSnapshot(data.snapshot);
                    if (data.snapshot.entryPlan?.entry) {
                        setCurrentPrice(data.snapshot.entryPlan.entry);
                    }
                }
            }
        } catch (error) {
            logger.error('Failed to load snapshot', {}, error as Error);
        }
    };

    const loadEntryPlan = async () => {
        try {
            const accountBalance = balance?.availableBalance || 1000;
            const riskPercent = 2;

            const response = await fetch(
                `http://localhost:${import.meta.env.VITE_BACKEND_PORT || '8001'}/api/entry-plan?symbol=${symbol}&accountBalance=${accountBalance}&riskPercent=${riskPercent}`,
                { mode: "cors", headers: { "Content-Type": "application/json" } }
            );

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.plan) {
                    setEntryPlan(data.plan);
                }
            }
        } catch (error) {
            logger.error('Failed to load entry plan', {}, error as Error);
        }
    };

    const handlePlaceOrder = async () => {
        const confirmed = await confirm(
            'Place Order',
            `Place ${orderSide.toUpperCase()} ${orderType.toUpperCase()} order for ${orderSize} ${symbol}?`,
            'warning'
        );

        if (!confirmed) return;

        setLoading(true);
        try {
            const backendPort = import.meta.env.VITE_BACKEND_PORT || '3001';
            const response = await fetch(`http://localhost:${backendPort}/api/futures/order`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol,
                    side: orderSide.toUpperCase(),
                    type: orderType.toUpperCase(),
                    quantity: parseFloat(orderSize),
                    price: orderType === 'limit' ? parseFloat(orderPrice) : undefined,
                    leverage,
                    stopLoss: stopLoss ? parseFloat(stopLoss) : undefined,
                    takeProfit: takeProfit ? parseFloat(takeProfit) : undefined
                })
            });

            const data = await response.json();

            if (data.success) {
                showToast('success', 'Order Placed', 'Futures order placed successfully.');
                loadData(); // Refresh positions
            } else {
                showToast('error', 'Order Failed', data.message || 'Failed to place order.');
            }
        } catch (error) {
            logger.error('Failed to place order:', {}, error as Error);
            showToast('error', 'Order Failed', 'An error occurred while placing order.');
        } finally {
            setLoading(false);
        }
    };

    const handleClosePosition = async (positionId: string) => {
        const confirmed = await confirm(
            'Close Position',
            'Are you sure you want to close this position?',
            'warning'
        );

        if (!confirmed) return;

        setLoading(true);
        try {
            const backendPort = import.meta.env.VITE_BACKEND_PORT || '3001';
            const response = await fetch(`http://localhost:${backendPort}/api/futures/position/close`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ positionId })
            });

            const data = await response.json();

            if (data.success) {
                showToast('success', 'Position Closed', 'Position closed successfully.');
                loadData();
            } else {
                showToast('error', 'Close Failed', data.message || 'Failed to close position.');
            }
        } catch (error) {
            logger.error('Failed to close position:', {}, error as Error);
            showToast('error', 'Close Failed', 'An error occurred.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <ModalComponent />

            {/* Symbol Selector and Balance */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-card p-4 rounded-lg shadow">
                    <label className="block text-sm font-medium text-muted-foreground mb-2">Symbol</label>
                    <select
                        value={symbol}
                        onChange={(e) => {
                            setSymbol(e.target.value);
                            onSymbolChange(e.target.value);
                        }}
                        className="w-full px-4 py-2 rounded-lg bg-background border border-border focus:ring-2 focus:ring-primary"
                    >
                        {SYMBOLS.map(s => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                </div>

                <div className="bg-card p-4 rounded-lg shadow">
                    <div className="flex items-center gap-2 mb-2">
                        <Wallet className="w-5 h-5 text-muted-foreground" />
                        <span className="text-sm font-medium text-muted-foreground">Balance</span>
                    </div>
                    {balance ? (
                        <div className="space-y-1">
                            <div className="text-2xl font-bold">${balance.availableBalance?.toFixed(2) || '0.00'}</div>
                            <div className="text-sm text-muted-foreground">
                                Used: ${balance.usedMargin?.toFixed(2) || '0.00'}
                            </div>
                        </div>
                    ) : (
                        <div className="text-sm text-muted-foreground">Loading balance...</div>
                    )}
                </div>
            </div>

            {/* Positions Display */}
            <div className="bg-card p-6 rounded-lg shadow-lg">
                <h3 className="text-lg font-semibold mb-4">Open Positions ({positions.length})</h3>

                {positions.length > 0 ? (
                    <div className="space-y-2">
                        {positions.map((pos, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-center justify-between p-4 bg-background rounded-lg"
                            >
                                <div className="flex items-center gap-4">
                                    {pos.side === 'LONG' ? (
                                        <TrendingUp className="w-5 h-5 text-green-500" />
                                    ) : (
                                        <TrendingDown className="w-5 h-5 text-red-500" />
                                    )}
                                    <div>
                                        <div className="font-medium">{pos.symbol}</div>
                                        <div className="text-sm text-muted-foreground">
                                            {pos.size} @ ${pos.entryPrice?.toFixed(2)}
                                        </div>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className={`font-medium ${pos.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                        {pos.pnl >= 0 ? '+' : ''}{pos.pnl?.toFixed(2)} USDT
                                    </div>
                                    <div className="text-sm text-muted-foreground">
                                        {pos.pnlPercent?.toFixed(2)}%
                                    </div>
                                </div>

                                <button
                                    onClick={() => handleClosePosition(pos.id)}
                                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                                >
                                    Close
                                </button>
                            </motion.div>
                        ))}
                    </div>
                ) : (
                    <p className="text-center text-muted-foreground py-8">No open positions</p>
                )}
            </div>

            {/* Order Form */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Left: Order Form */}
                <div className="bg-card p-6 rounded-lg shadow-lg">
                    <h3 className="text-lg font-semibold mb-4">Place Futures Order</h3>

                    <div className="space-y-4">
                        {/* Side Selection */}
                        <div>
                            <label className="block text-sm font-medium text-muted-foreground mb-2">Side</label>
                            <div className="grid grid-cols-2 gap-2">
                                <button
                                    onClick={() => setOrderSide('buy')}
                                    className={`
                    px-4 py-2 rounded-lg font-medium transition-colors
                    ${orderSide === 'buy' ? 'bg-green-500 text-white' : 'bg-background hover:bg-accent'}
                  `}
                                >
                                    Long
                                </button>
                                <button
                                    onClick={() => setOrderSide('sell')}
                                    className={`
                    px-4 py-2 rounded-lg font-medium transition-colors
                    ${orderSide === 'sell' ? 'bg-red-500 text-white' : 'bg-background hover:bg-accent'}
                  `}
                                >
                                    Short
                                </button>
                            </div>
                        </div>

                        {/* Leverage Slider */}
                        <div>
                            <label className="block text-sm font-medium text-muted-foreground mb-2">
                                Leverage: {leverage}x
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="125"
                                value={leverage}
                                onChange={(e) => setLeverage(parseInt(e.target.value))}
                                className="w-full"
                            />
                        </div>

                        {/* Order Size */}
                        <div>
                            <label className="block text-sm font-medium text-muted-foreground mb-2">
                                Size ({symbol.replace('USDT', '')})
                            </label>
                            <input
                                type="number"
                                value={orderSize}
                                onChange={(e) => setOrderSize(e.target.value)}
                                className="w-full px-4 py-2 rounded-lg bg-background border border-border focus:ring-2 focus:ring-primary"
                                step="0.001"
                            />
                        </div>

                        {/* Stop Loss */}
                        <div>
                            <label className="block text-sm font-medium text-muted-foreground mb-2">
                                Stop Loss (Optional)
                            </label>
                            <input
                                type="number"
                                value={stopLoss}
                                onChange={(e) => setStopLoss(e.target.value)}
                                className="w-full px-4 py-2 rounded-lg bg-background border border-border focus:ring-2 focus:ring-primary"
                                placeholder="Price"
                            />
                        </div>

                        {/* Take Profit */}
                        <div>
                            <label className="block text-sm font-medium text-muted-foreground mb-2">
                                Take Profit (Optional)
                            </label>
                            <input
                                type="number"
                                value={takeProfit}
                                onChange={(e) => setTakeProfit(e.target.value)}
                                className="w-full px-4 py-2 rounded-lg bg-background border border-border focus:ring-2 focus:ring-primary"
                                placeholder="Price"
                            />
                        </div>

                        {/* Submit Button */}
                        <button
                            onClick={handlePlaceOrder}
                            disabled={loading}
                            className={`
                w-full px-6 py-3 rounded-lg font-medium flex items-center justify-center gap-2
                ${orderSide === 'buy' ? 'bg-green-500 hover:bg-green-600' : 'bg-red-500 hover:bg-red-600'}
                text-white disabled:opacity-50 disabled:cursor-not-allowed
              `}
                        >
                            {loading && <Loader2 className="w-5 h-5 animate-spin" />}
                            {loading ? 'Placing Order...' : `${orderSide === 'buy' ? 'Long' : 'Short'} ${symbol}`}
                        </button>
                    </div>
                </div>

                {/* Right: Entry Plan & Order Book */}
                <div className="space-y-4">
                    {/* Entry Plan */}
                    {entryPlan && (
                        <div className="bg-card p-6 rounded-lg shadow-lg">
                            <h3 className="text-lg font-semibold mb-4">Entry Plan</h3>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Position Size:</span>
                                    <span className="font-medium">{entryPlan.positionSize?.toFixed(4)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Risk Amount:</span>
                                    <span className="font-medium">${entryPlan.riskAmount?.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Stop Loss:</span>
                                    <span className="font-medium text-red-500">${entryPlan.sl?.toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Take Profit:</span>
                                    <span className="font-medium text-green-500">${entryPlan.tp?.[0]?.toFixed(2)}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Order Book Preview */}
                    {orderbook && (
                        <div className="bg-card p-6 rounded-lg shadow-lg">
                            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <BarChart3 className="w-5 h-5" />
                                Order Book
                            </h3>
                            <div className="space-y-2 text-xs">
                                {orderbook.asks?.slice(0, 5).map((ask: any, idx: number) => (
                                    <div key={idx} className="flex justify-between text-red-500">
                                        <span>${ask[0]}</span>
                                        <span>{ask[1]}</span>
                                    </div>
                                ))}
                                <div className="border-t border-b py-1 text-center font-medium">
                                    ${currentPrice.toFixed(2)}
                                </div>
                                {orderbook.bids?.slice(0, 5).map((bid: any, idx: number) => (
                                    <div key={idx} className="flex justify-between text-green-500">
                                        <span>${bid[0]}</span>
                                        <span>{bid[1]}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FuturesTab;
