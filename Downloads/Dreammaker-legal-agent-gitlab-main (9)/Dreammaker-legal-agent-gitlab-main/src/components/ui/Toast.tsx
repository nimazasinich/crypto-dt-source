import React, { useEffect, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertCircle,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
  X,
  Loader2,
} from 'lucide-react';

// ============================================================================
// Types
// ============================================================================

export type ToastType = 'info' | 'warning' | 'error' | 'success' | 'loading';
export type ToastPosition = 'top-right' | 'top-left' | 'top-center' | 'bottom-right' | 'bottom-left' | 'bottom-center';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  dismissible?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: React.ReactNode;
  progress?: boolean;
}

export interface ToastOptions {
  title: string;
  message?: string;
  duration?: number;
  dismissible?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: React.ReactNode;
  progress?: boolean;
}

// ============================================================================
// Toast Store
// ============================================================================

let toastIdCounter = 0;
const toastListeners = new Set<(toasts: Toast[]) => void>();
let currentToasts: Toast[] = [];
let defaultPosition: ToastPosition = 'top-right';
let defaultDuration = 5000;

const notifyListeners = () => {
  toastListeners.forEach(listener => listener([...currentToasts]));
};

// ============================================================================
// Toast API
// ============================================================================

export function showToast(type: ToastType, title: string, message?: string, options?: Partial<ToastOptions>) {
  const id = `toast-${Date.now()}-${toastIdCounter++}`;
  const duration = options?.duration ?? (type === 'loading' ? Infinity : defaultDuration);
  
  const newToast: Toast = {
    id,
    type,
    title,
    message,
    duration,
    dismissible: options?.dismissible ?? true,
    action: options?.action,
    icon: options?.icon,
    progress: options?.progress ?? (type !== 'loading'),
  };

  currentToasts = [...currentToasts, newToast];
  notifyListeners();

  // Auto-dismiss (unless duration is Infinity)
  if (duration !== Infinity) {
    setTimeout(() => {
      dismissToast(id);
    }, duration);
  }

  return id;
}

export function dismissToast(id: string) {
  currentToasts = currentToasts.filter(t => t.id !== id);
  notifyListeners();
}

export function dismissAllToasts() {
  currentToasts = [];
  notifyListeners();
}

export function updateToast(id: string, updates: Partial<Toast>) {
  currentToasts = currentToasts.map(t => 
    t.id === id ? { ...t, ...updates } : t
  );
  notifyListeners();
}

// Convenience methods
export const toast = {
  info: (title: string, message?: string, options?: Partial<ToastOptions>) => 
    showToast('info', title, message, options),
  
  success: (title: string, message?: string, options?: Partial<ToastOptions>) => 
    showToast('success', title, message, options),
  
  warning: (title: string, message?: string, options?: Partial<ToastOptions>) => 
    showToast('warning', title, message, options),
  
  error: (title: string, message?: string, options?: Partial<ToastOptions>) => 
    showToast('error', title, message, options),
  
  loading: (title: string, message?: string, options?: Partial<ToastOptions>) => 
    showToast('loading', title, message, options),
  
  dismiss: dismissToast,
  dismissAll: dismissAllToasts,
  update: updateToast,
  
  promise: async <T,>(
    promise: Promise<T>,
    {
      loading,
      success,
      error,
    }: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((err: Error) => string);
    }
  ): Promise<T> => {
    const id = showToast('loading', loading);
    
    try {
      const data = await promise;
      updateToast(id, {
        type: 'success',
        title: typeof success === 'function' ? success(data) : success,
        duration: defaultDuration,
        progress: true,
      });
      setTimeout(() => dismissToast(id), defaultDuration);
      return data;
    } catch (err) {
      updateToast(id, {
        type: 'error',
        title: typeof error === 'function' ? error(err as Error) : error,
        duration: defaultDuration,
        progress: true,
      });
      setTimeout(() => dismissToast(id), defaultDuration);
      throw err;
    }
  },
};

// ============================================================================
// Hook
// ============================================================================

function useToasts() {
  const [toasts, setToasts] = useState<Toast[]>([...currentToasts]);

  useEffect(() => {
    const listener = (newToasts: Toast[]) => setToasts(newToasts);
    toastListeners.add(listener);
    return () => {
      toastListeners.delete(listener);
    };
  }, []);

  return toasts;
}

// ============================================================================
// Styles
// ============================================================================

