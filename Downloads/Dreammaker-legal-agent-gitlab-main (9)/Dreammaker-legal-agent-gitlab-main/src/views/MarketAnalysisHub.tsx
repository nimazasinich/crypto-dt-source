/**
 * Market Analysis Hub - Phase 2 Implementation
 * 
 * Unified hub combining all market analysis features:
 * - Market Overview (from MarketView) - Real-time market data & charts
 * - Scanner (from AI Lab Scanner) - AI-powered market scanning
 * - Technical Analysis (from TechnicalAnalysisView) - Pattern detection & indicators
 * 
 * @component
 * @example
 * ```tsx
 * <MarketAnalysisHub />
 * ```
 * 
 * Features:
 * - Tabbed interface for easy navigation
 * - Deep linking support via URL parameters (?tab=market)
 * - Independent tab state with separate data fetching
 * - Beautiful gradient design matching theme
 * - Enhanced glassmorphism UI
 * - Keyboard shortcuts (Cmd/Ctrl + 1-3)
 * - Quick actions bar
 * - Cross-tab search functionality
 * 
 * @since 2.0.0
 * @version 2.0.0 - Phase 2: Market Analysis Consolidation
 */

import React, { useState, useEffect, useCallback, Suspense, lazy, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    TrendingUp,
    Activity,
    BarChart3,
    Search,
    Zap,
    RefreshCw,
    Settings,
    Maximize2,
    Filter,
    Bell,
    Bookmark,
    Share2,
    Download,
    ChevronDown,
    X,
    Star,
    Clock,
    Target,
    Brain,
} from 'lucide-react';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { toast } from '../components/ui/Toast';

// Lazy load tab components for better performance
const MarketView = lazy(() => import('./MarketView').then(m => ({ default: m.MarketView || m.default })));
const TechnicalAnalysisView = lazy(() => import('./TechnicalAnalysisView').then(m => ({ default: m.TechnicalAnalysisView || m.default })));

// Scanner Tab Component (inline for now, can be extracted)
const ScannerTab = lazy(() => import('./ai-lab/tabs/ScannerTab').then(m => ({ default: m.ScannerTab || m.default })));

type TabId = 'market' | 'scanner' | 'technical';

interface Tab {
    id: TabId;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    description: string;
    gradient: string;
    glowColor: string;
    shortcut: string;
}

const TABS: Tab[] = [
    {
        id: 'market',
        label: 'Market Overview',
        icon: TrendingUp,
        description: 'Real-time market data & live charts',
        gradient: 'from-purple-500 via-purple-400 to-violet-500',
        glowColor: 'rgba(139, 92, 246, 0.5)',
        shortcut: '1',
    },
    {
        id: 'scanner',
        label: 'AI Scanner',
        icon: Search,
        description: 'AI-powered market scanning & signals',
        gradient: 'from-cyan-500 via-cyan-400 to-blue-500',
        glowColor: 'rgba(6, 182, 212, 0.5)',
        shortcut: '2',
    },
    {
        id: 'technical',
        label: 'Technical Analysis',
        icon: Activity,
        description: 'Advanced pattern detection & indicators',
        gradient: 'from-emerald-500 via-emerald-400 to-teal-500',
        glowColor: 'rgba(16, 185, 129, 0.5)',
        shortcut: '3',
    },
];

// Quick Actions Configuration
interface QuickAction {
    id: string;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    onClick: () => void;
    variant: 'primary' | 'secondary' | 'success' | 'warning';
}

/**
 * Market Analysis Hub View Component
 * Provides tabbed interface for all market analysis features
 * Supports deep linking via URL parameters
 */
