import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Brain,
  ChevronLeft,
  ChevronRight,
  DollarSign,
  Home,
  Layers,
  Search,
  Settings,
  Shield,
  Sliders,
  Sparkles,
  TrendingUp,
  Wallet,
  Zap,
  Rocket,
  ListOrdered,
  Monitor,
  Stethoscope,
  Moon,
  Sun,
} from 'lucide-react';
import { useNavigation, NavigationView } from './NavigationProvider';
import { useTheme } from '../Theme/ThemeProvider';
import { t } from '../../i18n';

interface NavigationItem {
  id: NavigationView;
  label: string;
  icon: React.ComponentType<{ className?: string; size?: number }>;
  badge?: string;
  category?: string;
}

// Organize navigation items by category for better UX
const NAV_ITEMS: NavigationItem[] = [
  // Overview
  { id: 'dashboard', label: t('navigation.dashboard'), icon: Home, category: 'Overview' },
  { id: 'tradingview-dashboard', label: 'TradingView Pro', icon: BarChart3, badge: 'New', category: 'Overview' },
  { id: 'monitoring', label: 'Monitoring', icon: Monitor, category: 'Overview' },
  
  // Market Analysis
  { id: 'market', label: t('navigation.market'), icon: Zap, category: 'Market Analysis' },
  { id: 'charting', label: t('navigation.charting'), icon: TrendingUp, category: 'Market Analysis' },
  { id: 'scanner', label: t('navigation.scanner'), icon: Search, category: 'Market Analysis' },
  { id: 'technical-analysis', label: 'Technical Analysis', icon: Activity, category: 'Market Analysis' },
  
  // Trading
  { id: 'trading-hub', label: 'Trading Hub', icon: Layers, badge: 'New', category: 'Trading' },
  { id: 'trading', label: t('navigation.trading'), icon: Sparkles, category: 'Trading' },
  { id: 'enhanced-trading', label: 'Enhanced Trading', icon: Rocket, category: 'Trading' },
  { id: 'futures', label: t('navigation.futures'), icon: DollarSign, category: 'Trading' },
  { id: 'positions', label: 'Positions', icon: ListOrdered, category: 'Trading' },
  
  // Portfolio & Risk
  { id: 'portfolio', label: 'Portfolio', icon: Wallet, category: 'Portfolio & Risk' },
  { id: 'risk-management', label: 'Risk Management', icon: Shield, category: 'Portfolio & Risk' },
  { id: 'risk', label: t('navigation.risk'), icon: Shield, category: 'Portfolio & Risk' },
  { id: 'professional-risk', label: 'Pro Risk', icon: AlertTriangle, badge: 'Pro', category: 'Portfolio & Risk' },
  
  // Strategy & AI
  { id: 'strategylab', label: 'Strategy Lab', icon: Activity, category: 'Strategy & AI', badge: '4 Tabs' },
  // REMOVED: strategyBuilder - Merged into Strategy Lab (Builder tab)
  // REMOVED: strategy-insights - Merged into Strategy Lab (Insights tab)
  // REMOVED: backtest - Merged into Strategy Lab (Backtest tab)
  { id: 'training', label: t('navigation.training'), icon: Brain, category: 'Strategy & AI' },
  
  // System
  { id: 'health', label: t('navigation.health'), icon: Activity, category: 'System' },
  { id: 'diagnostics', label: 'Diagnostics', icon: Stethoscope, category: 'System' },
  { id: 'settings', label: t('navigation.settings'), icon: Settings, category: 'System' },
  { id: 'exchange-settings', label: 'Exchange Settings', icon: Settings, category: 'System' },
];

// Group items by category
const groupedNavItems = NAV_ITEMS.reduce((acc, item) => {
  const category = item.category || 'Other';
  if (!acc[category]) acc[category] = [];
  acc[category].push(item);
  return acc;
}, {} as Record<string, NavigationItem[]>);

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  show: boolean;
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, show }) => {
  if (!show) return <>{children}</>;
  
  return (
    <div className="group/tooltip relative inline-flex">
      {children}
      <div 
        className="pointer-events-none absolute left-full top-1/2 z-50 ml-3 -translate-y-1/2 rounded-lg px-3 py-2 text-sm font-medium text-white opacity-0 shadow-xl transition-all duration-200 group-hover/tooltip:opacity-100"
        style={{
          background: 'linear-gradient(135deg, rgba(15, 15, 24, 0.98) 0%, rgba(20, 20, 30, 0.98) 100%)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(139, 92, 246, 0.2)',
          whiteSpace: 'nowrap',
        }}
      >
        {content}
        {/* Arrow */}
        <div 
          className="absolute right-full top-1/2 -translate-y-1/2"
          style={{
            width: 0,
            height: 0,
            borderTop: '6px solid transparent',
            borderBottom: '6px solid transparent',
            borderRight: '6px solid rgba(15, 15, 24, 0.98)',
          }}
        />
      </div>
    </div>
  );
};

