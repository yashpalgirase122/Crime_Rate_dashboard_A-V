document.addEventListener('DOMContentLoaded', async () => {
    const mapEl = document.getElementById('crimeMap');
    if (!mapEl) return;

    // Center map roughly on India
    const map = L.map('crimeMap').setView([20.5937, 78.9629], 5);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    try {
        const response = await fetch('/api/map_data');
        const points = await response.json();

        const heatArray = [];

        points.forEach(p => {
            heatArray.push([p.lat, p.lng, p.intensity]);
            
            let color = '#10b981'; // green
            if (p.risk === 'HIGH') color = '#ef4444'; // red
            else if (p.risk === 'MEDIUM') color = '#f59e0b'; // orange
            
            L.circleMarker([p.lat, p.lng], {
                radius: 4,
                fillColor: color,
                color: color,
                weight: 1,
                opacity: 0.8,
                fillOpacity: 0.5
            }).bindPopup(`<b>${p.city}</b><br>Risk: <span style="color:${color}">${p.risk}</span><br>Crime: ${p.crime}`).addTo(map);
        });

        if(typeof L.heatLayer !== 'undefined') {
            L.heatLayer(heatArray, {
                radius: 25,
                blur: 15,
                maxZoom: 10,
                gradient: {0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
            }).addTo(map);
        }

        const patrolRes = await fetch('/api/patrol_routes');
        const routes = await patrolRes.json();
        
        if(routes.length > 0) {
            routes.forEach((r, idx) => {
                L.marker([r.lat, r.lng], {
                    title: `Patrol Hub ${idx+1}`
                }).bindPopup(`<b>Optimal Patrol Hub ${idx+1}</b>`).addTo(map);
            });
            
            const latlngs = routes.map(r => [r.lat, r.lng]);
            latlngs.push([routes[0].lat, routes[0].lng]);
            L.polyline(latlngs, {color: '#3b82f6', dashArray: '5, 5', weight: 3}).addTo(map);
        }

    } catch(e) {
        console.error('Error loading map data', e);
    }
});
