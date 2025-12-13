/**
 * System Monitor - REAL BACKEND DATA VERSION
 * Uses actual API endpoints for real-time system monitoring
 */

class SystemMonitorReal {
  constructor() {
    this.canvas = document.getElementById('network-canvas');
    this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
    
    // Network state
    this.nodes = [];
    this.packets = [];
    this.particles = [];
    this.time = 0;
    
    // System stats (will be populated from backend)
    this.stats = {
      serverRequests: 0,
      serverLoad: 0,
      dbSize: 0,
      dbUsage: 0,
      dbQueries: 0,
      aiTotal: 0,
      aiActive: 0,
      sourcesTotal: 0,
      sourcesActive: 0,
      sourcesHealthy: 0,
      sourcesDegraded: 0,
      sourcesOffline: 0
    };
    
    // Activity log
    this.activities = [];
    this.maxActivities = 10;
    
    // API endpoints
    this.endpoints = {
      sourceHealth: '/api/source-health/status',
      systemMetrics: '/api/monitoring/metrics',
      modelsStatus: '/api/models/status',
      apiStatus: '/api/status'
    };
    
    this.init();
  }
  
  init() {
    console.log('[SystemMonitorReal] Initializing with REAL backend data...');
    
    if (this.canvas && this.ctx) {
      this.setupCanvas();
      this.createNetworkNodes();
      this.startAnimation();
    }
    
    this.setupEventListeners();
    this.startDataUpdates();
    this.updateUI();
    
    // Initial data fetch
    this.fetchAllData();
    
    // Initial animations
    this.animateStats();
    
    console.log('[SystemMonitorReal] Initialized successfully with real backend!');
  }
  
  async fetchAllData() {
    /**
     * Fetch all data from backend in parallel
     */
    try {
      const [sourceHealth, systemMetrics, modelsStatus, apiStatus] = await Promise.all([
        this.fetchSourceHealth(),
        this.fetchSystemMetrics(),
        this.fetchModelsStatus(),
        this.fetchAPIStatus()
      ]);
      
      // Update stats from real data
      if (sourceHealth) {
        this.stats.sourcesTotal = sourceHealth.summary?.total || 0;
        this.stats.sourcesHealthy = sourceHealth.summary?.healthy || 0;
        this.stats.sourcesDegraded = sourceHealth.summary?.degraded || 0;
        this.stats.sourcesOffline = sourceHealth.summary?.offline || 0;
        this.stats.sourcesActive = this.stats.sourcesHealthy + this.stats.sourcesDegraded;
      }
      
      if (modelsStatus) {
        this.stats.aiTotal = modelsStatus.total_models || 0;
        this.stats.aiActive = modelsStatus.loaded_models || 0;
      }
      
      if (systemMetrics) {
        this.stats.serverLoad = Math.min(100, Math.round((systemMetrics.cpu_percent || 0)));
        this.stats.dbUsage = Math.min(100, Math.round((systemMetrics.memory_percent || 0)));
      }
      
      if (apiStatus) {
        this.stats.serverRequests = apiStatus.online || 0;
      }
      
      this.updateUI();
      this.addActivity({
        title: 'System data updated',
        desc: 'Real-time data fetched successfully',
        icon: 'download'
      });
      
    } catch (error) {
      console.error('[SystemMonitorReal] Error fetching data:', error);
      this.addActivity({
        title: 'Data fetch failed',
        desc: error.message || 'Unknown error',
        icon: 'alert'
      });
    }
  }
  
  async fetchSourceHealth() {
    /**
     * Fetch source health data from backend
     */
    try {
      const response = await fetch(this.endpoints.sourceHealth);
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data.success ? data : null;
    } catch (error) {
      console.error('[SystemMonitorReal] Source health fetch failed:', error);
      return null;
    }
  }
  
  async fetchSystemMetrics() {
    /**
     * Fetch system metrics from backend
     */
    try {
      const response = await fetch(this.endpoints.systemMetrics);
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data.metrics || null;
    } catch (error) {
      console.error('[SystemMonitorReal] System metrics fetch failed:', error);
      return null;
    }
  }
  
  async fetchModelsStatus() {
    /**
     * Fetch AI models status from backend
     */
    try {
      const response = await fetch(this.endpoints.modelsStatus);
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('[SystemMonitorReal] Models status fetch failed:', error);
      return null;
    }
  }
  