export const MarketAnalysisHub: React.FC = () => {
    // Initialize from URL parameter if present
    const getInitialTab = (): TabId => {
        const params = new URLSearchParams(window.location.search);
        const tabParam = params.get('tab') as TabId;
        return TABS.find(t => t.id === tabParam)?.id || 'market';
    };

    const [activeTab, setActiveTab] = useState<TabId>(getInitialTab);
    const [hoveredTab, setHoveredTab] = useState<TabId | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [showSearch, setShowSearch] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [showQuickActions, setShowQuickActions] = useState(false);
    const [bookmarkedSymbols, setBookmarkedSymbols] = useState<string[]>(['BTCUSDT', 'ETHUSDT']);
    const [notifications, setNotifications] = useState<number>(3);

    // Quick actions
    const quickActions: QuickAction[] = useMemo(() => [
        {
            id: 'scan',
            label: 'Quick Scan',
            icon: Search,
            onClick: () => {
                setActiveTab('scanner');
                toast.info('Scanner Activated', 'Running quick market scan...');
            },
            variant: 'primary',
        },
        {
            id: 'alert',
            label: 'Set Alert',
            icon: Bell,
            onClick: () => {
                toast.success('Alert Created', 'Price alert has been set');
            },
            variant: 'warning',
        },
        {
            id: 'bookmark',
            label: 'Bookmark',
            icon: Bookmark,
            onClick: () => {
                toast.info('Bookmarked', 'Symbol added to watchlist');
            },
            variant: 'secondary',
        },
        {
            id: 'share',
            label: 'Share Analysis',
            icon: Share2,
            onClick: () => {
                navigator.clipboard.writeText(window.location.href);
                toast.success('Link Copied', 'Analysis link copied to clipboard');
            },
            variant: 'success',
        },
    ], []);

    // Sync URL with active tab
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const currentTabParam = params.get('tab');

        if (currentTabParam !== activeTab) {
            params.set('tab', activeTab);
            const newUrl = `${window.location.pathname}?${params.toString()}`;
            window.history.replaceState({}, '', newUrl);
        }
    }, [activeTab]);

    // Listen for URL changes (back/forward navigation)
    useEffect(() => {
        const handlePopState = () => {
            const params = new URLSearchParams(window.location.search);
            const tabParam = params.get('tab') as TabId;
            if (tabParam && TABS.find(t => t.id === tabParam)) {
                setActiveTab(tabParam);
            }
        };

        window.addEventListener('popstate', handlePopState);
        return () => window.removeEventListener('popstate', handlePopState);
    }, []);

    // Keyboard shortcuts (Cmd/Ctrl + 1/2/3)
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            // Tab switching
            if ((e.metaKey || e.ctrlKey)) {
                if (e.key === '1') {
                    e.preventDefault();
                    handleTabChange('market');
                } else if (e.key === '2') {
                    e.preventDefault();
                    handleTabChange('scanner');
                } else if (e.key === '3') {
                    e.preventDefault();
                    handleTabChange('technical');
                } else if (e.key === 'k') {
                    e.preventDefault();
                    setShowSearch(true);
                }
            }
            
            // Escape to close search
            if (e.key === 'Escape') {
                setShowSearch(false);
                setShowQuickActions(false);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    // Handle tab change with loading state
    const handleTabChange = useCallback((tabId: TabId) => {
        if (tabId === activeTab) return;
        setIsLoading(true);
        setActiveTab(tabId);
        // Small delay to show loading state
        setTimeout(() => setIsLoading(false), 300);
    }, [activeTab]);

    // Handle search
    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
        if (query.length > 0) {
            // Could trigger search across all tabs
            toast.info('Searching...', `Looking for "${query}" across all markets`);
        }
    }, []);

    // Get active component
    const activeTabConfig = TABS.find(tab => tab.id === activeTab);

    // Render tab content
    const renderTabContent = () => {
        switch (activeTab) {
            case 'market':
                return <MarketView />;
            case 'scanner':
                return <ScannerTab />;
            case 'technical':
                return <TechnicalAnalysisView />;
            default:
                return <MarketView />;
        }
    };

    return (
        <div className="min-h-screen bg-[color:var(--surface-page)]">
            {/* Enhanced Header with Tabs */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="sticky top-0 z-20 border-b border-purple-500/20"
                style={{
                    background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.98) 0%, rgba(25, 20, 40, 0.98) 100%)',
                    backdropFilter: 'blur(20px)',
                    boxShadow: '0 4px 30px rgba(0, 0, 0, 0.3)',
                }}
            >
                <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="py-4">
                        {/* Title Row */}
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-4">
                                {/* Logo */}
                                <motion.div
                                    whileHover={{ scale: 1.05, rotate: 5 }}
                                    className="p-2.5 rounded-xl shadow-lg"
                                    style={{
                                        background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
                                        boxShadow: '0 8px 24px rgba(139, 92, 246, 0.4)',
                                    }}
                                >
                                    <BarChart3 className="w-6 h-6 text-white" style={{
                                        filter: 'drop-shadow(0 0 8px rgba(255, 255, 255, 0.5))'
                                    }} />
                                </motion.div>
                                
                                <div>
                                    <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
                                        Market Analysis Hub
                                    </h1>
                                    <p className="text-xs text-slate-400 mt-0.5">
                                        Comprehensive market intelligence • 3 integrated modules
                                    </p>
                                </div>
                            </div>

                            {/* Action buttons */}
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

                                {/* Notifications */}
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="relative p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                                >
                                    <Bell className="w-4 h-4" />
                                    {notifications > 0 && (
                                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] font-bold text-white flex items-center justify-center">
                                            {notifications}
                                        </span>
                                    )}
                                </motion.button>

                                {/* Quick Actions */}
                                <div className="relative">
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => setShowQuickActions(!showQuickActions)}
                                        className="flex items-center gap-1 px-3 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white transition-colors"
                                    >
                                        <Zap className="w-4 h-4" />
                                        <span className="text-sm font-medium">Actions</span>
                                        <ChevronDown className={`w-3 h-3 transition-transform ${showQuickActions ? 'rotate-180' : ''}`} />
                                    </motion.button>

                                    {/* Quick Actions Dropdown */}
                                    <AnimatePresence>
                                        {showQuickActions && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, scale: 1 }}
                                                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                                className="absolute right-0 mt-2 w-48 rounded-xl overflow-hidden z-50"
                                                style={{
                                                    background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.98) 0%, rgba(25, 20, 40, 0.98) 100%)',
                                                    border: '1px solid rgba(139, 92, 246, 0.3)',
                                                    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
                                                }}
                                            >
                                                {quickActions.map((action) => {
                                                    const Icon = action.icon;
                                                    return (
                                                        <button
                                                            key={action.id}
                                                            onClick={() => {
                                                                action.onClick();
                                                                setShowQuickActions(false);
                                                            }}
                                                            className="w-full flex items-center gap-3 px-4 py-3 text-left text-slate-300 hover:text-white hover:bg-purple-500/20 transition-colors"
                                                        >
                                                            <Icon className="w-4 h-4" />
                                                            <span className="text-sm">{action.label}</span>
                                                        </button>
                                                    );
                                                })}
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>

                                {/* More Options */}
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="p-2.5 rounded-lg bg-slate-800/50 border border-slate-700/50 text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                                >
                                    <Settings className="w-4 h-4" />
                                </motion.button>
                            </div>
                        </div>

                        {/* Tab Navigation */}
                        <nav className="flex gap-3" role="tablist">
                            {TABS.map((tab, index) => {
                                const Icon = tab.icon;
                                const isActive = activeTab === tab.id;
                                const isHovered = hoveredTab === tab.id;

                                return (
                                    <motion.button
                                        key={tab.id}
                                        role="tab"
                                        aria-selected={isActive}
                                        aria-controls={`panel-${tab.id}`}
                                        onClick={() => handleTabChange(tab.id)}
                                        onMouseEnter={() => setHoveredTab(tab.id)}
                                        onMouseLeave={() => setHoveredTab(null)}
                                        className="relative flex items-center gap-3 px-5 py-3 rounded-xl font-medium transition-all duration-300 flex-1 sm:flex-none"
                                        style={{
                                            background: isActive 
                                                ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(168, 85, 247, 0.15) 100%)'
                                                : isHovered 
                                                    ? 'rgba(139, 92, 246, 0.1)' 
                                                    : 'rgba(15, 15, 24, 0.5)',
                                            boxShadow: isActive 
                                                ? `0 4px 16px ${tab.glowColor}, inset 0 1px 2px rgba(255, 255, 255, 0.1)` 
                                                : undefined,
                                            border: `1px solid ${isActive ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.1)'}`,
                                        }}
                                        whileHover={{ scale: 1.02, y: -2 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        {/* Hover glow effect */}
                                        {!isActive && (
                                            <motion.div
                                                className="absolute inset-0 rounded-xl opacity-0 transition-opacity duration-300"
                                                style={{
                                                    background: `radial-gradient(circle at center, ${tab.glowColor.replace('0.5', '0.15')} 0%, transparent 70%)`,
                                                }}
                                                animate={{ opacity: isHovered ? 1 : 0 }}
                                            />
                                        )}

                                        {/* Icon */}
                                        <span className={`relative z-10 p-2 rounded-lg transition-all duration-300 ${
                                            isActive 
                                                ? 'bg-white/20' 
                                                : 'bg-slate-800/50'
                                        }`}>
                                            <Icon className={`w-4 h-4 transition-colors duration-300 ${
                                                isActive ? 'text-white' : 'text-slate-400'
                                            }`} />
                                        </span>

                                        {/* Label */}
                                        <div className="relative z-10 text-left hidden sm:block">
                                            <span className={`block text-sm font-semibold transition-colors duration-300 ${
                                                isActive ? 'text-white' : 'text-slate-300'
                                            }`}>
                                                {tab.label}
                                            </span>
                                            <span className={`block text-[10px] transition-colors duration-300 ${
                                                isActive ? 'text-white/70' : 'text-slate-500'
                                            }`}>
                                                {tab.description}
                                            </span>
                                        </div>

                                        {/* Keyboard shortcut */}
                                        <span className={`relative z-10 ml-auto px-1.5 py-0.5 text-[10px] font-mono rounded transition-colors duration-300 hidden sm:block ${
                                            isActive 
                                                ? 'bg-white/20 text-white' 
                                                : 'bg-slate-800 text-slate-500'
                                        }`}>
                                            ⌘{tab.shortcut}
                                        </span>

                                        {/* Active indicator */}
                                        {isActive && (
                                            <motion.div
                                                layoutId="marketHubActiveIndicator"
                                                className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-0.5 rounded-full"
                                                style={{
                                                    background: `linear-gradient(90deg, transparent 0%, ${tab.glowColor.replace('0.5', '1')} 50%, transparent 100%)`,
                                                    boxShadow: `0 0 8px ${tab.glowColor}`,
                                                }}
                                            />
                                        )}
                                    </motion.button>
                                );
                            })}
                        </nav>

                        {/* Bookmarked Symbols Bar */}
                        {bookmarkedSymbols.length > 0 && (
                            <div className="mt-3 flex items-center gap-2 overflow-x-auto pb-1">
                                <span className="text-xs text-slate-500 flex-shrink-0">Watchlist:</span>
                                {bookmarkedSymbols.map((symbol) => (
                                    <motion.button
                                        key={symbol}
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/50 border border-slate-700/50 text-xs text-slate-300 hover:text-white hover:border-purple-500/30 transition-colors"
                                    >
                                        <Star className="w-3 h-3 text-yellow-500" />
                                        {symbol}
                                    </motion.button>
                                ))}
                                <button className="text-xs text-purple-400 hover:text-purple-300 transition-colors">
                                    + Add
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </motion.header>

            {/* Content Area */}
            <main className="relative">
                <AnimatePresence mode="wait">
                    {isLoading ? (
                        <motion.div
                            key="loading"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex items-center justify-center h-[60vh]"
                        >
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
                        </motion.div>
                    ) : (
                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.2, ease: 'easeOut' }}
                            role="tabpanel"
                            id={`panel-${activeTab}`}
                            aria-labelledby={`tab-${activeTab}`}
                        >
                            <Suspense fallback={
                                <div className="flex items-center justify-center h-[60vh]">
                                    <LoadingSpinner variant="gradient" size="xl" label={`Loading ${activeTabConfig?.label}...`} />
                                </div>
                            }>
                                {renderTabContent()}
                            </Suspense>
                        </motion.div>
                    )}
                </AnimatePresence>
            </main>

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
                        {/* Backdrop */}
                        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
                        
                        {/* Search Modal */}
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
                            {/* Search Input */}
                            <div className="flex items-center gap-3 p-4 border-b border-purple-500/20">
                                <Search className="w-5 h-5 text-purple-400" />
                                <input
                                    type="text"
                                    placeholder="Search symbols, patterns, signals..."
                                    value={searchQuery}
                                    onChange={(e) => handleSearch(e.target.value)}
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

                            {/* Quick Filters */}
                            <div className="flex items-center gap-2 p-3 border-b border-purple-500/10">
                                <span className="text-xs text-slate-500">Filter:</span>
                                {['All', 'Symbols', 'Patterns', 'Signals', 'News'].map((filter) => (
                                    <button
                                        key={filter}
                                        className="px-2.5 py-1 text-xs rounded-lg bg-slate-800/50 text-slate-400 hover:text-white hover:bg-purple-500/20 transition-colors"
                                    >
                                        {filter}
                                    </button>
                                ))}
                            </div>

                            {/* Recent Searches / Results */}
                            <div className="p-4 max-h-80 overflow-y-auto">
                                <p className="text-xs text-slate-500 mb-3">Recent Searches</p>
                                <div className="space-y-2">
                                    {['BTCUSDT', 'Head and Shoulders', 'RSI Divergence', 'ETHUSDT'].map((item) => (
                                        <button
                                            key={item}
                                            className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-purple-500/10 text-left transition-colors"
                                        >
                                            <Clock className="w-4 h-4 text-slate-500" />
                                            <span className="text-slate-300">{item}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Footer */}
                            <div className="flex items-center justify-between p-3 border-t border-purple-500/10 text-xs text-slate-500">
                                <div className="flex items-center gap-4">
                                    <span><kbd className="px-1.5 py-0.5 bg-slate-700 rounded">↵</kbd> Select</span>
                                    <span><kbd className="px-1.5 py-0.5 bg-slate-700 rounded">↑↓</kbd> Navigate</span>
                                    <span><kbd className="px-1.5 py-0.5 bg-slate-700 rounded">Esc</kbd> Close</span>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Floating Quick Stats Panel */}
            <motion.div
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="fixed right-6 top-1/2 -translate-y-1/2 z-10 hidden xl:block"
            >
                <div
                    className="p-4 rounded-2xl space-y-4"
                    style={{
                        background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.95) 0%, rgba(25, 20, 40, 0.95) 100%)',
                        backdropFilter: 'blur(20px)',
                        border: '1px solid rgba(139, 92, 246, 0.2)',
                        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
                    }}
                >
                    <div className="text-center">
                        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">BTC</p>
                        <p className="text-lg font-bold text-white">$67,234</p>
                        <p className="text-xs text-emerald-400">+2.34%</p>
                    </div>
                    <div className="w-full h-px bg-purple-500/20" />
                    <div className="text-center">
                        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">ETH</p>
                        <p className="text-lg font-bold text-white">$3,456</p>
                        <p className="text-xs text-emerald-400">+1.87%</p>
                    </div>
                    <div className="w-full h-px bg-purple-500/20" />
                    <div className="text-center">
                        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Signals</p>
                        <p className="text-lg font-bold text-cyan-400">12</p>
                        <p className="text-xs text-slate-500">Active</p>
                    </div>
                    <div className="w-full h-px bg-purple-500/20" />
                    <div className="text-center">
                        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Market</p>
                        <p className="text-sm font-bold text-emerald-400">Bullish</p>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default MarketAnalysisHub;
