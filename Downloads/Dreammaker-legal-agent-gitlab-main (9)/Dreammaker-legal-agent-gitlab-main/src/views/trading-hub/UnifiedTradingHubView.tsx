/**
 * Unified Trading Hub View - Phase 2 Enhanced Implementation
 * 
 * Consolidates 6 trading pages into one unified interface with 5 tabs:
 * - Charts: TradingView widgets and market screener
 * - Spot: Spot trading with scoring system
 * - Futures: Futures trading (DEFAULT)
 * - Positions: Position and order management
 * - Portfolio: Portfolio overview and risk center
 * 
 * Phase 2 Features:
 * - Quick Actions Bar (floating action buttons)
 * - Tab Presets (save/load custom layouts)
 * - Cross-Tab Features (unified search, global filters)
 * - Shared WebSocket connection for real-time updates
 * - Lazy loading for heavy components
 * - Keyboard shortcuts (Cmd/Ctrl + 1-5)
 * - Backward compatibility via route redirects
 * 
 * @version 2.0.0
 * @since Phase 1, Enhanced in Phase 2
 */

import React, { useState, useEffect, Suspense, lazy, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    BarChart3,
    TrendingUp,
    CircleDollarSign,
    List,
    Wallet,
    Zap,
    Activity,
    Search,
    Filter,
    Settings,
    Bookmark,
    Layout,
    Plus,
    X,
    Check,
    ChevronDown,
    RefreshCw,
    Bell,
    Target,
    Shield,
    ArrowUpRight,
    ArrowDownRight,
    Maximize2,
    Minimize2,
    Save,
    FolderOpen,
    Trash2,
    Copy,
    MoreHorizontal,
} from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';
import { toast } from '../../components/ui/Toast';

// Lazy load Charts tab (heavy TradingView widgets)
const ChartsTab = lazy(() => import('./tabs/ChartsTab'));

// Regular imports for other tabs
import { SpotTab } from './tabs/SpotTab';
import { FuturesTab } from './tabs/FuturesTab';
import { PositionsTab } from './tabs/PositionsTab';
import { PortfolioTab } from './tabs/PortfolioTab';

type TabId = 'charts' | 'spot' | 'futures' | 'positions' | 'portfolio';

interface TabConfig {
    id: TabId;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    component: React.ComponentType<TabProps>;
    lazy?: boolean;
    gradient: string;
    glowColor: string;
    description: string;
}

interface TabProps {
    selectedSymbol: string;
    onSymbolChange: (symbol: string) => void;
    wsData?: any;
    globalFilters?: GlobalFilters;
}

interface GlobalFilters {
    timeframe: string;
    exchange: string;
    marketType: 'all' | 'spot' | 'futures';
    minVolume: number;
}

interface TabPreset {
    id: string;
    name: string;
    tabs: TabId[];
    defaultTab: TabId;
    filters: GlobalFilters;
    createdAt: Date;
}

interface QuickAction {
    id: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    shortcut?: string;
    variant: 'primary' | 'success' | 'warning' | 'danger';
    onClick: () => void;
}

const TABS: TabConfig[] = [
    {
        id: 'charts',
        label: 'Charts',
        icon: BarChart3,
        component: ChartsTab as any,
        lazy: true,
        gradient: 'from-purple-500 via-purple-400 to-violet-500',
        glowColor: 'rgba(139, 92, 246, 0.5)',
        description: 'Advanced charting & analysis'
    },
    {
        id: 'spot',
        label: 'Spot',
        icon: CircleDollarSign,
        component: SpotTab,
        gradient: 'from-emerald-500 via-emerald-400 to-teal-500',
        glowColor: 'rgba(16, 185, 129, 0.5)',
        description: 'Spot trading with AI scoring'
    },
    {
        id: 'futures',
        label: 'Futures',
        icon: TrendingUp,
        component: FuturesTab,
        gradient: 'from-blue-500 via-blue-400 to-cyan-500',
        glowColor: 'rgba(59, 130, 246, 0.5)',
        description: 'Leveraged futures trading'
    },
    {
        id: 'positions',
        label: 'Positions',
        icon: List,
        component: PositionsTab,
        gradient: 'from-orange-500 via-orange-400 to-amber-500',
        glowColor: 'rgba(249, 115, 22, 0.5)',
        description: 'Manage open positions'
    },
    {
        id: 'portfolio',
        label: 'Portfolio',
        icon: Wallet,
        component: PortfolioTab,
        gradient: 'from-pink-500 via-pink-400 to-rose-500',
        glowColor: 'rgba(236, 72, 153, 0.5)',
        description: 'Portfolio & risk overview'
    }
];