const TYPE_CONFIG: Record<ToastType, {
  icon: React.ComponentType<{ className?: string }>;
  containerClass: string;
  iconClass: string;
  progressClass: string;
}> = {
  info: {
    icon: Info,
    containerClass: 'bg-gradient-to-r from-blue-900/95 to-blue-800/95 border-blue-500/30',
    iconClass: 'text-blue-400',
    progressClass: 'bg-blue-400',
  },
  success: {
    icon: CheckCircle2,
    containerClass: 'bg-gradient-to-r from-emerald-900/95 to-emerald-800/95 border-emerald-500/30',
    iconClass: 'text-emerald-400',
    progressClass: 'bg-emerald-400',
  },
  warning: {
    icon: AlertTriangle,
    containerClass: 'bg-gradient-to-r from-amber-900/95 to-amber-800/95 border-amber-500/30',
    iconClass: 'text-amber-400',
    progressClass: 'bg-amber-400',
  },
  error: {
    icon: XCircle,
    containerClass: 'bg-gradient-to-r from-red-900/95 to-red-800/95 border-red-500/30',
    iconClass: 'text-red-400',
    progressClass: 'bg-red-400',
  },
  loading: {
    icon: Loader2,
    containerClass: 'bg-gradient-to-r from-purple-900/95 to-purple-800/95 border-purple-500/30',
    iconClass: 'text-purple-400 animate-spin',
    progressClass: 'bg-purple-400',
  },
};

const POSITION_STYLES: Record<ToastPosition, string> = {
  'top-right': 'top-4 right-4',
  'top-left': 'top-4 left-4',
  'top-center': 'top-4 left-1/2 -translate-x-1/2',
  'bottom-right': 'bottom-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2',
};

// ============================================================================
// Toast Item Component
// ============================================================================

interface ToastItemProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

const ToastItem = React.forwardRef<HTMLDivElement, ToastItemProps>(({ toast, onDismiss }, ref) => {
  const config = TYPE_CONFIG[toast.type];
  const Icon = config.icon;
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    if (!toast.progress || toast.duration === Infinity) return;

    const startTime = Date.now();
    const duration = toast.duration || defaultDuration;

    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, 100 - (elapsed / duration) * 100);
      setProgress(remaining);

      if (remaining <= 0) {
        clearInterval(interval);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [toast.progress, toast.duration]);

  return (
    <motion.div
      ref={ref}
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 50, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
      className={`
        relative overflow-hidden
        ${config.containerClass}
        backdrop-blur-xl
        border rounded-xl
        shadow-2xl shadow-black/20
        min-w-[320px] max-w-[420px]
        pointer-events-auto
      `}
      role="alert"
      aria-live="polite"
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div className={`flex-shrink-0 mt-0.5 ${config.iconClass}`}>
            {toast.icon || <Icon className="w-5 h-5" />}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-sm text-white leading-tight">
              {toast.title}
            </p>
            {toast.message && (
              <p className="mt-1 text-xs text-white/70 leading-relaxed">
                {toast.message}
              </p>
            )}
            
            {/* Action button */}
            {toast.action && (
              <button
                onClick={() => {
                  toast.action?.onClick();
                  onDismiss(toast.id);
                }}
                className={`
                  mt-2 px-3 py-1.5 text-xs font-semibold rounded-lg
                  ${config.iconClass} bg-white/10 hover:bg-white/20
                  transition-colors duration-200
                `}
              >
                {toast.action.label}
              </button>
            )}
          </div>

          {/* Dismiss button */}
          {toast.dismissible && (
            <button
              onClick={() => onDismiss(toast.id)}
              className="flex-shrink-0 p-1 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Dismiss notification"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      {toast.progress && toast.duration !== Infinity && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
          <motion.div
            className={`h-full ${config.progressClass}`}
            initial={{ width: '100%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.05, ease: 'linear' }}
          />
        </div>
      )}
    </motion.div>
  );
});

ToastItem.displayName = 'ToastItem';

// ============================================================================
// Toast Container Component
// ============================================================================

interface ToastContainerProps {
  position?: ToastPosition;
  maxToasts?: number;
}

export function ToastContainer({
  position = 'top-right',
  maxToasts = 5,
}: ToastContainerProps) {
  const toasts = useToasts();
  const visibleToasts = toasts.slice(-maxToasts);

  return (
    <div
      className={`fixed z-[9999] ${POSITION_STYLES[position]} flex flex-col gap-2 pointer-events-none`}
      aria-label="Notifications"
    >
      <AnimatePresence mode="popLayout">
        {visibleToasts.map(toast => (
          <ToastItem
            key={toast.id}
            toast={toast}
            onDismiss={dismissToast}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}

export default ToastContainer;
