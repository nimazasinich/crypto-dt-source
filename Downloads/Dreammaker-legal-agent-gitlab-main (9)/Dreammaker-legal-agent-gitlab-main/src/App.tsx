import React, { useState, useEffect } from 'react';
import { Logger } from './core/Logger.js';
import { NavigationProvider, useNavigation } from './components/Navigation/NavigationProvider';
import { ThemeProvider } from './components/Theme/ThemeProvider';
import { AccessibilityProvider } from './components/Accessibility/AccessibilityProvider';
import { RefreshSettingsProvider } from './contexts/RefreshSettingsContext';
import { LiveDataProvider } from './components/LiveDataContext';
import { DataProvider } from './contexts/DataContext';
import { TradingProvider } from './contexts/TradingContext';
import { ModeProvider } from './contexts/ModeContext';
import { BacktestProvider } from './contexts/BacktestContext';
import { SignalProvider } from './contexts/SignalContext';
import { EnhancedSidebar } from './components/Navigation/EnhancedSidebar';
import { lazyLoad } from './components/lazyLoad';
import LoadingSpinner from './components/ui/LoadingSpinner';
import LoadingScreen from './components/ui/LoadingScreen';
import ErrorBoundary from './components/ui/ErrorBoundary';
import { getViewTheme } from './config/viewThemes';
import { ToastContainer } from './components/ui/Toast';

const DashboardView = lazyLoad(() => import('./views/EnhancedDashboardView'), 'EnhancedDashboardView');
// REMOVED: TradingViewDashboard - Deleted in Phase 4 cleanup (replaced by Trading Hub > Charts tab)
// REMOVED: ChartingView - Merged into MarketView (Charting tab)
// Archived to: archive/merged-files-20251204/ChartingView.tsx
// PHASE 2: Market Analysis Hub - Consolidated market views
const MarketAnalysisHub = lazyLoad(() => import('./views/MarketAnalysisHub'), 'MarketAnalysisHub');
const MarketView = lazyLoad(() => import('./views/MarketView'), 'MarketView');
// REMOVED: ScannerView - Deleted in Phase 4 cleanup (replaced by AI Lab > Scanner tab)
// REMOVED: TrainingView - Deleted in Phase 4 cleanup (replaced by AI Lab > Training tab)
// REMOVED: RiskView - Merged into ProfessionalRiskView (Portfolio tab)
// Archived to: archive/merged-files-20251204/RiskView.tsx
const ProfessionalRiskView = lazyLoad(() => import('./views/ProfessionalRiskView')
    .then(m => ({ default: m.ProfessionalRiskView }))
    .catch(err => {
        console.warn("ProfessionalRiskView load error:", err);
        return { default: () => <div className="p-4 text-red-500">Error loading Professional Risk View</div> };
    }), 'ProfessionalRiskView');
