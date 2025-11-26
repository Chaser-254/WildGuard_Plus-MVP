class ElephantDashboard {
    constructor() {
        this.map = null;
        this.detectionMarkers = [];
        this.cameraMarkers = [];
        this.isDemoMode = false;
        this.demoInterval = null;

        // Route related properties
        this.routeControl = null;
        this.routeLayer = null;
        this.bufferLayer = null;
        this.routeStartMarker = null;
        this.routeEndMarker = null;
        this.roadStats = null;
        this.roadLengthChart = null;
        this.distributionChart = null;

        // Custom icons
        this.icons = {
            camera: this.createCameraIcon(),
            detection: this.createDetectionIcon(),
            start: this.createStartIcon(),
            end: this.createEndIcon()
        };

        this.init();
    }

    // Custom icon creation methods
    createCameraIcon() {
        return L.divIcon({
            className: 'camera-marker',
            html: '📷',
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            popupAnchor: [0, -15]
        });
    }

    createDetectionIcon() {
        return L.divIcon({
            className: 'detection-marker',
            html: '🐘',
            iconSize: [35, 35],
            iconAnchor: [17, 17],
            popupAnchor: [0, -17]
        });
    }

    createStartIcon() {
        return L.divIcon({
            className: 'route-start-marker',
            html: '📍<div style="font-size: 10px; color: white; background: #10b981; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; position: absolute; top: -5px; right: -5px;">A</div>',
            iconSize: [25, 25],
            iconAnchor: [12, 12],
            popupAnchor: [0, -12]
        });
    }

    createEndIcon() {
        return L.divIcon({
            className: 'route-end-marker',
            html: '📍<div style="font-size: 10px; color: white; background: #ef4444; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; position: absolute; top: -5px; right: -5px;">B</div>',
            iconSize: [25, 25],
            iconAnchor: [12, 12],
            popupAnchor: [0, -12]
        });
    }

    init() {
        this.initMap();
        this.loadMapData();
        this.setupEventListeners();

        // Initialize buffer value display
        const bufferValueEl = document.getElementById('bufferValue');
        const bufferInputEl = document.getElementById('bufferRadius');
        if (bufferValueEl && bufferInputEl) {
            bufferValueEl.textContent = `${parseInt(bufferInputEl.value || 1000)}m`;
        }

        // Auto-refresh every 30 seconds
        setInterval(() => this.loadMapData(), 30000);
    }

    initMap() {
        // Initialize Leaflet map centered on Taita Taveta County
        // Coordinates for Taita Taveta County center (approximately Voi town)
        this.map = L.map('map').setView([-3.3962, 38.5569], 10);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);

        // Add a marker for Taita Taveta County
        L.marker([-3.395565, 37.676113])
            .addTo(this.map)
            .bindPopup('<b>Taita Taveta County</b><br>KRCS Taveta Office')
            .openPopup();

        // // Add approximate boundary for Taita Taveta County (simplified)
        // const taitaBoundary = L.polygon([
        //     [-3.0, 38.2],   // Northwest
        //     [-3.0, 38.8],   // Northeast  
        //     [-3.8, 38.8],   // Southeast
        //     [-3.8, 38.2],   // Southwest
        //     [-3.0, 38.2]    // Close polygon
        // ], {
        //     color: '#2c5530',
        //     weight: 2,
        //     fillColor: '#2c5530',
        //     fillOpacity: 0.1,
        //     dashArray: '5, 5'
        // }).addTo(this.map).bindPopup('Taita Taveta County Boundary');

        // // Fit map to show the county boundary
        // this.map.fitBounds(taitaBoundary.getBounds());
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
        // Clear existing detection markers
        this.detectionMarkers.forEach(marker => this.map.removeLayer(marker));
        this.detectionMarkers = [];

        // Clear existing camera markers
        this.cameraMarkers.forEach(marker => this.map.removeLayer(marker));
        this.cameraMarkers = [];

        // Add camera markers with custom icons - positioned in Taita Taveta County
        cameras.forEach(camera => {
            if (!camera.location) return;
            const marker = L.marker([camera.location.lat, camera.location.lng], {
                icon: this.icons.camera
            })
            .bindPopup(`
                <div class="camera-popup">
                    <h4>${camera.name}</h4>
                    <p><strong>ID:</strong> ${camera.camera_id}</p>
                    <p><strong>Status:</strong> ${camera.is_active ? '🟢 Active' : '🔴 Inactive'}</p>
                    <p><strong>Location:</strong> ${camera.location.lat.toFixed(4)}, ${camera.location.lng.toFixed(4)}</p>
                </div>
            `)
            .addTo(this.map);
            this.cameraMarkers.push(marker);
        });

        // Add detection markers with custom icons - positioned in Taita Taveta County
        detections.forEach(detection => {
            if (!detection.location) return;
            const confidencePercent = (detection.confidence * 100).toFixed(1);
            const timestamp = new Date(detection.timestamp).toLocaleString();

            const marker = L.marker([detection.location.lat, detection.location.lng], {
                icon: this.icons.detection
            })
            .bindPopup(`
                <div class="detection-popup">
                    <h4>Elephant Detected!</h4>
                    <p><strong>Camera:</strong> ${detection.camera_id}</p>
                    <p><strong>Confidence:</strong> ${confidencePercent}%</p>
                    <p><strong>Time:</strong> ${timestamp}</p>
                    <p><strong>Location:</strong> ${detection.location.lat.toFixed(4)}, ${detection.location.lng.toFixed(4)}</p>
                    ${detection.image_path ? `<p><strong>Image:</strong> Available</p>` : ''}
                </div>
            `)
            .addTo(this.map);

            this.detectionMarkers.push(marker);
        });
    }

    updateSidebar(detections) {
        const alertsContainer = document.getElementById('alerts');
        if (!alertsContainer) {
            console.warn('alerts container not found');
            return;
        }

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
                    <strong>Elephant Detected</strong><br>
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
        if (!statsContainer) return;
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
        // Helper to safely attach listeners
        const attach = (id, event, handler) => {
            const el = document.getElementById(id);
            if (!el) {
                console.warn(`Element #${id} not found for event ${event}`);
                return;
            }
            el.addEventListener(event, handler);
        };

        attach('simulateDetection', 'click', () => this.simulateDetection());
        attach('toggleDemo', 'click', () => this.toggleDemoMode());
        attach('refreshData', 'click', () => this.loadMapData());
        attach('findRoute', 'click', () => this.findRoute());
        attach('clearRoute', 'click', () => this.clearRoute());

        // Buffer radius slider
        const bufferEl = document.getElementById('bufferRadius');
        if (bufferEl) {
            bufferEl.addEventListener('input', (e) => {
                const value = parseInt(e.target.value) || 1000;
                const bufferValueEl = document.getElementById('bufferValue');
                if (bufferValueEl) bufferValueEl.textContent = `${value}m`;

                // Only update buffer if route exists
                if (this.routeLayer) {
                    this.updateBuffer(value);
                }
            });
        } else {
            console.warn('#bufferRadius not found; buffer slider will not work');
        }

        // Buffer color picker
        const bufferColorEl = document.getElementById('bufferColor');
        if (bufferColorEl) {
            bufferColorEl.addEventListener('input', (e) => {
                if (this.bufferLayer) {
                    this.updateBufferColor(e.target.value);
                }
            });
        }

        // Initialize map click for route points
        if (this.map) {
            this.map.on('click', (e) => {
                this.handleMapClick(e);
            });
        }

        // Initialize route controls on load
        this.initializeRouteControls();
    }

    async simulateDetection() {
        try {
            // Camera locations in Taita Taveta County
            const cameras = [
                {id: 'cam_001', lat: -3.3962, lng: 38.5569}, // Voi area
                {id: 'cam_002', lat: -3.4500, lng: 38.6000}, // Near Tsavo East
                {id: 'cam_003', lat: -3.3500, lng: 38.5000}, // Mwatate area
                {id: 'cam_004', lat: -3.5000, lng: 38.4000}, // Taveta area
                {id: 'cam_005', lat: -3.3000, lng: 38.6500}  // Near Tsavo West
            ];

            const camera = cameras[Math.floor(Math.random() * cameras.length)];

            const detectionData = {
                species: 'elephant',
                confidence: Math.round((0.7 + Math.random() * 0.3) * 100) / 100,
                camera_id: camera.id,
                location: {
                    lat: camera.lat + (Math.random() - 0.5) * 0.02, // Random offset within county
                    lng: camera.lng + (Math.random() - 0.5) * 0.02
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

        if (!button) return;

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

        // Update stats card (demo mode indicator)
        const statsEl = document.getElementById('stats');
        if (statsEl) {
            this.updateStats([]);
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

    // Route related methods
    initializeRouteControls() {
        try {
            // Check if Leaflet Routing is loaded
            if (typeof L === 'undefined' || typeof L.Routing === 'undefined') {
                console.error('Leaflet or Leaflet Routing Machine not loaded');
                this.showNotification('Error: Routing functionality not available', 'error');
                return;
            }

            // Initialize route control if not already done
            if (!this.routeControl) {
                this.routeControl = L.Routing.control({
                    waypoints: [],
                    routeWhileDragging: true,
                    show: false, // We'll handle the display ourselves
                    createMarker: () => null, // Don't create default markers
                    lineOptions: {
                        styles: [{color: '#3b82f6', opacity: 0.7, weight: 5}]
                    },
                    router: L.Routing.osrmv1({
                        serviceUrl: 'https://router.project-osrm.org/route/v1',
                        profile: 'driving'
                    })
                }).addTo(this.map);

                // Listen for route changes
                this.routeControl.on('routesfound', (e) => {
                    const routes = e.routes;
                    if (routes && routes[0]) {
                        this.displayRouteInfo(routes[0]);
                        this.analyzeRouteRoads(routes[0]);
                    }
                });

                // Error handling
                this.routeControl.on('routingerror', (e) => {
                    console.error('Routing error:', e.error);
                    this.showNotification('Error finding route: ' + (e.error && e.error.message ? e.error.message : 'Unknown error'), 'error');
                });
            }
        } catch (error) {
            console.error('Error initializing route controls:', error);
            this.showNotification('Error initializing routing: ' + error.message, 'error');
        }
    }

    // handle map clicks to fill start/end inputs and place markers
    handleMapClick(e) {
        try {
            const startInput = document.getElementById('startPoint');
            const endInput = document.getElementById('endPoint');
            if (!startInput || !endInput) return;

            const startPoint = startInput.value;
            const endPoint = endInput.value;

            if (!startPoint) {
                // Set start point
                startInput.value = `${e.latlng.lat.toFixed(6)}, ${e.latlng.lng.toFixed(6)}`;
                if (this.routeStartMarker) this.map.removeLayer(this.routeStartMarker);
                this.routeStartMarker = L.marker(e.latlng, {
                    icon: this.icons.start
                }).addTo(this.map);
            } else if (!endPoint) {
                // Set end point
                endInput.value = `${e.latlng.lat.toFixed(6)}, ${e.latlng.lng.toFixed(6)}`;
                if (this.routeEndMarker) this.map.removeLayer(this.routeEndMarker);
                this.routeEndMarker = L.marker(e.latlng, {
                    icon: this.icons.end
                }).addTo(this.map);
            }
        } catch (error) {
            console.error('Error handling map click:', error);
            this.showNotification('Error setting route point', 'error');
            return;
        }
    }

    async findRoute() {
        console.log('findRoute() called');
        // Get start/end either from inputs (lat,lng) or from markers
        const startInput = document.getElementById('startPoint');
        const endInput = document.getElementById('endPoint');
        if (!startInput || !endInput) {
            this.showNotification('Start or end input not found', 'error');
            return;
        }

        let startVal = startInput.value;
        let endVal = endInput.value;

        if (!startVal && this.routeStartMarker) {
            const latlng = this.routeStartMarker.getLatLng();
            startVal = `${latlng.lat}, ${latlng.lng}`;
            startInput.value = startVal;
        }

        if (!endVal && this.routeEndMarker) {
            const latlng = this.routeEndMarker.getLatLng();
            endVal = `${latlng.lat}, ${latlng.lng}`;
            endInput.value = endVal;
        }

        if (!startVal) {
            this.showNotification('Please set a start point', 'error');
            return;
        }
        if (!endVal) {
            this.showNotification('Please set an end point', 'error');
            return;
        }

        // Parse coordinates "lat, lng"
        const parseLatLng = (str) => {
            const parts = str.split(',').map(p => p.trim());
            if (parts.length < 2) return null;
            const lat = parseFloat(parts[0]);
            const lng = parseFloat(parts[1]);
            if (isNaN(lat) || isNaN(lng)) return null;
            return L.latLng(lat, lng);
        };

        const startLatLng = parseLatLng(startVal);
        const endLatLng = parseLatLng(endVal);

        if (!startLatLng || !endLatLng) {
            this.showNotification('Invalid coordinates. Use "lat, lng" format', 'error');
            return;
        }

        // Set waypoints on routeControl - this will trigger 'routesfound' event
        if (!this.routeControl) this.initializeRouteControls();
        if (this.routeControl) {
            this.routeControl.setWaypoints([startLatLng, endLatLng]);
        } else {
            this.showNotification('Routing control unavailable', 'error');
        }
    }

    displayRouteInfo(route) {
        try {
            // Clear existing route layer
            if (this.routeLayer) {
                this.map.removeLayer(this.routeLayer);
                this.routeLayer = null;
            }

            // Get coordinates from the route
            let coordinates = [];
            if (route.coordinates && route.coordinates.length > 0) {
                // Handle L.Routing.Machine coordinates (LatLng objects)
                coordinates = route.coordinates.map(coord => {
                    return Array.isArray(coord) ? 
                        L.latLng(coord[0], coord[1]) : 
                        L.latLng(coord.lat, coord.lng);
                });
            } else if (route.instructions && route.instructions.length > 0) {
                // Alternative: extract coordinates from instructions
                coordinates = this.extractCoordinatesFromInstructions(route.instructions);
            }

            if (coordinates.length === 0) {
                console.warn('No coordinates found in route');
                return;
            }

            // Create the route layer as a Polyline
            this.routeLayer = L.polyline(coordinates, {
                color: '#3b82f6',
                weight: 6,
                opacity: 0.8,
                lineJoin: 'round'
            }).addTo(this.map);

            // Fit map to show the route
            this.map.fitBounds(this.routeLayer.getBounds());

            // Fill distance/time
            const distanceMeters = route.summary?.totalDistance || route.distance || 0;
            const timeSeconds = route.summary?.totalTime || route.time || 0;

            const distanceKm = (distanceMeters / 1000).toFixed(2);
            const timeMin = timeSeconds ? Math.round(timeSeconds / 60) : '-';

            if (document.getElementById('totalDistance')) {
                document.getElementById('totalDistance').textContent = `${distanceKm} km`;
            }
            if (document.getElementById('estimatedTime')) {
                document.getElementById('estimatedTime').textContent = `${timeMin} min`;
            }

            // Update buffer using current slider value
            const bufferRadius = parseInt(document.getElementById('bufferRadius')?.value) || 1000;
            const bufferValueEl = document.getElementById('bufferValue');
            if (bufferValueEl) bufferValueEl.textContent = `${bufferRadius}m`;
            
            // Create initial buffer
            this.updateBuffer(bufferRadius);

        } catch (err) {
            console.error('Error displaying route info:', err);
            this.showNotification('Error displaying route: ' + err.message, 'error');
        }
    }

    // Helper method to extract coordinates from route instructions
    extractCoordinatesFromInstructions(instructions) {
        const coordinates = [];
        instructions.forEach(instruction => {
            if (instruction.coords && instruction.coords.length > 0) {
                instruction.coords.forEach(coord => {
                    coordinates.push(L.latLng(coord.lat, coord.lng));
                });
            }
        });
        return coordinates;
    }

    updateBuffer(radius) {
        try {
            if (!this.routeLayer) {
                console.log('No route layer found for buffer');
                return;
            }

            console.log('Updating buffer with radius:', radius, 'meters');

            // Remove existing buffer layer
            if (this.bufferLayer) {
                this.map.removeLayer(this.bufferLayer);
                this.bufferLayer = null;
            }

            // Get the route coordinates from the routeLayer
            const routeLatLngs = this.routeLayer.getLatLngs();
            if (!routeLatLngs || routeLatLngs.length === 0) {
                console.error('No coordinates found in route layer');
                return;
            }

            console.log('Route coordinates:', routeLatLngs.length, 'points');

            // Convert Leaflet LatLng objects to GeoJSON format [lng, lat]
            const coordinates = routeLatLngs.map(latlng => [latlng.lng, latlng.lat]);
            
            // Ensure we have valid coordinates
            if (coordinates.length < 2) {
                console.error('Not enough coordinates for buffer');
                return;
            }

            // Create a Turf.js line string
            const line = turf.lineString(coordinates);
            console.log('Created line string for buffer');

            // Convert meters to kilometers for Turf
            const radiusKm = radius / 1000;
            console.log('Creating buffer with radius:', radiusKm, 'km');

            // Create buffer around the route line
            const buffer = turf.buffer(line, radiusKm, { units: 'kilometers' });
            
            if (!buffer || !buffer.geometry) {
                console.error('Failed to create buffer geometry');
                return;
            }

            console.log('Buffer created successfully:', buffer);

            // Get the selected color
            const color = document.getElementById('bufferColor')?.value || '#f24e39';
            console.log('Using buffer color:', color);

            // Add buffer to map as a GeoJSON layer
            this.bufferLayer = L.geoJSON(buffer, {
                style: {
                    color: color,
                    weight: 2,
                    fillColor: color,
                    fillOpacity: 0.3,
                    opacity: 0.8
                },
                onEachFeature: function(feature, layer) {
                    // Add popup with buffer info
                    layer.bindPopup(`Buffer Zone: ${radius}m radius`);
                }
            }).addTo(this.map);

            console.log('Buffer layer added to map successfully');

            // Fit map to show both route and buffer
            const allLayers = [this.routeLayer, this.bufferLayer];
            const group = new L.featureGroup(allLayers);
            this.map.fitBounds(group.getBounds().pad(0.1));

        } catch (error) {
            console.error('Error in updateBuffer:', error);
            this.showNotification('Error updating buffer: ' + error.message, 'error');
        }
    }

    updateBufferColor(color) {
        try {
            if (!this.bufferLayer) {
                console.log('No buffer layer to update');
                return;
            }

            console.log('Updating buffer color to:', color);
            this.bufferLayer.setStyle({
                color: color,
                fillColor: color
            });

            // If we have a buffer radius set, update the buffer to apply the new color
            const radiusInput = document.getElementById('bufferRadius');
            if (radiusInput) {
                this.updateBuffer(parseInt(radiusInput.value) || 1000);
            }
        } catch (error) {
            console.error('Error updating buffer color:', error);
        }
    }

    async analyzeRouteRoads(route) {
        try {
            // Mock road data for demonstration
            this.roadStats = {
                totalRoads: 602,
                totalLength: 103.35, // km
                byType: [
                    {type: 'Residential', length: 60.5, count: 356},
                    {type: 'Secondary', length: 7.2, count: 42},
                    {type: 'Unclassified', length: 12.4, count: 72},
                    {type: 'Primary', length: 6.2, count: 36},
                    {type: 'Service', length: 5.6, count: 33},
                    {type: 'Tertiary', length: 4.8, count: 28},
                    {type: 'Path', length: 0.8, count: 5},
                    {type: 'Pedestrian', length: 0.4, count: 2},
                    {type: 'Track', length: 0.1, count: 1},
                    {type: 'Footway', length: 0.05, count: 1}
                ]
            };

            this.updateRoadCharts();

        } catch (error) {
            console.error('Error analyzing route roads:', error);
            this.showNotification('Error analyzing road data', 'error');
        }
    }

    updateRoadCharts() {
        if (!this.roadStats) return;

        const roadLengthCanvas = document.getElementById('roadLengthChart');
        const distributionCanvas = document.getElementById('distributionChart');
        if (!roadLengthCanvas || !distributionCanvas) {
            console.warn('Chart canvases not found, skipping chart update');
            return;
        }

        const ctx1 = roadLengthCanvas.getContext('2d');
        const ctx2 = distributionCanvas.getContext('2d');

        // Destroy existing charts if they exist
        if (this.roadLengthChart) this.roadLengthChart.destroy();
        if (this.distributionChart) this.distributionChart.destroy();

        // Sort by length for better visualization
        const sortedByLength = [...this.roadStats.byType].sort((a, b) => b.length - a.length);

        // Road Length by Type (Bar Chart)
        this.roadLengthChart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: sortedByLength.map(item => item.type),
                datasets: [{
                    label: 'Length (km)',
                    data: sortedByLength.map(item => item.length),
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Length (km)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const val = context.parsed && context.parsed.y != null ? context.parsed.y : context.raw;
                                return `${val.toFixed ? val.toFixed(2) : val} km`;
                            }
                        }
                    }
                }
            }
        });

        // Distribution by Type (Pie Chart)
        this.distributionChart = new Chart(ctx2, {
            type: 'pie',
            data: {
                labels: this.roadStats.byType.map(item => item.type),
                datasets: [{
                    data: this.roadStats.byType.map(item => item.count),
                    backgroundColor: [
                        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
                        '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#a855f7'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    clearRoute() {
        // Clear route layer
        if (this.routeLayer) {
            this.map.removeLayer(this.routeLayer);
            this.routeLayer = null;
        }

        // Clear buffer layer
        if (this.bufferLayer) {
            this.map.removeLayer(this.bufferLayer);
            this.bufferLayer = null;
        }

        // Clear markers
        if (this.routeStartMarker) {
            this.map.removeLayer(this.routeStartMarker);
            this.routeStartMarker = null;
        }

        if (this.routeEndMarker) {
            this.map.removeLayer(this.routeEndMarker);
            this.routeEndMarker = null;
        }

        // Clear input fields
        const startInput = document.getElementById('startPoint');
        const endInput = document.getElementById('endPoint');
        if (startInput) startInput.value = '';
        if (endInput) endInput.value = '';

        // Reset route control
        if (this.routeControl) {
            this.routeControl.setWaypoints([]);
        }

        // Reset stats
        if (document.getElementById('totalDistance')) document.getElementById('totalDistance').textContent = '-';
        if (document.getElementById('estimatedTime')) document.getElementById('estimatedTime').textContent = '-';
        if (document.getElementById('roadType')) document.getElementById('roadType').textContent = '-';

        // Clear charts
        if (this.roadLengthChart) {
            this.roadLengthChart.destroy();
            this.roadLengthChart = null;
        }

        if (this.distributionChart) {
            this.distributionChart.destroy();
            this.distributionChart = null;
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
            background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f6'};
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

// Add CSS animations and marker styles
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

    /* Custom marker styles */
    .camera-marker {
        background: rgba(51, 136, 255, 0.9);
        border: 3px solid white;
        border-radius: 50%;
        text-align: center;
        font-size: 16px;
        line-height: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .detection-marker {
        background: rgba(255, 68, 68, 0.9);
        border: 3px solid white;
        border-radius: 50%;
        text-align: center;
        font-size: 18px;
        line-height: 28px;
        box-shadow: 0 2px 10px rgba(255,0,0,0.5);
        animation: pulse 2s infinite;
    }

    .route-start-marker,
    .route-end-marker {
        text-align: center;
        font-size: 16px;
        line-height: 20px;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
`;
document.head.appendChild(style);

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new ElephantDashboard();
});