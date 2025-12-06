/**
 * CacheManager - Intelligent Caching Layer for API Data
 * 
 * Phase 2 Implementation - Performance Optimization
 * 
 * Features:
 * - In-memory caching with configurable TTL
 * - Automatic cache invalidation
 * - LRU (Least Recently Used) eviction policy
 * - Cache statistics and monitoring
 * - Support for stale-while-revalidate pattern
 * - Namespace support for organized caching
 * 
 * @version 1.0.0
 * @since Phase 2
 */

interface CacheEntry<T> {
    data: T;
    timestamp: number;
    ttl: number;
    hits: number;
    lastAccessed: number;
    namespace: string;
    key: string;
}

interface CacheOptions {
    /** Time to live in milliseconds (default: 5 minutes) */
    ttl?: number;
    /** Whether to return stale data while revalidating (default: true) */
    staleWhileRevalidate?: boolean;
    /** Namespace for organizing cache entries */
    namespace?: string;
}

interface CacheStats {
    totalEntries: number;
    totalHits: number;
    totalMisses: number;
    hitRate: number;
    memoryUsage: number;
    namespaces: Record<string, number>;
}

type RevalidateFn<T> = () => Promise<T>;

class CacheManager {
    private cache: Map<string, CacheEntry<any>> = new Map();
    private maxSize: number = 1000;
    private totalHits: number = 0;
    private totalMisses: number = 0;
    private revalidationQueue: Set<string> = new Set();
    private defaultTTL: number = 5 * 60 * 1000; // 5 minutes

    constructor(maxSize: number = 1000) {
        this.maxSize = maxSize;
        
        // Periodic cleanup of expired entries
        setInterval(() => this.cleanup(), 60 * 1000); // Every minute
    }

    /**
     * Generate a unique cache key
     */
    private generateKey(key: string, namespace: string = 'default'): string {
        return `${namespace}:${key}`;
    }

    /**
     * Set a value in the cache
     */
    set<T>(key: string, data: T, options: CacheOptions = {}): void {
        const {
            ttl = this.defaultTTL,
            namespace = 'default'
        } = options;

        const fullKey = this.generateKey(key, namespace);
        const now = Date.now();

        // Evict if at capacity
        if (this.cache.size >= this.maxSize && !this.cache.has(fullKey)) {
            this.evictLRU();
        }

        const entry: CacheEntry<T> = {
            data,
            timestamp: now,
            ttl,
            hits: 0,
            lastAccessed: now,
            namespace,
            key
        };

        this.cache.set(fullKey, entry);
    }

    /**
     * Get a value from the cache
     */
    get<T>(key: string, options: CacheOptions = {}): T | null {
        const { namespace = 'default' } = options;
        const fullKey = this.generateKey(key, namespace);
        const entry = this.cache.get(fullKey) as CacheEntry<T> | undefined;

        if (!entry) {
            this.totalMisses++;
            return null;
        }

        const now = Date.now();
        const isExpired = now - entry.timestamp > entry.ttl;

        if (isExpired && !options.staleWhileRevalidate) {
            this.totalMisses++;
            this.cache.delete(fullKey);
            return null;
        }

        // Update access statistics
        entry.hits++;
        entry.lastAccessed = now;
        this.totalHits++;

        return entry.data;
    }

    /**
     * Get or set with automatic revalidation
     */
    async getOrSet<T>(
        key: string,
        fetchFn: RevalidateFn<T>,
        options: CacheOptions = {}
    ): Promise<T> {
        const { namespace = 'default', staleWhileRevalidate = true } = options;
        const fullKey = this.generateKey(key, namespace);
        const cached = this.get<T>(key, { ...options, staleWhileRevalidate: true });

        if (cached !== null) {
            const entry = this.cache.get(fullKey);
            const isExpired = entry && Date.now() - entry.timestamp > entry.ttl;

            // If stale and not already revalidating, trigger background revalidation
            if (isExpired && staleWhileRevalidate && !this.revalidationQueue.has(fullKey)) {
                this.revalidateInBackground(key, fetchFn, options);
            }

            return cached;
        }

        // Cache miss - fetch and cache
        const data = await fetchFn();
        this.set(key, data, options);
        return data;
    }

    /**
     * Background revalidation (stale-while-revalidate pattern)
     */
    private async revalidateInBackground<T>(
        key: string,
        fetchFn: RevalidateFn<T>,
        options: CacheOptions
    ): Promise<void> {
        const { namespace = 'default' } = options;
        const fullKey = this.generateKey(key, namespace);

        if (this.revalidationQueue.has(fullKey)) {
            return;
        }

        this.revalidationQueue.add(fullKey);

        try {
            const data = await fetchFn();
            this.set(key, data, options);
        } catch (error) {
            console.error(`Cache revalidation failed for ${fullKey}:`, error);
        } finally {
            this.revalidationQueue.delete(fullKey);
        }
    }