// REMOVED: BacktestView - Merged into EnhancedStrategyLabView (Backtest tab)
// Archived to: archive/merged-files-20251204/BacktestView.tsx
// REMOVED: HealthView - Deleted in Phase 4 cleanup (replaced by Admin Hub > Health tab)
const SettingsView = lazyLoad(() => import('./views/SettingsView'), 'SettingsView');
// REMOVED: FuturesTradingView - Deleted in Phase 4 cleanup (replaced by Trading Hub > Futures tab)
// REMOVED: TradingView - Dead code (imported but never routed, superseded by UnifiedTradingView)
// Archived to: archive/dead-code-20251204/TradingView.tsx
// REMOVED: UnifiedTradingView - Simple wrapper, now redirects directly to Futures
// Archived to: archive/dead-code-20251204/UnifiedTradingView.tsx
// REMOVED: EnhancedTradingView - Deleted in Phase 4 cleanup (replaced by Trading Hub > Spot tab)
// REMOVED: PositionsView - Deleted in Phase 4 cleanup (replaced by Trading Hub > Positions tab)
// REMOVED: PortfolioPage - Deleted in Phase 4 cleanup (replaced by Trading Hub > Portfolio tab)
// REMOVED: StrategyLabView/EnhancedStrategyLabView - Deleted in Phase 4 cleanup (replaced by AI Lab > Backtest tab)
// REMOVED: StrategyBuilderView - Merged into EnhancedStrategyLabView (Builder tab)
// Archived to: archive/merged-files-20251204/StrategyBuilderView.tsx
// REMOVED: StrategyInsightsView - Merged into EnhancedStrategyLabView (Insights tab)
// Archived to: archive/merged-files-20251204/StrategyInsightsView.tsx
// REMOVED: ExchangeSettingsView - Merged into SettingsView (simplified for Phase 5)
// Archived to: archive/merged-files-20251204/ExchangeSettingsView.tsx
// REMOVED: MonitoringView - Deleted in Phase 4 cleanup (replaced by Admin Hub > Monitoring tab)
// REMOVED: DiagnosticsView - Merged into HealthView (Diagnostics tab)
// Archived to: archive/merged-files-20251204/DiagnosticsView.tsx
const TechnicalAnalysisView = lazyLoad(() => import('./views/TechnicalAnalysisView'), 'TechnicalAnalysisView');
const RiskManagementView = lazyLoad(() => import('./views/RiskManagementView'), 'RiskManagementView');
// REMOVED: TradingHubView - OLD hub, Deleted in Phase 4 cleanup (replaced by UnifiedTradingHubView)
// PHASE 1: Unified Trading Hub
const UnifiedTradingHubView = lazyLoad(() => import('./views/trading-hub/UnifiedTradingHubView')
    .then(m => ({ default: m.UnifiedTradingHubView || m.default }))
    .catch(err => {
        console.warn("UnifiedTradingHubView load error:", err);
        return { default: () => <div className="p-4 text-red-500">Error loading Unified Trading Hub</div> };
    }), 'UnifiedTradingHubView');
// PHASE 2: Unified AI Lab
const UnifiedAILabView = lazyLoad(() => import('./views/ai-lab/UnifiedAILabView')
    .then(m => ({ default: m.UnifiedAILabView || m.default }))
    .catch(err => {
        console.warn("UnifiedAILabView load error:", err);
        return { default: () => <div className="p-4 text-red-500">Error loading Unified AI Lab</div> };
    }), 'UnifiedAILabView');
// PHASE 3: Unified Admin Hub
const UnifiedAdminView = lazyLoad(() => import('./views/admin/UnifiedAdminView')
    .then(m => ({ default: m.UnifiedAdminView || m.default }))
    .catch(err => {
        console.warn("UnifiedAdminView load error:", err);
        return { default: () => <div className="p-4 text-red-500">Error loading Unified Admin Hub</div> };
    }), 'UnifiedAdminView');

// Navigate component for handling redirects with query params
const Navigate: React.FC<{ to: string }> = ({ to }) => {
    const { setCurrentView } = useNavigation();

    useEffect(() => {
        // Parse the target route
        const [path, query] = to.split('?');
        const viewName = path.replace('/', '');

        // Update the URL if there are query params
        if (query) {
            const url = new URL(window.location.href);
            const params = new URLSearchParams(query);
            params.forEach((value, key) => {
                url.searchParams.set(key, value);
            });
            window.history.replaceState({}, '', url.toString());
        }

        // Navigate to the new view
        setCurrentView(viewName as any);
    }, [to, setCurrentView]);

    return <LoadingSpinner />;
};