export const EnhancedSidebar: React.FC = () => {
  const { currentView, setCurrentView } = useNavigation();
  const { theme, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile/tablet viewport
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
      if (window.innerWidth < 1024) {
        setCollapsed(true);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Auto-collapse on mobile after navigation
  useEffect(() => {
    if (isMobile) {
      const timer = setTimeout(() => setCollapsed(true), 300);
      return () => clearTimeout(timer);
    }
  }, [currentView, isMobile]);

  const handleToggle = () => {
    setCollapsed((prev) => !prev);
  };

  const isDark = theme === 'dark';

  return (
    <>
      {/* Mobile overlay */}
      {isMobile && !collapsed && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity duration-300 lg:hidden"
          onClick={() => setCollapsed(true)}
          style={{ animation: 'fadeIn 0.3s ease-out' }}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed bottom-0 right-0 top-0 z-50 flex flex-col border-l transition-all duration-500 ease-in-out lg:relative ${
          collapsed ? 'w-[72px]' : 'w-[280px]'
        } ${isMobile && collapsed ? 'translate-x-full' : 'translate-x-0'}`}
        style={{
          background: isDark
            ? 'linear-gradient(135deg, rgba(15, 15, 24, 0.98) 0%, rgba(20, 20, 30, 0.98) 50%, rgba(25, 15, 35, 0.98) 100%)'
            : 'linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 249, 255, 0.98) 50%, rgba(243, 244, 246, 0.98) 100%)',
          backdropFilter: 'blur(20px)',
          borderColor: isDark ? 'rgba(139, 92, 246, 0.15)' : 'rgba(139, 92, 246, 0.1)',
          boxShadow: isDark
            ? '0 0 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.05)'
            : '0 0 40px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.8)',
        }}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        {/* Animated gradient overlay */}
        <div 
          className="pointer-events-none absolute inset-0 opacity-20"
          style={{
            background: isDark
              ? 'radial-gradient(circle at 50% 0%, rgba(139, 92, 246, 0.15) 0%, transparent 50%)'
              : 'radial-gradient(circle at 50% 0%, rgba(139, 92, 246, 0.08) 0%, transparent 50%)',
            animation: 'pulse 4s ease-in-out infinite',
          }}
        />

        {/* Top highlight */}
        <div 
          className="absolute left-0 right-0 top-0 h-px"
          style={{
            background: 'linear-gradient(90deg, transparent 0%, rgba(139, 92, 246, 0.5) 50%, transparent 100%)',
          }}
        />

        {/* Header */}
        <div className="relative flex items-center justify-between border-b px-5 py-4"
          style={{
            borderColor: isDark ? 'rgba(139, 92, 246, 0.15)' : 'rgba(139, 92, 246, 0.1)',
          }}
        >
          <div className="flex items-center gap-3 overflow-hidden">
            {/* Logo */}
            <span 
              className="relative inline-flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl shadow-lg transition-all duration-300 hover:scale-110 hover:rotate-12"
              style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
                boxShadow: '0 8px 24px rgba(139, 92, 246, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.2)',
              }}
            >
              <Zap 
                className="h-5 w-5 text-white" 
                aria-hidden="true"
                style={{ filter: 'drop-shadow(0 0 8px rgba(255, 255, 255, 0.5))' }}
              />
            </span>
            
            {/* Brand text */}
            {!collapsed && (
              <div className="min-w-0 flex-1 transition-opacity duration-300">
                <p 
                  className="truncate text-sm font-bold uppercase tracking-wide"
                  style={{
                    background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Bolt AI
                </p>
                <p className={`truncate text-xs ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                  {t('layout.sidebarTagline')}
                </p>
              </div>
            )}
          </div>
          
          {/* Collapse toggle button */}
          <button
            type="button"
            className={`inline-flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border transition-all duration-300 hover:scale-110 ${
              isDark
                ? 'border-purple-500/30 text-slate-400 hover:border-purple-400/50 hover:bg-purple-500/10 hover:text-purple-400'
                : 'border-purple-300/50 text-slate-600 hover:border-purple-400 hover:bg-purple-50 hover:text-purple-600'
            }`}
            style={{
              background: isDark ? 'rgba(15, 15, 24, 0.6)' : 'rgba(255, 255, 255, 0.8)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1), inset 0 1px 1px rgba(255, 255, 255, 0.1)',
              transform: collapsed ? 'rotate(180deg)' : 'rotate(0deg)',
            }}
            onClick={handleToggle}
            aria-label={collapsed ? 'Expand navigation' : 'Collapse navigation'}
            aria-expanded={!collapsed}
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        {/* Navigation */}
        <nav 
          className="relative flex-1 overflow-x-hidden overflow-y-auto px-2 py-4"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: isDark 
              ? 'rgba(139, 92, 246, 0.3) rgba(0, 0, 0, 0.1)'
              : 'rgba(139, 92, 246, 0.2) rgba(0, 0, 0, 0.05)',
          }}
          role="navigation"
          aria-label="Main navigation"
        >
          <style>{`
            nav::-webkit-scrollbar {
              width: 6px;
            }
            nav::-webkit-scrollbar-track {
              background: ${isDark ? 'rgba(0, 0, 0, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
            }
            nav::-webkit-scrollbar-thumb {
              background: ${isDark ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.2)'};
              border-radius: 3px;
            }
            nav::-webkit-scrollbar-thumb:hover {
              background: ${isDark ? 'rgba(139, 92, 246, 0.5)' : 'rgba(139, 92, 246, 0.35)'};
            }
          `}</style>

          {Object.entries(groupedNavItems).map(([category, items], categoryIndex) => (
            <div key={category} className="mb-6 last:mb-0">
              {/* Category label */}
              {!collapsed && (
                <div 
                  className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider"
                  style={{
                    color: isDark ? 'rgba(148, 163, 184, 0.6)' : 'rgba(71, 85, 105, 0.7)',
                    letterSpacing: '0.1em',
                  }}
                >
                  {category}
                </div>
              )}

              {/* Category items */}
              <ul className="space-y-1">
                {items.map((item, index) => {
                  const Icon = item.icon;
                  const isActive = currentView === item.id;
                  const globalIndex = categoryIndex * 10 + index;

                  const button = (
                    <button
                      type="button"
                      onClick={() => setCurrentView(item.id)}
                      className={`group relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-300 ${
                        isActive
                          ? isDark ? 'text-white' : 'text-purple-900'
                          : isDark ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-purple-900'
                      }`}
                      style={isActive ? {
                        background: isDark
                          ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(168, 85, 247, 0.15) 100%)'
                          : 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.08) 100%)',
                        boxShadow: isDark
                          ? '0 4px 16px rgba(139, 92, 246, 0.3), inset 0 1px 2px rgba(255, 255, 255, 0.1)'
                          : '0 4px 16px rgba(139, 92, 246, 0.2), inset 0 1px 2px rgba(255, 255, 255, 0.5)',
                        border: `1px solid ${isDark ? 'rgba(139, 92, 246, 0.3)' : 'rgba(139, 92, 246, 0.2)'}`,
                        animation: `slideIn 0.3s ease-out ${globalIndex * 0.03}s both`,
                      } : {
                        animation: `slideIn 0.3s ease-out ${globalIndex * 0.03}s both`,
                      }}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      {/* Hover glow effect */}
                      {!isActive && (
                        <div 
                          className="absolute inset-0 rounded-xl opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                          style={{
                            background: isDark
                              ? 'radial-gradient(circle at center, rgba(139, 92, 246, 0.15) 0%, transparent 70%)'
                              : 'radial-gradient(circle at center, rgba(139, 92, 246, 0.08) 0%, transparent 70%)',
                          }}
                        />
                      )}

                      {/* Icon container */}
                      <span
                        className={`relative flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl transition-all duration-300 ${
                          isActive ? 'scale-110' : 'scale-100 group-hover:scale-110'
                        }`}
                        style={isActive ? {
                          background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%)',
                          boxShadow: '0 8px 20px rgba(139, 92, 246, 0.5), inset 0 1px 2px rgba(255, 255, 255, 0.2)',
                        } : {
                          background: isDark ? 'rgba(15, 15, 24, 0.6)' : 'rgba(248, 250, 252, 0.8)',
                          border: `1px solid ${isDark ? 'rgba(139, 92, 246, 0.2)' : 'rgba(139, 92, 246, 0.15)'}`,
                        }}
                      >
                        <Icon 
                          className={`h-4 w-4 transition-all duration-300 ${
                            isActive 
                              ? 'text-white' 
                              : isDark 
                                ? 'text-slate-400 group-hover:text-purple-400' 
                                : 'text-slate-600 group-hover:text-purple-600'
                          }`}
                          aria-hidden="true"
                          style={isActive ? {
                            filter: 'drop-shadow(0 0 6px rgba(255, 255, 255, 0.5))'
                          } : {}}
                        />
                      </span>

                      {/* Label */}
                      {!collapsed && (
                        <span 
                          className={`relative z-10 flex-1 truncate transition-all duration-300 ${
                            isActive ? 'font-semibold' : 'group-hover:translate-x-1'
                          }`}
                        >
                          {item.label}
                        </span>
                      )}

                      {/* Badge */}
                      {!collapsed && item.badge && (
                        <span 
                          className="ml-auto rounded-full px-2 py-0.5 text-xs font-semibold"
                          style={{
                            background: isActive
                              ? 'linear-gradient(135deg, #ec4899 0%, #f43f5e 100%)'
                              : isDark
                                ? 'rgba(139, 92, 246, 0.2)'
                                : 'rgba(139, 92, 246, 0.1)',
                            color: isActive ? 'white' : isDark ? '#c084fc' : '#7e22ce',
                          }}
                        >
                          {item.badge}
                        </span>
                      )}

                      {/* Active indicator */}
                      {isActive && !collapsed && (
                        <div 
                          className="absolute right-2 h-1.5 w-1.5 rounded-full"
                          style={{
                            background: '#a78bfa',
                            boxShadow: '0 0 8px rgba(167, 139, 250, 0.8)',
                            animation: 'pulse 2s ease-in-out infinite',
                          }}
                        />
                      )}
                    </button>
                  );

                  return (
                    <li key={item.id}>
                      {collapsed ? (
                        <Tooltip content={item.label} show={collapsed}>
                          {button}
                        </Tooltip>
                      ) : (
                        button
                      )}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div 
          className="relative border-t px-4 py-4"
          style={{
            borderColor: isDark ? 'rgba(139, 92, 246, 0.15)' : 'rgba(139, 92, 246, 0.1)',
          }}
        >
          {/* Theme toggle */}
          <button
            type="button"
            onClick={toggleTheme}
            className={`mb-3 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-300 ${
              isDark
                ? 'text-slate-400 hover:bg-purple-500/10 hover:text-purple-400'
                : 'text-slate-600 hover:bg-purple-50 hover:text-purple-600'
            }`}
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
          >
            <span
              className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl transition-all duration-300"
              style={{
                background: isDark ? 'rgba(15, 15, 24, 0.6)' : 'rgba(248, 250, 252, 0.8)',
                border: `1px solid ${isDark ? 'rgba(139, 92, 246, 0.2)' : 'rgba(139, 92, 246, 0.15)'}`,
              }}
            >
              {isDark ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </span>
            {!collapsed && (
              <span className="flex-1 text-left">
                {isDark ? 'Light Mode' : 'Dark Mode'}
              </span>
            )}
          </button>

          {/* Status indicator */}
          {!collapsed ? (
            <div 
              className="relative overflow-hidden rounded-xl px-4 py-3 transition-all duration-300 hover:scale-105"
              style={{
                background: isDark
                  ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.10) 100%)'
                  : 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%)',
                border: `1px solid ${isDark ? 'rgba(16, 185, 129, 0.3)' : 'rgba(16, 185, 129, 0.2)'}`,
                boxShadow: isDark
                  ? '0 4px 16px rgba(16, 185, 129, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.1)'
                  : '0 4px 16px rgba(16, 185, 129, 0.1), inset 0 1px 1px rgba(255, 255, 255, 0.5)',
              }}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <div 
                  className="h-2 w-2 rounded-full"
                  style={{
                    background: '#10b981',
                    boxShadow: '0 0 10px rgba(16, 185, 129, 0.8)',
                    animation: 'pulse 2s ease-in-out infinite',
                  }}
                />
                <p className="text-sm font-bold text-emerald-400">
                  {t('layout.sidebarOnline')}
                </p>
              </div>
              <p className={`text-[10px] pl-4 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                {t('layout.sidebarDetails')}
              </p>
            </div>
          ) : (
            <div className="flex h-12 items-center justify-center">
              <div 
                className="h-3 w-3 rounded-full"
                style={{
                  background: '#10b981',
                  boxShadow: '0 0 10px rgba(16, 185, 129, 0.8)',
                  animation: 'pulse 2s ease-in-out infinite',
                }}
              />
            </div>
          )}
        </div>

        {/* Animations */}
        <style>{`
          @keyframes fadeIn {
            from {
              opacity: 0;
            }
            to {
              opacity: 1;
            }
          }
          
          @keyframes slideIn {
            from {
              opacity: 0;
              transform: translateX(-20px);
            }
            to {
              opacity: 1;
              transform: translateX(0);
            }
          }
          
          @keyframes pulse {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
          }
        `}</style>
      </aside>
    </>
  );
};