    /**
     * Check if a key exists and is not expired
     */
    has(key: string, namespace: string = 'default'): boolean {
        const fullKey = this.generateKey(key, namespace);
        const entry = this.cache.get(fullKey);

        if (!entry) return false;

        const isExpired = Date.now() - entry.timestamp > entry.ttl;
        if (isExpired) {
            this.cache.delete(fullKey);
            return false;
        }

        return true;
    }

    /**
     * Delete a specific key
     */
    delete(key: string, namespace: string = 'default'): boolean {
        const fullKey = this.generateKey(key, namespace);
        return this.cache.delete(fullKey);
    }

    /**
     * Clear all entries in a namespace
     */
    clearNamespace(namespace: string): number {
        let cleared = 0;
        for (const [key, entry] of this.cache.entries()) {
            if (entry.namespace === namespace) {
                this.cache.delete(key);
                cleared++;
            }
        }
        return cleared;
    }

    /**
     * Clear all cache entries
     */
    clear(): void {
        this.cache.clear();
        this.totalHits = 0;
        this.totalMisses = 0;
    }

    /**
     * Evict least recently used entry
     */
    private evictLRU(): void {
        let oldestKey: string | null = null;
        let oldestAccess = Infinity;

        for (const [key, entry] of this.cache.entries()) {
            if (entry.lastAccessed < oldestAccess) {
                oldestAccess = entry.lastAccessed;
                oldestKey = key;
            }
        }

        if (oldestKey) {
            this.cache.delete(oldestKey);
        }
    }

    /**
     * Clean up expired entries
     */
    private cleanup(): void {
        const now = Date.now();
        for (const [key, entry] of this.cache.entries()) {
            if (now - entry.timestamp > entry.ttl) {
                this.cache.delete(key);
            }
        }
    }

    /**
     * Get cache statistics
     */
    getStats(): CacheStats {
        const namespaces: Record<string, number> = {};
        
        for (const entry of this.cache.values()) {
            namespaces[entry.namespace] = (namespaces[entry.namespace] || 0) + 1;
        }

        const totalRequests = this.totalHits + this.totalMisses;
        const hitRate = totalRequests > 0 ? this.totalHits / totalRequests : 0;

        // Rough memory estimation
        let memoryUsage = 0;
        for (const entry of this.cache.values()) {
            memoryUsage += JSON.stringify(entry.data).length * 2; // UTF-16 chars
        }

        return {
            totalEntries: this.cache.size,
            totalHits: this.totalHits,
            totalMisses: this.totalMisses,
            hitRate,
            memoryUsage,
            namespaces
        };
    }

    /**
     * Invalidate cache entries based on a pattern
     */
    invalidatePattern(pattern: RegExp, namespace?: string): number {
        let invalidated = 0;
        for (const [key, entry] of this.cache.entries()) {
            if (namespace && entry.namespace !== namespace) continue;
            if (pattern.test(entry.key)) {
                this.cache.delete(key);
                invalidated++;
            }
        }
        return invalidated;
    }

    /**
     * Prefetch and cache data
     */
    async prefetch<T>(
        keys: string[],
        fetchFn: (key: string) => Promise<T>,
        options: CacheOptions = {}
    ): Promise<void> {
        const promises = keys.map(async (key) => {
            if (!this.has(key, options.namespace)) {
                try {
                    const data = await fetchFn(key);
                    this.set(key, data, options);
                } catch (error) {
                    console.error(`Prefetch failed for ${key}:`, error);
                }
            }
        });

        await Promise.all(promises);
    }
}

// Singleton instance
export const cacheManager = new CacheManager();

// Named exports for specific cache namespaces
export const marketCache = {
    get: <T>(key: string) => cacheManager.get<T>(key, { namespace: 'market' }),
    set: <T>(key: string, data: T, ttl?: number) => 
        cacheManager.set(key, data, { namespace: 'market', ttl }),
    getOrSet: <T>(key: string, fetchFn: RevalidateFn<T>, ttl?: number) =>
        cacheManager.getOrSet(key, fetchFn, { namespace: 'market', ttl }),
    clear: () => cacheManager.clearNamespace('market'),
};

export const userCache = {
    get: <T>(key: string) => cacheManager.get<T>(key, { namespace: 'user' }),
    set: <T>(key: string, data: T, ttl?: number) =>
        cacheManager.set(key, data, { namespace: 'user', ttl }),
    getOrSet: <T>(key: string, fetchFn: RevalidateFn<T>, ttl?: number) =>
        cacheManager.getOrSet(key, fetchFn, { namespace: 'user', ttl }),
    clear: () => cacheManager.clearNamespace('user'),
};

export const chartCache = {
    get: <T>(key: string) => cacheManager.get<T>(key, { namespace: 'chart' }),
    set: <T>(key: string, data: T, ttl?: number) =>
        cacheManager.set(key, data, { namespace: 'chart', ttl }),
    getOrSet: <T>(key: string, fetchFn: RevalidateFn<T>, ttl?: number) =>
        cacheManager.getOrSet(key, fetchFn, { namespace: 'chart', ttl, staleWhileRevalidate: true }),
    clear: () => cacheManager.clearNamespace('chart'),
};

export default cacheManager;

