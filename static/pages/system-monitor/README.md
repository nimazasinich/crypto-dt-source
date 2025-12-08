# System Monitor - Enhanced Animated Visualization

## Overview

The System Monitor provides a beautiful, real-time animated visualization of your entire system architecture. It's like looking at your system from above with a bird's-eye view, showing all components and data flow between them.

## Features

### 🎨 Visual Components

1. **API Server (Center)** - The main FastAPI server
   - Green pulsing glow when healthy
   - Central hub for all communications
   - Server icon with status indicator

2. **Database (Right)** - SQLite database
   - Blue when online, red when offline
   - Shows data persistence operations
   - Database cylinder icon

3. **Clients (Bottom)** - Multiple client connections
   - Purple nodes representing different clients
   - Monitor icons showing active connections
   - Receives final responses

4. **Data Sources (Top Arc)** - External API sources
   - Orange/yellow nodes in an arc formation
   - Radio wave icons for data sources
   - Shows active/inactive status

5. **AI Models (Left Side)** - Machine learning models
   - Pink nodes for AI/ML models
   - Neural network icons
   - Status indicators for model health

### 🌊 Animated Data Flow

The system shows complete request/response cycles with beautiful animations:

1. **Request Phase (Purple)** 
   - Client → Server
   - Arrow indicator on packet

2. **Processing Phase (Cyan)**
   - Server → Data Source/AI Model/Database
   - Shows where data is being fetched

3. **Response Phase (Green)**
   - Data Source/AI Model/Database → Server
   - Checkmark indicator on packet

4. **Final Response (Bright Green)**
   - Server → Client
   - Particle explosion effect on arrival

### ✨ Visual Effects

- **Pulsing Glows** - All nodes have animated glowing effects
- **Animated Connections** - Dashed lines flow between active nodes
- **Packet Trails** - Data packets leave glowing trails
- **Particle Effects** - Burst animations when packets arrive
- **Grid Background** - Subtle grid pattern for depth
- **Gradient Backgrounds** - Beautiful dark theme with gradients

### 📊 Real-Time Stats

**Top-Left Legend:**
- Request (Purple)
- Processing (Cyan)
- Response (Green)

**Top-Right Stats Panel:**
- Active Packets count
- Data Sources count
- AI Models count
- Connected Clients count

### 🔄 Data Updates

The monitor updates via two methods:

1. **WebSocket** - Real-time updates every 2 seconds
2. **HTTP Polling** - Fallback polling every 5 seconds

### 🎯 Status Indicators

Each node shows its status:
- **Green dot** - Online/Healthy
- **Red dot** - Offline/Failed
- **Pulsing glow** - Active processing

## Technical Details

### Canvas Size
- Default: 700px height
- Responsive: Adjusts for different screen sizes
- Dark theme with gradient background

### Animation System
- 60 FPS smooth animations
- Easing functions for natural movement
- Trail effects with fade-out
- Particle system for visual feedback

### Node Layout
- **Server**: Center (x: 50%, y: 50%)
- **Database**: Right of server (+200px)
- **Clients**: Bottom row (3 clients, 150px spacing)
- **Sources**: Top arc (250px radius)
- **AI Models**: Left column (80px spacing)

### Packet Flow Logic

```
Client Request
    ↓
API Server
    ↓
[Data Source / AI Model / Database]
    ↓
API Server
    ↓
Client Response (with particle effect)
```

### Demo Mode

When no real requests are active, the system generates demo packets every 3 seconds to showcase the animation system:
- `/api/market/price`
- `/api/models/sentiment`
- `/api/service/rate`
- `/api/monitoring/status`
- `/api/database/query`

## API Integration

### Endpoints Used

- `GET /api/monitoring/status` - System status
- `WS /api/monitoring/ws` - Real-time WebSocket
- `GET /api/monitoring/sources/detailed` - Source details
- `GET /api/monitoring/requests/recent` - Recent requests

### Data Structure

```javascript
{
  database: { online: true },
  ai_models: {
    total: 10,
    available: 8,
    failed: 2,
    models: [...]
  },
  data_sources: {
    total: 15,
    active: 12,
    pools: 3,
    sources: [...]
  },
  recent_requests: [...],
  stats: {
    active_sources: 12,
    requests_last_minute: 45,
    requests_last_hour: 2500
  }
}
```

## Customization

### Colors

You can customize colors in the code:

```javascript
// Node colors
server: '#22c55e'    // Green
database: '#3b82f6'  // Blue
client: '#8b5cf6'    // Purple
source: '#f59e0b'    // Orange
aiModel: '#ec4899'   // Pink

// Packet colors
request: '#8b5cf6'      // Purple
processing: '#22d3ee'   // Cyan
response: '#22c55e'     // Green
final: '#10b981'        // Bright Green
```

### Canvas Size

Adjust in CSS:

```css
.network-canvas-container {
  height: 700px; /* Change this value */
}
```

### Animation Speed

Adjust packet speed:

```javascript
speed: 0.015  // Lower = slower, Higher = faster
```

### Demo Packet Frequency

```javascript
setInterval(() => {
  this.createPacket({ endpoint: randomEndpoint });
}, 3000); // Change interval (milliseconds)
```

## Browser Compatibility

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ✅ Opera

Requires HTML5 Canvas support.

## Performance

- Optimized for 60 FPS
- Automatic cleanup of old packets
- Efficient canvas rendering
- Pauses updates when tab is hidden

## Troubleshooting

### Canvas not showing
- Check browser console for errors
- Ensure canvas element exists in DOM
- Verify JavaScript is enabled

### No animations
- Check WebSocket connection status
- Verify API endpoints are accessible
- Look for rate limiting (429 errors)

### Slow performance
- Reduce canvas size
- Decrease packet generation frequency
- Close other browser tabs

## Future Enhancements

- [ ] Click on nodes to see details
- [ ] Zoom and pan controls
- [ ] Export visualization as image
- [ ] Custom color themes
- [ ] Sound effects for packets
- [ ] 3D visualization mode
- [ ] Historical playback
- [ ] Alert animations for errors

## Credits

Built with ❤️ using:
- HTML5 Canvas API
- WebSocket API
- FastAPI backend
- Modern JavaScript (ES6+)

---

**Version**: 2.0  
**Last Updated**: 2025-12-08  
**Author**: Crypto Monitor Team