const AppContent: React.FC = () => {
    const { currentView } = useNavigation();
    const viewTheme = getViewTheme(currentView);

    // Prefetch critical views for better user experience
    React.useEffect(() => {
        // Note: Prefetching disabled for merged views - using lazy loading only
    }, []);

    const renderCurrentView = () => {
        const ViewComponent = (() => {
            switch (currentView) {
                case 'dashboard': return <DashboardView />;
                // PHASE 2: Market Analysis Hub (consolidated)
                case 'market-analysis': return <MarketAnalysisHub />;
                // PHASE 2: Legacy redirects for market views
                case 'market': return <Navigate to="market-analysis?tab=market" />;
                // MERGED: charting → market-analysis?tab=market (charting is within MarketView)
                case 'charting': return <Navigate to="market-analysis?tab=market" />;
                // PHASE 2: Unified AI Lab - New consolidated view
                case 'ai-lab': return <UnifiedAILabView />;
                // PHASE 2: Backward compatibility redirects to unified AI lab
                case 'scanner': return <Navigate to="ai-lab?tab=scanner" />;
                case 'training': return <Navigate to="ai-lab?tab=training" />;
                case 'strategylab': return <Navigate to="ai-lab?tab=backtest" />;
                case 'backtest': return <Navigate to="ai-lab?tab=backtest" />;
                case 'strategyBuilder': return <Navigate to="ai-lab?tab=builder" />;
                case 'strategy-insights': return <Navigate to="ai-lab?tab=insights" />;
                // Risk Management
                case 'risk': return <Navigate to="professional-risk?tab=portfolio" />;
                case 'professional-risk': return <ProfessionalRiskView />;
                // PHASE 3: Unified Admin Hub - New consolidated view
                case 'admin': return <UnifiedAdminView />;
                // PHASE 3: Backward compatibility redirects to unified admin hub
                case 'health': return <Navigate to="admin?tab=health" />;
                case 'monitoring': return <Navigate to="admin?tab=monitoring" />;
                case 'diagnostics': return <Navigate to="admin?tab=diagnostics" />;
                // MERGED: exchange-settings → settings (simplified)
                case 'exchange-settings': return <Navigate to="settings" />;
                case 'settings': return <SettingsView />;
                // PHASE 1: Unified Trading Hub - New consolidated view
                case 'trading': return <UnifiedTradingHubView />;
                // PHASE 1: Backward compatibility redirects to unified trading hub
                case 'tradingview-dashboard': return <Navigate to="trading?tab=charts" />;
                case 'enhanced-trading': return <Navigate to="trading?tab=spot" />;
                case 'futures': return <Navigate to="trading?tab=futures" />;
                case 'positions': return <Navigate to="trading?tab=positions" />;
                case 'portfolio': return <Navigate to="trading?tab=portfolio" />;
                // PHASE 1: Legacy trading-hub redirects to new unified hub
                case 'trading-hub': return <Navigate to="trading?tab=futures" />;
                // PHASE 2: Technical Analysis redirects to Market Analysis Hub
                case 'technical-analysis': return <Navigate to="market-analysis?tab=technical" />;
                case 'risk-management': return <RiskManagementView />;
                default: return <DashboardView />;
            }
        })();

        return (
            <ErrorBoundary>
                {ViewComponent}
            </ErrorBoundary>
        );
    };

    return (
        <div
            className="flex min-h-screen flex-col transition-colors duration-700 lg:flex-row-reverse"
            style={{
                background: viewTheme.backgroundGradient,
            }}
        >
            <EnhancedSidebar />
            <main className="flex-1 overflow-auto" role="main">
                {renderCurrentView()}
            </main>
        </div>
    );
};

function App() {
    const [isAppReady, setIsAppReady] = useState(false);

    React.useEffect(() => {
        // Optimized app initialization with faster loading
        const initializeApp = async () => {
            try {
                // Reduced initialization time for faster perceived performance
                // Providers will continue to initialize in the background
                await new Promise(resolve => setTimeout(resolve, 800));

                // Mark app as ready - components will handle their own lazy loading
                setIsAppReady(true);
            } catch (error) {
                Logger.getInstance().error('Error during app initialization:', {}, error);
                // Still show the app even if initialization has issues
                setIsAppReady(true);
            }
        };

        initializeApp();
    }, []);

    // Show loading screen during initialization
    if (!isAppReady) {
        return (
            <ModeProvider>
                <ThemeProvider>
                    {/* Use consistent loading screen */}
                    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
                        <LoadingScreen message="Initializing trading platform" showProgress />
                    </div>
                </ThemeProvider>
            </ModeProvider>
        );
    }

    return (
        <ModeProvider>
            <ThemeProvider>
                <AccessibilityProvider>
                    <RefreshSettingsProvider>
                        <DataProvider>
                            {/* FIXED: Removed RealDataProvider to prevent duplicate data fetching */}
                            <LiveDataProvider>
                                <TradingProvider>
                                    <BacktestProvider>
                                        <SignalProvider autoStart={false}>
                                            <NavigationProvider>
                                                <AppContent />
                                                <ToastContainer />
                                            </NavigationProvider>
                                        </SignalProvider>
                                    </BacktestProvider>
                                </TradingProvider>
                            </LiveDataProvider>
                        </DataProvider>
                    </RefreshSettingsProvider>
                </AccessibilityProvider>
            </ThemeProvider>
        </ModeProvider>
    );
}

export default App;