// Default presets
const DEFAULT_PRESETS: TabPreset[] = [
    {
        id: 'trader',
        name: 'Active Trader',
        tabs: ['charts', 'futures', 'positions'],
        defaultTab: 'futures',
        filters: { timeframe: '15m', exchange: 'all', marketType: 'futures', minVolume: 1000000 },
        createdAt: new Date(),
    },
    {
        id: 'investor',
        name: 'Long-term Investor',
        tabs: ['charts', 'spot', 'portfolio'],
        defaultTab: 'portfolio',
        filters: { timeframe: '1d', exchange: 'all', marketType: 'spot', minVolume: 500000 },
        createdAt: new Date(),
    },
    {
        id: 'analyst',
        name: 'Market Analyst',
        tabs: ['charts', 'positions', 'portfolio'],
        defaultTab: 'charts',
        filters: { timeframe: '4h', exchange: 'all', marketType: 'all', minVolume: 100000 },
        createdAt: new Date(),
    },
];

export const UnifiedTradingHubView: React.FC = () => {
    // Get initial tab from URL params or default to 'futures'
    const getInitialTab = (): TabId => {
        const params = new URLSearchParams(window.location.search);
        const tabParam = params.get('tab') as TabId;
        return TABS.find(t => t.id === tabParam)?.id || 'futures';
    };

    const [activeTab, setActiveTab] = useState<TabId>(getInitialTab());
    const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
    const [hoveredTab, setHoveredTab] = useState<TabId | null>(null);
    
    // Phase 2: New state
    const [showSearch, setShowSearch] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showFilters, setShowFilters] = useState(false);
    const [showPresets, setShowPresets] = useState(false);
    const [showQuickActions, setShowQuickActions] = useState(true);
    const [presets, setPresets] = useState<TabPreset[]>(DEFAULT_PRESETS);
    const [activePreset, setActivePreset] = useState<string | null>(null);
    const [isFullscreen, setIsFullscreen] = useState(false);
    
    // Global filters
    const [globalFilters, setGlobalFilters] = useState<GlobalFilters>({
        timeframe: '15m',
        exchange: 'all',
        marketType: 'all',
        minVolume: 0,
    });

    // Shared WebSocket connections for all tabs
    const priceData = useWebSocket({ topic: 'price_update', enabled: true });
    const scoringData = useWebSocket({ topic: 'scoring_snapshot', enabled: true });
    const positionsData = useWebSocket({ topic: 'positions_update', enabled: true });

    // Combine WebSocket data for tabs
    const wsData = useMemo(() => ({
        priceUpdate: priceData.data,
        scoringSnapshot: scoringData.data,
        positionsUpdate: positionsData.data,
        isConnected: priceData.isConnected || scoringData.isConnected || positionsData.isConnected
    }), [priceData.data, priceData.isConnected, scoringData.data, scoringData.isConnected, positionsData.data, positionsData.isConnected]);

    // Quick Actions
    const quickActions: QuickAction[] = useMemo(() => [
        {
            id: 'quick-buy',
            label: 'Quick Buy',
            icon: ArrowUpRight,
            shortcut: 'B',
            variant: 'success',
            onClick: () => {
                toast.success('Quick Buy', `Opening buy order for ${selectedSymbol}`);
            },
        },
        {
            id: 'quick-sell',
            label: 'Quick Sell',
            icon: ArrowDownRight,
            shortcut: 'S',
            variant: 'danger',
            onClick: () => {
                toast.warning('Quick Sell', `Opening sell order for ${selectedSymbol}`);
            },
        },
        {
            id: 'close-all',
            label: 'Close All',
            icon: X,
            shortcut: 'C',
            variant: 'warning',
            onClick: () => {
                toast.warning('Close All Positions', 'Are you sure? This will close all open positions.');
            },
        },
        {
            id: 'set-alert',
            label: 'Set Alert',
            icon: Bell,
            shortcut: 'A',
            variant: 'primary',
            onClick: () => {
                toast.info('Price Alert', `Setting alert for ${selectedSymbol}`);
            },
        },
    ], [selectedSymbol]);

    // Handle tab changes
    const handleTabChange = useCallback((tabId: TabId) => {
        setActiveTab(tabId);
        const url = new URL(window.location.href);
        url.searchParams.set('tab', tabId);
        window.history.replaceState({}, '', url.toString());
    }, []);

    // Handle preset selection
    const handlePresetSelect = useCallback((preset: TabPreset) => {
        setActivePreset(preset.id);
        setGlobalFilters(preset.filters);
        handleTabChange(preset.defaultTab);
        toast.success('Preset Loaded', `Switched to "${preset.name}" preset`);
        setShowPresets(false);
    }, [handleTabChange]);

    // Save current layout as preset
    const saveCurrentAsPreset = useCallback(() => {
        const name = prompt('Enter preset name:');
        if (!name) return;

        const newPreset: TabPreset = {
            id: `custom-${Date.now()}`,
            name,
            tabs: TABS.map(t => t.id),
            defaultTab: activeTab,
            filters: globalFilters,
            createdAt: new Date(),
        };

        setPresets(prev => [...prev, newPreset]);
        setActivePreset(newPreset.id);
        toast.success('Preset Saved', `"${name}" has been saved`);
    }, [activeTab, globalFilters]);

    // Delete preset
    const deletePreset = useCallback((presetId: string) => {
        setPresets(prev => prev.filter(p => p.id !== presetId));
        if (activePreset === presetId) {
            setActivePreset(null);
        }
        toast.info('Preset Deleted', 'Preset has been removed');
    }, [activePreset]);

    // Sync active tab with URL params
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const tabParam = params.get('tab') as TabId;
        if (tabParam && TABS.find(t => t.id === tabParam)) {
            setActiveTab(tabParam);
        }
    }, []);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyPress = (e: KeyboardEvent) => {
            // Tab switching: Cmd/Ctrl + 1-5
            if ((e.metaKey || e.ctrlKey) && e.key >= '1' && e.key <= '5') {
                e.preventDefault();
                const index = parseInt(e.key) - 1;
                if (TABS[index]) {
                    handleTabChange(TABS[index].id);
                }
            }

            // Global search: Cmd/Ctrl + K
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                setShowSearch(true);
            }

            // Quick actions shortcuts (when not in input)
            if (!e.metaKey && !e.ctrlKey && !e.altKey) {
                const target = e.target as HTMLElement;
                if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
                    const action = quickActions.find(a => a.shortcut?.toLowerCase() === e.key.toLowerCase());
                    if (action) {
                        e.preventDefault();
                        action.onClick();
                    }
                }
            }

            // Escape to close modals
            if (e.key === 'Escape') {
                setShowSearch(false);
                setShowFilters(false);
                setShowPresets(false);
            }

            // Fullscreen toggle: F
            if (e.key === 'f' && !e.metaKey && !e.ctrlKey) {
                const target = e.target as HTMLElement;
                if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
                    setIsFullscreen(prev => !prev);
                }
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [handleTabChange, quickActions]);

    const ActiveComponent = TABS.find(t => t.id === activeTab)?.component;
    const activeTabConfig = TABS.find(t => t.id === activeTab);

    return (
        <div className={`min-h-screen bg-[color:var(--surface-page)] ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
            {/* Enhanced Header */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`sticky top-0 z-20 border-b border-purple-500/20 ${isFullscreen ? 'hidden' : ''}`}
                style={{
                    background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.98) 0%, rgba(25, 20, 40, 0.98) 100%)',
                    backdropFilter: 'blur(20px)',
                    boxShadow: '0 4px 30px rgba(0, 0, 0, 0.3)',
                }}
            >
                <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="py-4">
                        {/* Title and Status */}
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-4">
                                {/* Logo */}
                                <div
                                    className="p-2.5 rounded-xl shadow-lg"
                                    style={{
                                        background: 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
                                        boxShadow: '0 8px 24px rgba(139, 92, 246, 0.4)',
                                    }}
                                >
                                    <Zap className="w-6 h-6 text-white" style={{
                                        filter: 'drop-shadow(0 0 8px rgba(255, 255, 255, 0.5))'
                                    }} />
                                </div>
                                
                                <div>
                                    <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
                                        Trading Hub
                                    </h1>
                                    <p className="text-xs text-slate-400 mt-0.5">
                                        {activePreset ? `Preset: ${presets.find(p => p.id === activePreset)?.name}` : 'Unified trading interface'} • Real-time data
                                    </p>
                                </div>
                            </div>

                            {/* Header Actions */}
                            <div className="flex items-center gap-2">
                                {/* Global Search */}
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setShowSearch(true)}
                                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                                >
                                    <Search className="w-4 h-4" />
                                    <span className="text-sm hidden sm:inline">Search</span>
                                    <kbd className="hidden sm:inline px-1.5 py-0.5 text-[10px] bg-slate-700 rounded">⌘K</kbd>
                                </motion.button>

                                {/* Global Filters */}
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setShowFilters(!showFilters)}
                                    className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors ${
                                        showFilters 
                                            ? 'bg-purple-600 border-purple-500 text-white' 
                                            : 'bg-slate-800/50 border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-700/50'
                                    }`}
                                >
                                    <Filter className="w-4 h-4" />
                                    <span className="text-sm hidden sm:inline">Filters</span>
                                </motion.button>

                                {/* Presets */}
                                <div className="relative">
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => setShowPresets(!showPresets)}
                                        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                                    >
                                        <Layout className="w-4 h-4" />
                                        <span className="text-sm hidden sm:inline">Presets</span>
                                        <ChevronDown className={`w-3 h-3 transition-transform ${showPresets ? 'rotate-180' : ''}`} />
                                    </motion.button>

                                    {/* Presets Dropdown */}
                                    <AnimatePresence>
                                        {showPresets && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                                className="absolute right-0 mt-2 w-64 rounded-xl overflow-hidden z-50"
                                                style={{
                                                    background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.98) 0%, rgba(25, 20, 40, 0.98) 100%)',
                                                    border: '1px solid rgba(139, 92, 246, 0.3)',
                                                    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
                                                }}
                                            >
                                                <div className="p-2 border-b border-purple-500/20">
                                                    <p className="text-xs text-slate-500 px-2">Layout Presets</p>
                                                </div>
                                                <div className="p-2 space-y-1 max-h-60 overflow-y-auto">
                                                    {presets.map((preset) => (
                                                        <div
                                                            key={preset.id}
                                                            className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors ${
                                                                activePreset === preset.id 
                                                                    ? 'bg-purple-500/20 text-white' 
                                                                    : 'hover:bg-slate-700/50 text-slate-300'
                                                            }`}
                                                            onClick={() => handlePresetSelect(preset)}
                                                        >
                                                            <div className="flex items-center gap-2">
                                                                {activePreset === preset.id && <Check className="w-4 h-4 text-purple-400" />}
                                                                <span className="text-sm">{preset.name}</span>
                                                            </div>
                                                            {preset.id.startsWith('custom') && (
                                                                <button
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        deletePreset(preset.id);
                                                                    }}
                                                                    className="p-1 rounded hover:bg-red-500/20 text-slate-500 hover:text-red-400"
                                                                >
                                                                    <Trash2 className="w-3 h-3" />
                                                                </button>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                                <div className="p-2 border-t border-purple-500/20">
                                                    <button
                                                        onClick={saveCurrentAsPreset}
                                                        className="w-full flex items-center justify-center gap-2 p-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-sm transition-colors"
                                                    >
                                                        <Save className="w-4 h-4" />
                                                        Save Current Layout
                                                    </button>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>

                                {/* Connection Status */}
                                <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
                                    wsData.isConnected 
                                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                                        : 'bg-red-500/10 text-red-400 border border-red-500/20'
                                }`}>
                                    <span className={`w-2 h-2 rounded-full ${
                                        wsData.isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'
                                    }`} />
                                    {wsData.isConnected ? 'Live' : 'Offline'}
                                </div>

                                {/* Symbol selector */}
                                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/50 border border-slate-700/50">
                                    <Activity className="w-4 h-4 text-purple-400" />
                                    <span className="text-sm font-semibold text-white">{selectedSymbol}</span>
                                </div>

                                {/* Fullscreen toggle */}
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setIsFullscreen(!isFullscreen)}
                                    className="p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                                >
                                    {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                                </motion.button>
                            </div>
                        </div>

                        {/* Global Filters Bar */}
                        <AnimatePresence>
                            {showFilters && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="mb-4 p-3 rounded-xl bg-slate-800/30 border border-purple-500/20"
                                >
                                    <div className="flex flex-wrap items-center gap-4">
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-slate-500">Timeframe:</span>
                                            <select
                                                value={globalFilters.timeframe}
                                                onChange={(e) => setGlobalFilters(prev => ({ ...prev, timeframe: e.target.value }))}
                                                className="px-2 py-1 text-sm rounded-lg bg-slate-700/50 border border-slate-600/50 text-white"
                                            >
                                                {['1m', '5m', '15m', '1h', '4h', '1d', '1w'].map(tf => (
                                                    <option key={tf} value={tf}>{tf}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-slate-500">Market:</span>
                                            <select
                                                value={globalFilters.marketType}
                                                onChange={(e) => setGlobalFilters(prev => ({ ...prev, marketType: e.target.value as any }))}
                                                className="px-2 py-1 text-sm rounded-lg bg-slate-700/50 border border-slate-600/50 text-white"
                                            >
                                                <option value="all">All</option>
                                                <option value="spot">Spot</option>
                                                <option value="futures">Futures</option>
                                            </select>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs text-slate-500">Min Volume:</span>
                                            <input
                                                type="number"
                                                value={globalFilters.minVolume}
                                                onChange={(e) => setGlobalFilters(prev => ({ ...prev, minVolume: parseInt(e.target.value) || 0 }))}
                                                className="w-24 px-2 py-1 text-sm rounded-lg bg-slate-700/50 border border-slate-600/50 text-white"
                                                placeholder="0"
                                            />
                                        </div>
                                        <button
                                            onClick={() => setGlobalFilters({ timeframe: '15m', exchange: 'all', marketType: 'all', minVolume: 0 })}
                                            className="px-2 py-1 text-xs text-purple-400 hover:text-purple-300"
                                        >
                                            Reset
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Tab Navigation */}
                        <nav className="flex gap-2 overflow-x-auto pb-1 hide-scrollbar" role="tablist">
                            {TABS.map((tab, index) => {
                                const Icon = tab.icon;
                                const isActive = activeTab === tab.id;
                                const isHovered = hoveredTab === tab.id;

                                return (
                                    <motion.button
                                        key={tab.id}
                                        role="tab"
                                        aria-selected={isActive}
                                        onClick={() => handleTabChange(tab.id)}
                                        onMouseEnter={() => setHoveredTab(tab.id)}
                                        onMouseLeave={() => setHoveredTab(null)}
                                        className="relative flex items-center gap-2.5 px-4 py-2.5 rounded-xl font-medium whitespace-nowrap transition-all duration-300"
                                        style={{
                                            background: isActive 
                                                ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(168, 85, 247, 0.15) 100%)'
                                                : isHovered 
                                                    ? 'rgba(139, 92, 246, 0.1)' 
                                                    : 'rgba(15, 15, 24, 0.5)',
                                            boxShadow: isActive ? `0 4px 20px ${tab.glowColor}` : undefined,
                                            border: `1px solid ${isActive ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.1)'}`,
                                        }}
                                        whileHover={{ scale: 1.02, y: -2 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        <span className={`p-1.5 rounded-lg transition-all duration-300 ${
                                            isActive ? 'bg-white/20' : 'bg-slate-800/50'
                                        }`}>
                                            <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                                        </span>

                                        <div className="text-left">
                                            <span className={`block text-sm font-semibold ${isActive ? 'text-white' : 'text-slate-300'}`}>
                                                {tab.label}
                                            </span>
                                            <span className={`block text-[10px] ${isActive ? 'text-white/70' : 'text-slate-500'}`}>
                                                {tab.description}
                                            </span>
                                        </div>

                                        <span className={`ml-auto px-1.5 py-0.5 text-[10px] font-mono rounded ${
                                            isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-500'
                                        }`}>
                                            ⌘{index + 1}
                                        </span>

                                        {isActive && (
                                            <motion.div
                                                layoutId="tradingHubActiveIndicator"
                                                className="absolute -bottom-1 left-4 right-4 h-0.5 rounded-full"
                                                style={{
                                                    background: 'linear-gradient(90deg, transparent, white, transparent)',
                                                }}
                                            />
                                        )}
                                    </motion.button>
                                );
                            })}
                        </nav>
                    </div>
                </div>
            </motion.header>

            {/* Tab Content */}
            <main className={`max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-6 ${isFullscreen ? 'h-screen overflow-auto' : ''}`}>
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.2, ease: 'easeOut' }}
                        className="min-h-[calc(100vh-200px)]"
                    >
                        <Suspense fallback={
                            <div className="flex items-center justify-center h-[60vh]">
                                <div className="text-center space-y-4">
                                    <LoadingSpinner variant="gradient" size="xl" />
                                    <div>
                                        <p className="text-lg font-medium text-slate-300">
                                            Loading {activeTabConfig?.label}
                                        </p>
                                        <p className="text-sm text-slate-500 mt-1">
                                            {activeTabConfig?.description}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        }>
                            {ActiveComponent && (
                                <ActiveComponent
                                    selectedSymbol={selectedSymbol}
                                    onSymbolChange={setSelectedSymbol}
                                    wsData={wsData}
                                    globalFilters={globalFilters}
                                />
                            )}
                        </Suspense>
                    </motion.div>
                </AnimatePresence>
            </main>

            {/* Floating Quick Actions Bar */}
            <AnimatePresence>
                {showQuickActions && !isFullscreen && (
                    <motion.div
                        initial={{ opacity: 0, y: 100 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 100 }}
                        className="fixed bottom-6 left-1/2 -translate-x-1/2 z-30"
                    >
                        <div
                            className="flex items-center gap-2 p-2 rounded-2xl"
                            style={{
                                background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.95) 0%, rgba(25, 20, 40, 0.95) 100%)',
                                backdropFilter: 'blur(20px)',
                                border: '1px solid rgba(139, 92, 246, 0.3)',
                                boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(139, 92, 246, 0.2)',
                            }}
                        >
                            {quickActions.map((action) => {
                                const Icon = action.icon;
                                const variantColors = {
                                    primary: 'from-purple-600 to-purple-500 hover:from-purple-500 hover:to-purple-400',
                                    success: 'from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400',
                                    warning: 'from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400',
                                    danger: 'from-red-600 to-red-500 hover:from-red-500 hover:to-red-400',
                                };

                                return (
                                    <motion.button
                                        key={action.id}
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.9 }}
                                        onClick={action.onClick}
                                        className={`relative flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r ${variantColors[action.variant]} text-white font-medium shadow-lg transition-all`}
                                        title={`${action.label} (${action.shortcut})`}
                                    >
                                        <Icon className="w-4 h-4" />
                                        <span className="text-sm hidden sm:inline">{action.label}</span>
                                        {action.shortcut && (
                                            <kbd className="hidden sm:inline px-1.5 py-0.5 text-[10px] bg-white/20 rounded">
                                                {action.shortcut}
                                            </kbd>
                                        )}
                                    </motion.button>
                                );
                            })}

                            {/* Toggle Quick Actions */}
                            <button
                                onClick={() => setShowQuickActions(false)}
                                className="p-2 rounded-lg text-slate-500 hover:text-white hover:bg-slate-700/50 transition-colors"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Mini FAB to show quick actions when hidden */}
            {!showQuickActions && !isFullscreen && (
                <motion.button
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setShowQuickActions(true)}
                    className="fixed bottom-6 right-6 z-30 p-4 rounded-full shadow-2xl"
                    style={{
                        background: 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
                        boxShadow: '0 8px 32px rgba(139, 92, 246, 0.5)',
                    }}
                >
                    <Zap className="w-6 h-6 text-white" />
                </motion.button>
            )}

            {/* Global Search Modal */}
            <AnimatePresence>
                {showSearch && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]"
                        onClick={() => setShowSearch(false)}
                    >
                        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
                        
                        <motion.div
                            initial={{ opacity: 0, y: -20, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -20, scale: 0.95 }}
                            onClick={(e) => e.stopPropagation()}
                            className="relative w-full max-w-2xl mx-4 rounded-2xl overflow-hidden"
                            style={{
                                background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.98) 0%, rgba(25, 20, 40, 0.98) 100%)',
                                border: '1px solid rgba(139, 92, 246, 0.3)',
                                boxShadow: '0 30px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(139, 92, 246, 0.2)',
                            }}
                        >
                            <div className="flex items-center gap-3 p-4 border-b border-purple-500/20">
                                <Search className="w-5 h-5 text-purple-400" />
                                <input
                                    type="text"
                                    placeholder="Search symbols, orders, positions..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    autoFocus
                                    className="flex-1 bg-transparent text-white text-lg placeholder-slate-500 outline-none"
                                />
                                <button
                                    onClick={() => setShowSearch(false)}
                                    className="p-1.5 rounded-lg hover:bg-slate-700/50 text-slate-400 hover:text-white transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>

                            <div className="p-4 max-h-80 overflow-y-auto">
                                <p className="text-xs text-slate-500 mb-3">Quick Actions</p>
                                <div className="grid grid-cols-2 gap-2">
                                    {quickActions.map((action) => {
                                        const Icon = action.icon;
                                        return (
                                            <button
                                                key={action.id}
                                                onClick={() => {
                                                    action.onClick();
                                                    setShowSearch(false);
                                                }}
                                                className="flex items-center gap-3 p-3 rounded-lg hover:bg-purple-500/10 text-left transition-colors"
                                            >
                                                <Icon className="w-4 h-4 text-purple-400" />
                                                <span className="text-slate-300">{action.label}</span>
                                                {action.shortcut && (
                                                    <kbd className="ml-auto px-1.5 py-0.5 text-[10px] bg-slate-700 rounded text-slate-400">
                                                        {action.shortcut}
                                                    </kbd>
                                                )}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            <div className="flex items-center justify-between p-3 border-t border-purple-500/10 text-xs text-slate-500">
                                <div className="flex items-center gap-4">
                                    <span><kbd className="px-1.5 py-0.5 bg-slate-700 rounded">↵</kbd> Select</span>
                                    <span><kbd className="px-1.5 py-0.5 bg-slate-700 rounded">Esc</kbd> Close</span>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default UnifiedTradingHubView;
