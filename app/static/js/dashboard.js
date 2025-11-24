class ElephantDashboard {
    constructor() {
        this.map = null;
        this.detectionMarkers = [];
        this.cameraMarkers = [];
        this.isDemoMode = false;
        this.demoInterval = null;
        
        this.init();
    }

    init() {
        this.initMap();
        this.loadMapData();
        this.setupEventListeners();
        
        // Auto-refresh every 30 seconds
        setInterval(() => this.loadMapData(), 30000);
    }

    initMap() {
        // Initialize Leaflet map centered on Kenya
        this.map = L.map('map').setView([-1.9441, 30.0619], 12);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: ' OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
    }

    async loadMapData() {
        try {
            console.log('Fetching map data...');
            const response = await fetch('/map-data');
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Received data:', data);

            if (data.status === 'success') {
                console.log('Updating map with', data.detections?.length || 0, 'detections and', data.cameras?.length || 0, 'cameras');
                this.updateMap(data.detections || [], data.cameras || []);
                this.updateSidebar(data.detections || []);
                this.updateStats(data.detections || []);
            } else {
                console.error('Error in response:', data.message || 'Unknown error');
            }
        } catch (error) {
            console.error('Error loading map data:', error);
        }
    }

    updateMap(detections, cameras) {
        // Clear existing markers
        this.detectionMarkers.forEach(marker => this.map.removeLayer(marker));
        this.detectionMarkers = [];

        // Add camera markers
        cameras.forEach(camera => {
            const marker = L.marker([camera.location.lat, camera.location.lng])
                .bindPopup(`
                    <div class="camera-popup">
                        <h4>📷 ${camera.name}</h4>
                        <p><strong>ID:</strong> ${camera.camera_id}</p>
                        <p><strong>Status:</strong> ${camera.is_active ? '🟢 Active' : '🔴 Inactive'}</p>
                    </div>
                `)
                .addTo(this.map);
            this.cameraMarkers.push(marker);
        });

        // Add detection markers
        const redIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });

        detections.forEach(detection => {
            const confidencePercent = (detection.confidence * 100).toFixed(1);
            const timestamp = new Date(detection.timestamp).toLocaleString();
            
            const marker = L.marker([detection.location.lat, detection.location.lng], {
                icon: redIcon
            })
            .bindPopup(`
                <div class="detection-popup">
                    <h4> Elephant Detected!</h4>
                    <p><strong>Camera:</strong> ${detection.camera_id}</p>
                    <p><strong>Confidence:</strong> ${confidencePercent}%</p>
                    <p><strong>Time:</strong> ${timestamp}</p>
                    ${detection.image_path ? `<p><strong>Image:</strong> Available</p>` : ''}
                </div>
            `)
            .addTo(this.map);
            
            this.detectionMarkers.push(marker);
        });
    }

    updateSidebar(detections) {
        const alertsContainer = document.getElementById('alerts');
        const recentDetections = detections.slice(0, 10); // Show last 10
        
        if (recentDetections.length === 0) {
            alertsContainer.innerHTML = '<div class="loading">No recent detections</div>';
            return;
        }

        alertsContainer.innerHTML = recentDetections.map(detection => {
            const confidencePercent = (detection.confidence * 100).toFixed(1);
            const timestamp = new Date(detection.timestamp).toLocaleString();
            const isRecent = this.isRecentDetection(detection.timestamp);
            
            return `
                <div class="alert-panel ${isRecent ? 'recent' : ''}">
                    <strong>🐘 Elephant Detected</strong><br>
                    <strong>Camera:</strong> ${detection.camera_id}<br>
                    <strong>Confidence:</strong> ${confidencePercent}%<br>
                    <strong>Time:</strong> ${timestamp}<br>
                    <small>Location: ${detection.location.lat.toFixed(4)}, ${detection.location.lng.toFixed(4)}</small>
                </div>
            `;
        }).join('');
    }

    updateStats(detections) {
        const statsContainer = document.getElementById('stats');
        const recentDetections = detections.filter(d => this.isRecentDetection(d.timestamp));
        const uniqueCameras = new Set(detections.map(d => d.camera_id));
        
        statsContainer.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${detections.length}</div>
                <div class="stat-label">Total Detections</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${recentDetections.length}</div>
                <div class="stat-label">Last 24h</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${uniqueCameras.size}</div>
                <div class="stat-label">Active Cameras</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${this.isDemoMode ? 'ON' : 'OFF'}</div>
                <div class="stat-label">Demo Mode</div>
            </div>
        `;
    }

    isRecentDetection(timestamp) {
        const detectionTime = new Date(timestamp);
        const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
        return detectionTime > twentyFourHoursAgo;
    }

    setupEventListeners() {
        // Simulate detection button
        document.getElementById('simulateDetection').addEventListener('click', () => {
            this.simulateDetection();
        });

        // Demo mode toggle
        document.getElementById('toggleDemo').addEventListener('click', () => {
            this.toggleDemoMode();
        });

        // Refresh button
        document.getElementById('refreshData').addEventListener('click', () => {
            this.loadMapData();
        });
    }

    async simulateDetection() {
        try {
            const cameras = [
                {id: 'cam_001', lat: -1.9441, lng: 30.0619},
                {id: 'cam_002', lat: -1.9500, lng: 30.0700},
                {id: 'cam_003', lat: -1.9300, lng: 30.0500}
            ];
            
            const camera = cameras[Math.floor(Math.random() * cameras.length)];
            
            const detectionData = {
                species: 'elephant',
                confidence: Math.round((0.7 + Math.random() * 0.3) * 100) / 100,
                camera_id: camera.id,
                location: {
                    lat: camera.lat + (Math.random() - 0.5) * 0.01,
                    lng: camera.lng + (Math.random() - 0.5) * 0.01
                },
                image_path: `/static/images/detection_${Math.floor(Math.random() * 3) + 1}.jpg`
            };

            const response = await fetch('/api/alert', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(detectionData)
            });

            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification('Detection simulated successfully!', 'success');
                this.loadMapData(); // Refresh data
            } else {
                this.showNotification(result.message, 'error');
            }
        } catch (error) {
            console.error('Error simulating detection:', error);
            this.showNotification('Error simulating detection', 'error');
        }
    }

    toggleDemoMode() {
        this.isDemoMode = !this.isDemoMode;
        const button = document.getElementById('toggleDemo');
        
        if (this.isDemoMode) {
            button.textContent = 'Stop Demo Mode';
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');
            this.startDemoMode();
        } else {
            button.textContent = 'Start Demo Mode';
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
            this.stopDemoMode();
        }
    }

    startDemoMode() {
        // Simulate detections every 15-45 seconds
        this.demoInterval = setInterval(() => {
            if (Math.random() > 0.3) { // 70% chance to simulate detection
                this.simulateDetection();
            }
        }, 15000 + Math.random() * 30000);
    }

    stopDemoMode() {
        if (this.demoInterval) {
            clearInterval(this.demoInterval);
            this.demoInterval = null;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ElephantDashboard();
});