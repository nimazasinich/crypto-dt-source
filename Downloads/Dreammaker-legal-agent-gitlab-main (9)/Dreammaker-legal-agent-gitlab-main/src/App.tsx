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
import { EnhancedSidebar } from './components/Navigation/EnhancedSidebar';
import { lazyLoad } from './components/lazyLoad';
import LoadingSpinner from './components/ui/LoadingSpinner';
import LoadingScreen from './components/ui/LoadingScreen';
import ErrorBoundary from './components/ui/ErrorBoundary';
import { getViewTheme } from './config/viewThemes';
import StatusRibbon from './components/ui/StatusRibbon';
import { ToastContainer } from './components/ui/Toast';

const DashboardView = lazyLoad(() => import('./views/EnhancedDashboardView'), 'EnhancedDashboardView');
const TradingViewDashboardView = lazyLoad(() => import('./views/TradingViewDashboard'), 'TradingViewDashboard');
const ChartingView = lazyLoad(() => import('./views/ChartingView'), 'ChartingView');
const MarketView = lazyLoad(() => import('./views/MarketView'), 'MarketView');
const ScannerView = lazyLoad(() => import('./views/ScannerView'), 'ScannerView');
const TrainingView = lazyLoad(() => import('./views/TrainingView'), 'TrainingView');
const RiskView = lazyLoad(() => import('./views/RiskView'), 'RiskView');
const ProfessionalRiskView = lazyLoad(() => import('./views/ProfessionalRiskView')
  .then(m => ({ default: m.ProfessionalRiskView }))
  .catch(err => {
    console.warn("ProfessionalRiskView load error:", err);
    return { default: () => <div className="p-4 text-red-500">Error loading Professional Risk View</div> };
  }), 'ProfessionalRiskView');
// REMOVED: BacktestView - Merged into EnhancedStrategyLabView (Backtest tab)
// Archived to: archive/merged-files-20251204/BacktestView.tsx
const HealthView = lazyLoad(() => import('./views/HealthView'), 'HealthView');
const SettingsView = lazyLoad(() => import('./views/SettingsView'), 'SettingsView');
const FuturesTradingView = lazyLoad(() => import('./views/FuturesTradingView')
  .then(m => ({ default: m.FuturesTradingView }))
  .catch(err => {
    console.warn("FuturesTradingView load error:", err);
    return { default: () => <div className="p-4 text-red-500">Error loading Futures Trading View</div> };
  }), 'FuturesTradingView');
// REMOVED: TradingView - Dead code (imported but never routed, superseded by UnifiedTradingView)
// Archived to: archive/dead-code-20251204/TradingView.tsx
const UnifiedTradingView = lazyLoad(() => import('./views/UnifiedTradingView'), 'UnifiedTradingView');
const EnhancedTradingView = lazyLoad(() => import('./views/EnhancedTradingView'), 'EnhancedTradingView');
const PositionsView = lazyLoad(() => import('./views/PositionsView')
  .then(m => ({ default: m.PositionsView }))
  .catch(err => {
    console.warn("PositionsView load error:", err);
    return { default: () => <div className="p-4 text-red-500">Error loading Positions View</div> };
  }), 'PositionsView');
const PortfolioPage = lazyLoad(() => import('./views/PortfolioPage')
  .then(m => ({ default: m.PortfolioPage }))
  .catch(err => {
    console.warn("PortfolioPage load error:", err);
    return { default: () => <div className="p-4 text-red-500">Error loading Portfolio Page</div> };
  }), 'PortfolioPage');
const StrategyLabView = lazyLoad(() => import('./views/EnhancedStrategyLabView')
  .then(m => ({ default: m.EnhancedStrategyLabView }))
  .catch(err => {
    console.warn("StrategyLabView load error:", err);
    return { default: () => <div className="p-4 text-red-500">Error loading Strategy Lab View</div> };
  }), 'EnhancedStrategyLabView');