  async fetchAPIStatus() {
    /**
     * Fetch API status from backend
     */
    try {
      const response = await fetch(this.endpoints.apiStatus);
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('[SystemMonitorReal] API status fetch failed:', error);
      return null;
    }
  }
  
  setupCanvas() {
    const resizeCanvas = () => {
      const rect = this.canvas.getBoundingClientRect();
      this.canvas.width = rect.width;
      this.canvas.height = rect.height;
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
  }
  
  createNetworkNodes() {
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    
    // Central server node
    this.serverNode = {
      x: centerX,
      y: centerY,
      radius: 50,
      label: 'API Server',
      type: 'server',
      color: '#22c55e',
      connections: []
    };
    
    // Database node
    this.dbNode = {
      x: centerX + 250,
      y: centerY,
      radius: 40,
      label: 'Database',
      type: 'database',
      color: '#3b82f6',
      connections: [this.serverNode]
    };
    
    // Client nodes (circle around server)
    this.clientNodes = [];
    const numClients = 6;
    const clientRadius = 220;
    
    for (let i = 0; i < numClients; i++) {
      const angle = (Math.PI * 2 * i) / numClients;
      this.clientNodes.push({
        x: centerX + Math.cos(angle) * clientRadius,
        y: centerY + Math.sin(angle) * clientRadius,
        radius: 30,
        label: `Client ${i + 1}`,
        type: 'client',
        color: '#8b5cf6',
        connections: [this.serverNode]
      });
    }
    
    // Data source nodes
    this.sourceNodes = [];
    const numSources = 8;
    const sourceRadius = 350;
    
    for (let i = 0; i < numSources; i++) {
      const angle = (Math.PI * 2 * i) / numSources - Math.PI / 2;
      this.sourceNodes.push({
        x: centerX + Math.cos(angle) * sourceRadius,
        y: centerY + Math.sin(angle) * sourceRadius,
        radius: 28,
        label: `Source ${i + 1}`,
        type: 'source',
        color: '#f59e0b',
        connections: [this.serverNode]
      });
    }
    
    // AI model nodes
    this.aiNodes = [];
    const numAI = 4;
    const aiSpacing = 80;
    const aiStartY = centerY - (aiSpacing * (numAI - 1)) / 2;
    
    for (let i = 0; i < numAI; i++) {
      this.aiNodes.push({
        x: 100,
        y: aiStartY + i * aiSpacing,
        radius: 25,
        label: `AI Model ${i + 1}`,
        type: 'ai',
        color: '#ec4899',
        connections: [this.serverNode]
      });
    }
    
    this.nodes = [
      this.serverNode,
      this.dbNode,
      ...this.clientNodes,
      ...this.sourceNodes,
      ...this.aiNodes
    ];
  }
  
  startAnimation() {
    const animate = () => {
      this.time += 0.016;
      this.update();
      this.draw();
      requestAnimationFrame(animate);
    };
    animate();
    
    // Generate packets periodically (based on real request activity)
    setInterval(() => {
      const requestRate = this.stats.serverRequests || 50;
      // More requests = more packets
      const numPackets = Math.ceil(requestRate / 50);
      for (let i = 0; i < numPackets; i++) {
        this.generateRandomPacket();
      }
    }, 2000);
  }
  
  update() {
    // Update packets
    this.packets.forEach(packet => {
      packet.progress += packet.speed;
      
      const easeProgress = this.easeInOutQuad(Math.min(packet.progress, 1));
      packet.x = packet.from.x + (packet.to.x - packet.from.x) * easeProgress;
      packet.y = packet.from.y + (packet.to.y - packet.from.y) * easeProgress;
      
      // Add trail
      if (packet.progress < 1) {
        packet.trail.push({ x: packet.x, y: packet.y });
        if (packet.trail.length > 15) {
          packet.trail.shift();
        }
      }
      
      // Create particle effect on arrival
      if (packet.progress >= 1 && !packet.completed) {
        this.createParticleEffect(packet.to.x, packet.to.y, packet.color);
        packet.completed = true;
      }
    });
    
    // Remove completed packets
    this.packets = this.packets.filter(p => p.progress < 1.5);
    
    // Update particles
    this.particles.forEach(particle => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      particle.life -= 0.02;
      particle.vx *= 0.95;
      particle.vy *= 0.95;
    });
    
    this.particles = this.particles.filter(p => p.life > 0);
  }
  
