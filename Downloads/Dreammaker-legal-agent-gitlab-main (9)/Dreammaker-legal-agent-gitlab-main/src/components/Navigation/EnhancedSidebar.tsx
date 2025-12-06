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
import { StatusAccordion } from './StatusAccordion';

interface NavigationItem {
    id: NavigationView;
    label: string;
    icon: React.ComponentType<any>;
    badge?: string;
    category?: string;
}

// Organize navigation items by category for better UX
// ✨ Phase 2 Complete: Unified hubs with consolidated features
const NAV_ITEMS: NavigationItem[] = [
    // Overview
    { id: 'dashboard', label: t('navigation.dashboard'), icon: Home, category: 'Overview' },

    // Market Analysis - ✅ Phase 2: Consolidated Market Analysis Hub (3 tabs)
    { id: 'market-analysis', label: 'Market Analysis', icon: BarChart3, badge: '3 Tabs ⭐', category: 'Markets' },

    // Trading - ✅ Phase 2 Enhanced: Trading Hub with Quick Actions
    { id: 'trading', label: 'Trading Hub', icon: Layers, badge: '5 Tabs ⭐', category: 'Trading' },

    // Portfolio & Risk - ✅ Risk Management consolidated
    { id: 'professional-risk', label: 'Risk Center', icon: Shield, badge: '2 Tabs', category: 'Portfolio & Risk' },

    // Strategy & AI - ✅ Phase 2: Unified AI Lab (5 tabs)
    { id: 'ai-lab', label: 'AI Lab', icon: Sparkles, badge: '5 Tabs ⭐', category: 'Strategy & AI' },

    // System - ✅ Phase 3: Unified Admin Hub (3 tabs)
    { id: 'admin', label: 'Admin Hub', icon: Stethoscope, badge: '3 Tabs', category: 'System' },
    { id: 'settings', label: t('navigation.settings'), icon: Settings, category: 'System' },
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

            {/* Enhanced Compact Sidebar on Right */}
            <aside
                className={`fixed bottom-0 right-0 top-0 z-50 flex flex-col border-l transition-all duration-500 ease-in-out lg:relative ${collapsed ? 'w-[64px]' : 'w-[260px]'
                    } ${isMobile && collapsed ? 'translate-x-full' : 'translate-x-0'}`}
                style={{
                    background: isDark
                        ? 'linear-gradient(160deg, rgba(10, 10, 20, 0.98) 0%, rgba(20, 15, 35, 0.98) 40%, rgba(25, 15, 45, 0.98) 70%, rgba(15, 10, 30, 0.98) 100%)'
                        : 'linear-gradient(160deg, rgba(255, 255, 255, 0.98) 0%, rgba(250, 248, 255, 0.98) 40%, rgba(245, 243, 255, 0.98) 70%, rgba(248, 246, 252, 0.98) 100%)',
                    backdropFilter: 'blur(24px) saturate(180%)',
                    borderColor: isDark ? 'rgba(139, 92, 246, 0.25)' : 'rgba(139, 92, 246, 0.15)',
                    boxShadow: isDark
                        ? '-8px 0 80px rgba(139, 92, 246, 0.15), -4px 0 40px rgba(0, 0, 0, 0.6), inset 1px 0 0 rgba(139, 92, 246, 0.1)'
                        : '-8px 0 60px rgba(139, 92, 246, 0.08), -4px 0 30px rgba(0, 0, 0, 0.1), inset 1px 0 0 rgba(255, 255, 255, 0.9)',
                }}
                onMouseEnter={() => setIsHovering(true)}
                onMouseLeave={() => setIsHovering(false)}
            >
                {/* Enhanced animated gradient overlays */}
                <div
                    className="pointer-events-none absolute inset-0 opacity-30"
                    style={{
                        background: isDark
                            ? 'radial-gradient(circle at 100% 0%, rgba(139, 92, 246, 0.25) 0%, rgba(168, 85, 247, 0.15) 30%, transparent 60%), radial-gradient(circle at 100% 100%, rgba(59, 130, 246, 0.15) 0%, transparent 50%)'
                            : 'radial-gradient(circle at 100% 0%, rgba(139, 92, 246, 0.12) 0%, rgba(168, 85, 247, 0.08) 30%, transparent 60%), radial-gradient(circle at 100% 100%, rgba(59, 130, 246, 0.08) 0%, transparent 50%)',
                        animation: 'pulse 6s ease-in-out infinite',
                    }}
                />



                {/* Enhanced border highlights */}
                <div
                    className="absolute left-0 right-0 top-0 h-px"
                    style={{
                        background: 'linear-gradient(270deg, rgba(139, 92, 246, 0.6) 0%, rgba(168, 85, 247, 0.4) 50%, transparent 100%)',
                    }}
                />
                <div
                    className="absolute bottom-0 left-0 right-0 h-px"
                    style={{
                        background: 'linear-gradient(270deg, rgba(59, 130, 246, 0.4) 0%, rgba(139, 92, 246, 0.3) 50%, transparent 100%)',
                    }}
                />

                {/* Dashboard Header in Sidebar */}
                <div className="relative border-b px-3 py-4"
                    style={{
                        borderColor: isDark ? 'rgba(139, 92, 246, 0.2)' : 'rgba(139, 92, 246, 0.15)',
                        background: isDark
                            ? 'linear-gradient(180deg, rgba(139, 92, 246, 0.08) 0%, transparent 100%)'
                            : 'linear-gradient(180deg, rgba(139, 92, 246, 0.05) 0%, transparent 100%)',
                    }}
                >
                    {!collapsed ? (
                        <div className="flex flex-col gap-3">
                            {/* Logo and Brand */}
                            <div className="flex items-center gap-2.5 flex-row-reverse">
                                <span
                                    className="relative inline-flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl shadow-lg transition-all duration-300 hover:scale-110 hover:rotate-12"
                                    style={{
                                        background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 50%, #ec4899 100%)',
                                        boxShadow: '0 8px 32px rgba(139, 92, 246, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.25)',
                                    }}
                                >
                                    <Zap
                                        className="h-5 w-5 text-white"
                                        aria-hidden="true"
                                        style={{
                                            filter: 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.8))',
                                        }}
                                    />
                                </span>

                                <div className="min-w-0 flex-1">
                                    <p
                                        className="truncate text-sm font-extrabold uppercase tracking-wider"
                                        style={{
                                            backgroundImage: 'linear-gradient(135deg, #a855f7 0%, #ec4899 70%, #f97316 100%)',
                                            WebkitBackgroundClip: 'text',
                                            WebkitTextFillColor: 'transparent',
                                            backgroundClip: 'text',
                                        }}
                                    >
                                        BOLT AI
                                    </p>
                                    <p className={`truncate text-[10px] font-medium ${isDark ? 'text-purple-400/70' : 'text-purple-600/70'}`}>
                                        ⚡ {t('layout.sidebarTagline')}
                                    </p>
                                </div>

                                {/* Collapse Toggle */}
                                <button
                                    type="button"
                                    className={`inline-flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-lg border transition-all duration-300 hover:scale-110 ${isDark
                                        ? 'border-purple-500/40 text-slate-300 hover:border-purple-400/60 hover:bg-purple-500/20 hover:text-purple-300'
                                        : 'border-purple-400/50 text-slate-700 hover:border-purple-500 hover:bg-purple-100 hover:text-purple-700'
                                        }`}
                                    style={{
                                        background: isDark
                                            ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)'
                                            : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(249, 250, 251, 0.9) 100%)',
                                        boxShadow: isDark
                                            ? '0 4px 16px rgba(139, 92, 246, 0.3), inset 0 1px 2px rgba(255, 255, 255, 0.1)'
                                            : '0 4px 12px rgba(139, 92, 246, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.5)',
                                    }}
                                    onClick={handleToggle}
                                    aria-label="Collapse navigation"
                                    aria-expanded={!collapsed}
                                >
                                    <ChevronRight className="h-3.5 w-3.5" />
                                </button>
                            </div>

                            {/* Dashboard Title */}
                            <div className="text-right">
                                <h1 className={`text-lg font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>
                                    Trading Dashboard
                                </h1>
                                <p className={`text-xs mt-0.5 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                                    Real-time market analysis
                                </p>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center gap-2">
                            {/* Collapsed Logo */}
                            <span
                                className="relative inline-flex h-10 w-10 items-center justify-center rounded-xl shadow-lg transition-all duration-300 hover:scale-110 hover:rotate-12"
                                style={{
                                    background: 'linear-gradient(135deg, #8b5cf6 0%, #a78bfa 50%, #ec4899 100%)',
                                    boxShadow: '0 8px 32px rgba(139, 92, 246, 0.6), inset 0 2px 4px rgba(255, 255, 255, 0.25)',
                                }}
                            >
                                <Zap
                                    className="h-5 w-5 text-white"
                                    aria-hidden="true"
                                    style={{
                                        filter: 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.8))',
                                    }}
                                />
                            </span>

                            {/* Expand Toggle */}
                            <button
                                type="button"
                                className={`inline-flex h-7 w-7 items-center justify-center rounded-lg border transition-all duration-300 hover:scale-110 ${isDark
                                    ? 'border-purple-500/40 text-slate-300 hover:border-purple-400/60 hover:bg-purple-500/20 hover:text-purple-300'
                                    : 'border-purple-400/50 text-slate-700 hover:border-purple-500 hover:bg-purple-100 hover:text-purple-700'
                                    }`}
                                style={{
                                    background: isDark
                                        ? 'linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)'
                                        : 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(249, 250, 251, 0.9) 100%)',
                                    boxShadow: isDark
                                        ? '0 4px 16px rgba(139, 92, 246, 0.3), inset 0 1px 2px rgba(255, 255, 255, 0.1)'
                                        : '0 4px 12px rgba(139, 92, 246, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.5)',
                                    transform: 'rotate(180deg)',
                                }}
                                onClick={handleToggle}
                                aria-label="Expand navigation"
                                aria-expanded={!collapsed}
                            >
                                <ChevronRight className="h-3.5 w-3.5" />
                            </button>
                        </div>
                    )}
                </div>

                {/* Compact Navigation */}
                <nav
                    className="relative flex-1 overflow-x-hidden overflow-y-auto px-2 py-3"
                    style={{
                        scrollbarWidth: 'thin',
                        scrollbarColor: isDark
                            ? 'rgba(139, 92, 246, 0.4) rgba(0, 0, 0, 0.2)'
                            : 'rgba(139, 92, 246, 0.3) rgba(0, 0, 0, 0.1)',
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
                        <div key={category} className="mb-4 last:mb-0">
                            {/* Category label */}
                            {!collapsed && (
                                <div
                                    className="mb-1.5 px-3 text-[10px] font-bold uppercase tracking-wider text-right"
                                    style={{
                                        color: isDark ? 'rgba(148, 163, 184, 0.6)' : 'rgba(71, 85, 105, 0.7)',
                                        letterSpacing: '0.12em',
                                    }}
                                >
                                    {category}
                                </div>
                            )}

                            {/* Category items */}
                            <ul className="space-y-0.5">
                                {items.map((item, index) => {
                                    const Icon = item.icon;
                                    const isActive = currentView === item.id;
                                    const globalIndex = categoryIndex * 10 + index;

                                    const button = (
                                        <button
                                            type="button"
                                            onClick={() => setCurrentView(item.id)}
                                            className={`group relative flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 flex-row-reverse ${isActive
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
                                                className={`relative flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-xl transition-all duration-300 ${isActive ? 'scale-110' : 'scale-100 group-hover:scale-110'
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
                                                    className={`h-4 w-4 transition-all duration-300 ${isActive
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
                                                    className={`relative z-10 flex-1 truncate transition-all duration-300 text-right ${isActive ? 'font-semibold' : 'group-hover:translate-x-1'
                                                        }`}
                                                >
                                                    {item.label}
                                                </span>
                                            )}



                                            {/* Active indicator */}
                                            {isActive && !collapsed && (
                                                <div
                                                    className="absolute left-2 h-1.5 w-1.5 rounded-full"
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
                    className="relative border-t px-3 py-3"
                    style={{
                        borderColor: isDark ? 'rgba(139, 92, 246, 0.15)' : 'rgba(139, 92, 246, 0.1)',
                    }}
                >
                    {/* Theme toggle */}
                    <button
                        type="button"
                        onClick={toggleTheme}
                        className={`mb-3 flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-300 flex-row-reverse ${isDark
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

                    {/* Status Accordion */}
                    <StatusAccordion collapsed={collapsed} />
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