// REMOVED: StrategyBuilderView - Merged into EnhancedStrategyLabView (Builder tab)
// Archived to: archive/merged-files-20251204/StrategyBuilderView.tsx
// REMOVED: StrategyInsightsView - Merged into EnhancedStrategyLabView (Insights tab)
// Archived to: archive/merged-files-20251204/StrategyInsightsView.tsx
const ExchangeSettingsView = lazyLoad(() => import('./views/ExchangeSettingsView'), 'ExchangeSettingsView');
const MonitoringView = lazyLoad(() => import('./views/MonitoringView'), 'MonitoringView');
const DiagnosticsView = lazyLoad(() => import('./views/DiagnosticsView'), 'DiagnosticsView');
const TechnicalAnalysisView = lazyLoad(() => import('./views/TechnicalAnalysisView'), 'TechnicalAnalysisView');
const RiskManagementView = lazyLoad(() => import('./views/RiskManagementView'), 'RiskManagementView');
const TradingHubView = lazyLoad(() => import('./views/TradingHubView'), 'TradingHubView');

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
  const logger = Logger.getInstance();

  // Prefetch critical views for better user experience
  React.useEffect(() => {
    // Prefetch charting view which is commonly used
    // Note: DashboardView removed (archived) - using EnhancedDashboardView instead
    import('./views/ChartingView').catch((err) => {
      logger.error('Failed to prefetch ChartingView:', {}, err);
    });
    // Skip MarketView prefetch to avoid potential import issues - let lazy load handle it
  }, []);

  const renderCurrentView = () => {
    const ViewComponent = (() => {
      switch (currentView) {
        case 'dashboard': return <DashboardView />;
        case 'tradingview-dashboard': return <TradingViewDashboardView />;
        case 'charting': return <ChartingView />;
        case 'market': return <MarketView />;
        case 'scanner': return <ScannerView />;
        case 'training': return <TrainingView />;
        case 'risk': return <RiskView />;
        case 'professional-risk': return <ProfessionalRiskView />;
        case 'backtest': return <Navigate to="strategylab?tab=backtest" />;
        case 'strategyBuilder': return <Navigate to="strategylab?tab=builder" />;
        case 'health': return <HealthView />;
        case 'settings': return <SettingsView />;
        case 'futures': return <FuturesTradingView />;
        case 'trading': return <UnifiedTradingView />;
        case 'trading-hub': return <TradingHubView />;
        case 'portfolio': return <PortfolioPage />;
        case 'technical-analysis': return <TechnicalAnalysisView />;
        case 'risk-management': return <RiskManagementView />;
        case 'enhanced-trading': return <EnhancedTradingView />;
        case 'positions': return <PositionsView />;
        case 'strategylab': return <StrategyLabView />;
        case 'strategy-insights': return <Navigate to="strategylab?tab=insights" />;
        case 'exchange-settings': return <ExchangeSettingsView />;
        case 'monitoring': return <MonitoringView />;
        case 'diagnostics': return <DiagnosticsView />;
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
        className="flex min-h-screen flex-col transition-colors duration-700 lg:flex-row"
        style={{
          background: viewTheme.backgroundGradient,
        }}
      >
        <main className="order-2 flex-1 overflow-auto lg:order-1" role="main">
          <div className="sticky top-0 z-30 border-b backdrop-blur-xl"
            style={{
              background: 'rgba(255, 255, 255, 0.8)',
              borderColor: 'rgba(139, 92, 246, 0.1)',
            }}
          >
            <StatusRibbon />
          </div>
          <div>
            {renderCurrentView()}
          </div>
        </main>
        <EnhancedSidebar />
      </div>
  );
};

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAppReady, setIsAppReady] = useState(false);

  React.useEffect(() => {
    // Simulate app initialization
    const initializeApp = async () => {
      try {
        // Give enough time for providers to initialize
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Mark app as ready
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
          <LoadingScreen message="Initializing trading platform" showProgress />
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
                    <NavigationProvider>
                      <AppContent />
                      <ToastContainer />
                    </NavigationProvider>
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