  draw() {
    if (!this.ctx) return;
    
    // Clear with gradient background
    const gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
    gradient.addColorStop(0, '#020617');
    gradient.addColorStop(1, '#0f172a');
    this.ctx.fillStyle = gradient;
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // Draw grid
    this.drawGrid();
    
    // Draw connections
    this.nodes.forEach(node => {
      if (node.connections) {
        node.connections.forEach(target => {
          this.drawConnection(node, target);
        });
      }
    });
    
    // Draw packet trails
    this.packets.forEach(packet => {
      if (packet.trail.length > 1) {
        this.drawTrail(packet.trail, packet.color);
      }
    });
    
    // Draw packets
    this.packets.forEach(packet => {
      this.drawPacket(packet);
    });
    
    // Draw particles
    this.particles.forEach(particle => {
      this.drawParticle(particle);
    });
    
    // Draw nodes
    this.nodes.forEach(node => {
      this.drawNode(node);
    });
  }
  
  drawGrid() {
    this.ctx.strokeStyle = 'rgba(148, 163, 184, 0.05)';
    this.ctx.lineWidth = 1;
    
    const gridSize = 40;
    
    for (let x = 0; x < this.canvas.width; x += gridSize) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.canvas.height);
      this.ctx.stroke();
    }
    
    for (let y = 0; y < this.canvas.height; y += gridSize) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.canvas.width, y);
      this.ctx.stroke();
    }
  }
  
  drawConnection(from, to) {
    const dashOffset = -this.time * 20;
    
    this.ctx.strokeStyle = 'rgba(34, 197, 94, 0.2)';
    this.ctx.lineWidth = 2;
    this.ctx.setLineDash([10, 5]);
    this.ctx.lineDashOffset = dashOffset;
    
    this.ctx.beginPath();
    this.ctx.moveTo(from.x, from.y);
    this.ctx.lineTo(to.x, to.y);
    this.ctx.stroke();
    
    this.ctx.setLineDash([]);
  }
  
  drawNode(node) {
    // Glow effect
    const pulseScale = 1 + Math.sin(this.time * 2) * 0.1;
    const glowRadius = node.radius * 2.5 * pulseScale;
    
    const gradient = this.ctx.createRadialGradient(
      node.x, node.y, 0,
      node.x, node.y, glowRadius
    );
    gradient.addColorStop(0, node.color + '60');
    gradient.addColorStop(0.5, node.color + '20');
    gradient.addColorStop(1, 'transparent');
    
    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(node.x, node.y, glowRadius, 0, Math.PI * 2);
    this.ctx.fill();
    
    // Node circle
    this.ctx.fillStyle = '#1e293b';
    this.ctx.beginPath();
    this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
    this.ctx.fill();
    
    // Node border
    const borderGradient = this.ctx.createLinearGradient(
      node.x - node.radius, node.y - node.radius,
      node.x + node.radius, node.y + node.radius
    );
    borderGradient.addColorStop(0, node.color);
    borderGradient.addColorStop(1, node.color + '80');
    
    this.ctx.strokeStyle = borderGradient;
    this.ctx.lineWidth = 3;
    this.ctx.stroke();
    
    // Node icon
    this.drawNodeIcon(node);
    
    // Node label
    this.ctx.fillStyle = '#f1f5f9';
    this.ctx.font = 'bold 11px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.fillText(node.label, node.x, node.y + node.radius + 20);
    
    // Status indicator
    this.ctx.fillStyle = node.color;
    this.ctx.beginPath();
    this.ctx.arc(node.x + node.radius - 8, node.y - node.radius + 8, 5, 0, Math.PI * 2);
    this.ctx.fill();
  }
  
  drawNodeIcon(node) {
    const iconSize = node.radius * 0.6;
    this.ctx.strokeStyle = node.color;
    this.ctx.fillStyle = node.color;
    this.ctx.lineWidth = 2;
    
    switch (node.type) {
      case 'server':
        for (let i = 0; i < 3; i++) {
          const y = node.y - iconSize/2 + i * (iconSize/2);
          this.ctx.strokeRect(node.x - iconSize/2, y, iconSize, iconSize/4);
        }
        break;
      case 'database':
        this.ctx.beginPath();
        this.ctx.ellipse(node.x, node.y - iconSize/3, iconSize/2, iconSize/6, 0, 0, Math.PI * 2);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.moveTo(node.x - iconSize/2, node.y - iconSize/3);
        this.ctx.lineTo(node.x - iconSize/2, node.y + iconSize/3);
        this.ctx.moveTo(node.x + iconSize/2, node.y - iconSize/3);
        this.ctx.lineTo(node.x + iconSize/2, node.y + iconSize/3);
        this.ctx.stroke();
        this.ctx.beginPath();
        this.ctx.ellipse(node.x, node.y + iconSize/3, iconSize/2, iconSize/6, 0, 0, Math.PI * 2);
        this.ctx.stroke();
        break;
      case 'client':
        this.ctx.strokeRect(node.x - iconSize/2, node.y - iconSize/2, iconSize, iconSize * 0.7);
        this.ctx.beginPath();
        this.ctx.moveTo(node.x - iconSize/4, node.y + iconSize/2);
        this.ctx.lineTo(node.x + iconSize/4, node.y + iconSize/2);
        this.ctx.stroke();
        break;
      case 'source':
        this.ctx.beginPath();
        this.ctx.arc(node.x, node.y, iconSize/4, 0, Math.PI * 2);
        this.ctx.fill();
        [iconSize/2, iconSize * 0.75].forEach(r => {
          this.ctx.beginPath();
          this.ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
          this.ctx.stroke();
        });
        break;
      case 'ai':
        const nodeSize = 3;
        const positions = [
          { x: -iconSize/3, y: -iconSize/4 },
          { x: -iconSize/3, y: iconSize/4 },
          { x: 0, y: -iconSize/3 },
          { x: 0, y: 0 },
          { x: 0, y: iconSize/3 },
          { x: iconSize/3, y: -iconSize/4 },
          { x: iconSize/3, y: iconSize/4 }
        ];
        positions.forEach(pos => {
          this.ctx.beginPath();
          this.ctx.arc(node.x + pos.x, node.y + pos.y, nodeSize, 0, Math.PI * 2);
          this.ctx.fill();
        });
        break;
    }
  }
  
  drawTrail(trail, color) {
    if (trail.length < 2) return;
    
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 2;
    this.ctx.globalAlpha = 0.3;
    
    this.ctx.beginPath();
    this.ctx.moveTo(trail[0].x, trail[0].y);
    
    for (let i = 1; i < trail.length; i++) {
      this.ctx.lineTo(trail[i].x, trail[i].y);
    }
    
    this.ctx.stroke();
    this.ctx.globalAlpha = 1;
  }
  
  drawPacket(packet) {
    if (packet.progress >= 1) return;
    
    const pulseScale = 1 + Math.sin(this.time * 5 + packet.progress * 10) * 0.3;
    const glowRadius = packet.size * 4 * pulseScale;
    
    const gradient = this.ctx.createRadialGradient(
      packet.x, packet.y, 0,
      packet.x, packet.y, glowRadius
    );
    gradient.addColorStop(0, packet.color);
    gradient.addColorStop(0.5, packet.color + '40');
    gradient.addColorStop(1, 'transparent');
    
    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(packet.x, packet.y, glowRadius, 0, Math.PI * 2);
    this.ctx.fill();
    
    this.ctx.fillStyle = packet.color;
    this.ctx.beginPath();
    this.ctx.arc(packet.x, packet.y, packet.size, 0, Math.PI * 2);
    this.ctx.fill();
    
    this.ctx.strokeStyle = '#ffffff';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();
  }
  
  drawParticle(particle) {
    this.ctx.globalAlpha = particle.life;
    this.ctx.fillStyle = particle.color;
    this.ctx.beginPath();
    this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.globalAlpha = 1;
  }
  
  createParticleEffect(x, y, color) {
    const numParticles = 12;
    for (let i = 0; i < numParticles; i++) {
      const angle = (Math.PI * 2 * i) / numParticles;
      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * 2,
        vy: Math.sin(angle) * 2,
        life: 1,
        color,
        size: 3
      });
    }
  }
  
  generateRandomPacket() {
    const types = [
      { from: this.clientNodes, to: this.serverNode, color: '#8b5cf6' },
      { from: [this.serverNode], to: this.dbNode, color: '#3b82f6' },
      { from: [this.serverNode], to: this.sourceNodes, color: '#f59e0b' },
      { from: [this.serverNode], to: this.aiNodes, color: '#ec4899' }
    ];
    
    const type = types[Math.floor(Math.random() * types.length)];
    const fromArray = Array.isArray(type.from) ? type.from : [type.from];
    const toArray = Array.isArray(type.to) ? type.to : [type.to];
    
    const from = fromArray[Math.floor(Math.random() * fromArray.length)];
    const to = toArray[Math.floor(Math.random() * toArray.length)];
    
    this.packets.push({
      from,
      to,
      x: from.x,
      y: from.y,
      progress: 0,
      speed: 0.01 + Math.random() * 0.01,
      color: type.color,
      size: 6,
      trail: [],
      completed: false
    });
  }
  
  easeInOutQuad(t) {
    return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }
  
  startDataUpdates() {
    // Update data from backend every 5 seconds
    setInterval(() => {
      this.fetchAllData();
    }, 5000);
    
    // Update time
    setInterval(() => {
      this.updateLastUpdate();
    }, 1000);
  }
  
  updateUI() {
    // Server stats
    this.animateNumber('server-requests', this.stats.serverRequests);
    this.animateProgress('server-load', this.stats.serverLoad);
    document.getElementById('server-load-text').textContent = this.stats.serverLoad + '%';
    
    // Database stats
    this.animateNumber('db-size', this.stats.dbSize);
    this.animateProgress('db-usage', this.stats.dbUsage);
    this.animateNumber('db-queries', this.stats.dbQueries);
    
    // AI stats
    this.animateNumber('ai-total', this.stats.aiTotal);
    this.animateNumber('ai-active', this.stats.aiActive);
    
    // Sources stats
    this.animateNumber('sources-total', this.stats.sourcesTotal);
    this.animateNumber('sources-active', this.stats.sourcesActive);
    this.animateNumber('sources-healthy', this.stats.sourcesHealthy);
    this.animateNumber('sources-degraded', this.stats.sourcesDegraded);
    this.animateNumber('sources-offline', this.stats.sourcesOffline);
    
    // Network stats
    document.getElementById('packets-count').textContent = this.packets.length;
    document.getElementById('clients-count').textContent = this.clientNodes.length;
  }
  
  animateNumber(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    
    const current = parseInt(el.textContent) || 0;
    const diff = target - current;
    const steps = 20;
    const stepSize = diff / steps;
    
    let step = 0;
    const interval = setInterval(() => {
      if (step >= steps) {
        el.textContent = target;
        clearInterval(interval);
        return;
      }
      
      el.textContent = Math.round(current + stepSize * step);
      step++;
    }, 30);
  }
  
  animateProgress(id, percent) {
    const el = document.getElementById(id);
    if (!el) return;
    
    el.style.width = percent + '%';
  }
  
  animateStats() {
    document.querySelectorAll('[data-animate]').forEach(el => {
      el.style.opacity = '0';
      setTimeout(() => {
        el.style.opacity = '1';
      }, parseInt(el.getAttribute('data-delay') || 0));
    });
  }
  
  updateLastUpdate() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US');
    document.getElementById('last-update').textContent = timeString;
  }
  
  addActivity(activity) {
    const activityLog = document.getElementById('activity-log');
    if (!activityLog) return;
    
    const item = document.createElement('div');
    item.className = 'activity-item';
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US');
    
    item.innerHTML = `
      <div class="activity-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
          ${this.getActivityIcon(activity.icon)}
        </svg>
      </div>
      <div class="activity-content">
        <div class="activity-title">${activity.title}</div>
        <div class="activity-desc">${activity.desc}</div>
      </div>
      <div class="activity-time">${timeString}</div>
    `;
    
    activityLog.insertBefore(item, activityLog.firstChild);
    
    while (activityLog.children.length > this.maxActivities) {
      activityLog.removeChild(activityLog.lastChild);
    }
  }
  
  getActivityIcon(type) {
    const icons = {
      'arrow-right': '<path d="M5 12h14"/><path d="M12 5l7 7-7 7"/>',
      'database': '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>',
      'cpu': '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3"/><path d="M15 1v3"/><path d="M9 20v3"/><path d="M15 20v3"/><path d="M20 9h3"/><path d="M20 14h3"/><path d="M1 9h3"/><path d="M1 14h3"/>',
      'download': '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
      'users': '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
      'alert': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'
    };
    return icons[type] || icons['arrow-right'];
  }
  
  setupEventListeners() {
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.fetchAllData();
        this.addActivity({
          title: 'System refreshed',
          desc: 'Manual refresh triggered',
          icon: 'download'
        });
      });
    }
    
    const clearBtn = document.getElementById('clear-log');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        const activityLog = document.getElementById('activity-log');
        if (activityLog) {
          activityLog.innerHTML = '';
        }
      });
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new SystemMonitorReal();
  });
} else {
  new SystemMonitorReal();
}
