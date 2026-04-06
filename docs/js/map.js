/**
 * FloodKH Map Module — Leaflet map with district polygons.
 */
const FloodMap = {
    map: null,
    districtLayers: {},
    data: null,
    geojsonLayer: null,

    init(data) {
        this.data = data;
        this.map = L.map('map-container', {
            center: [11.56, 104.92],
            zoom: 12,
            zoomControl: true,
            attributionControl: false
        });

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18
        }).addTo(this.map);

        this.loadDistricts();
        this.addLegend();
        this.addRiverLabels();
        this.addCoordinateDisplay();
    },

    async loadDistricts() {
        try {
            const resp = await fetch('data/phnom_penh_districts.geojson');
            const geojson = await resp.json();

            this.geojsonLayer = L.geoJSON(geojson, {
                style: (feature) => this.getDistrictStyle(feature.properties.id),
                onEachFeature: (feature, layer) => {
                    this.districtLayers[feature.properties.id] = layer;
                    layer.on('click', () => this.showDistrictPopup(feature.properties.id));
                    layer.on('mouseover', (e) => {
                        e.target.setStyle({ weight: 3, fillOpacity: 0.6 });
                        this.showHoverInfo(feature.properties.id, e);
                    });
                    layer.on('mouseout', (e) => {
                        e.target.setStyle(this.getDistrictStyle(feature.properties.id));
                        this.hideHoverInfo();
                    });
                    layer.on('mousemove', (e) => {
                        this.updateHoverPosition(e);
                    });
                }
            }).addTo(this.map);
        } catch (err) {
            console.error('Failed to load district GeoJSON:', err);
        }
    },

    getLevelColor(level) {
        return { 0: '#22c55e', 1: '#eab308', 2: '#f97316', 3: '#ef4444' }[level] || '#22c55e';
    },

    getDistrictData(id) {
        return this.data?.districts?.find(d => d.id === id);
    },

    getDistrictStyle(districtId) {
        const d = this.getDistrictData(districtId);
        const step = App.currentTimeStep;
        const info = step === 'current' ? d?.current : d?.forecast?.[step];
        const color = this.getLevelColor(info?.level ?? 0);
        return {
            fillColor: color,
            fillOpacity: 0.4,
            color: color,
            weight: 2,
            opacity: 0.8
        };
    },

    showDistrictPopup(districtId) {
        const d = this.getDistrictData(districtId);
        if (!d) return;
        const layer = this.districtLayers[districtId];
        const popup = L.popup({ maxWidth: 320, className: 'dark-popup' })
            .setContent(this.buildPopupContent(d));
        layer.bindPopup(popup).openPopup();
    },

    buildPopupContent(d) {
        const step = App.currentTimeStep;
        const current = d.current;
        const info = step === 'current' ? current : d.forecast[step];
        const colors = { 0: '#22c55e', 1: '#eab308', 2: '#f97316', 3: '#ef4444' };

        const steps = ['current', 't24h', 't48h', 't72h'];
        const labels = ['Now', '+24h', '+48h', '+72h'];
        let barsHtml = '<div class="popup-forecast-bars">';
        steps.forEach((s, i) => {
            const si = s === 'current' ? d.current : d.forecast[s];
            const score = si?.score ?? 0;
            const color = colors[si?.level ?? 0];
            const active = s === step ? ' active' : '';
            barsHtml += `<div class="forecast-bar${active}">
                <div class="bar-fill" style="height:${score}%;background:${color}"></div>
                <span class="bar-label">${labels[i]}</span>
            </div>`;
        });
        barsHtml += '</div>';

        return `
            <div class="popup-header">
                <h3>${d.name} <span class="popup-khmer">${d.name_km}</span></h3>
                <span class="level-badge level-${info.level}">${info.label}</span>
            </div>
            <div class="popup-score">Score: <strong>${info.score}</strong>/100</div>
            ${barsHtml}
            <div class="popup-metrics">
                <div class="metric"><span class="metric-label">Rain 24h</span><span>${current.rainfall_24h_mm ?? '--'}mm</span></div>
                <div class="metric"><span class="metric-label">Soil</span><span>${current.soil_moisture != null ? (current.soil_moisture * 100).toFixed(0) + '%' : '--'}</span></div>
                <div class="metric"><span class="metric-label">River</span><span>${current.river_discharge_ratio != null ? current.river_discharge_ratio.toFixed(2) + '\u00d7' : '--'}</span></div>
            </div>
            <div class="popup-factors">
                ${(info.factors || []).map(f => `<span class="factor-tag">${f}</span>`).join('')}
            </div>
        `;
    },

    updateForTimeStep(step) {
        Object.entries(this.districtLayers).forEach(([id, layer]) => {
            const d = this.getDistrictData(id);
            const info = step === 'current' ? d?.current : d?.forecast?.[step];
            const color = this.getLevelColor(info?.level ?? 0);
            layer.setStyle({
                fillColor: color,
                fillOpacity: 0.4,
                color: color,
                weight: 2,
                opacity: 0.8
            });
        });
    },

    addLegend() {
        const legend = L.control({ position: 'bottomright' });
        legend.onAdd = () => {
            const div = L.DomUtil.create('div', 'map-legend');
            div.innerHTML = `
                <h4 data-i18n="alert_levels">Alert Levels</h4>
                <div class="legend-item"><span class="legend-color" style="background:#22c55e"></span><span data-i18n="normal">Normal</span></div>
                <div class="legend-item"><span class="legend-color" style="background:#eab308"></span><span data-i18n="watch">Watch</span></div>
                <div class="legend-item"><span class="legend-color" style="background:#f97316"></span><span data-i18n="warning">Warning</span></div>
                <div class="legend-item"><span class="legend-color" style="background:#ef4444"></span><span data-i18n="emergency">Emergency</span></div>
            `;
            return div;
        };
        legend.addTo(this.map);
    },

    addRiverLabels() {
        const rivers = [
            { name: 'Mekong', lat: 11.62, lon: 104.955 },
            { name: 'Tonle Sap', lat: 11.585, lon: 104.925 },
            { name: 'Bassac', lat: 11.52, lon: 104.945 }
        ];
        rivers.forEach(r => {
            L.marker([r.lat, r.lon], {
                icon: L.divIcon({
                    className: 'river-label',
                    html: `<span>${r.name}</span>`,
                    iconSize: [80, 20]
                }),
                interactive: false
            }).addTo(this.map);
        });
    },

    addCoordinateDisplay() {
        const coordDiv = L.DomUtil.create('div', 'coord-display');
        coordDiv.id = 'coord-display';
        coordDiv.style.display = 'none';
        document.getElementById('map-container').appendChild(coordDiv);

        this.map.on('mousemove', (e) => {
            coordDiv.style.display = 'block';
            coordDiv.style.left = (e.containerPoint.x + 15) + 'px';
            coordDiv.style.top = (e.containerPoint.y + 15) + 'px';
            if (!this._hoverDistrict) {
                coordDiv.innerHTML = `<span class="coord-latlon">${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}</span>`;
            }
        });

        this.map.on('mouseout', () => {
            coordDiv.style.display = 'none';
        });
    },

    _hoverDistrict: null,

    showHoverInfo(districtId, e) {
        this._hoverDistrict = districtId;
        const d = this.getDistrictData(districtId);
        if (!d) return;
        const step = App.currentTimeStep;
        const info = step === 'current' ? d.current : d.forecast?.[step];
        const level = info?.level ?? 0;
        const labels = { 0: 'NORMAL', 1: 'WATCH', 2: 'WARNING', 3: 'EMERGENCY' };
        const colors = { 0: '#22c55e', 1: '#eab308', 2: '#f97316', 3: '#ef4444' };
        const coordDiv = document.getElementById('coord-display');
        if (coordDiv) {
            coordDiv.innerHTML = `
                <div class="hover-title">${d.name} <span style="color:${colors[level]}">${d.name_km}</span></div>
                <div class="hover-level" style="color:${colors[level]}">${labels[level]} (${info?.score ?? 0}/100)</div>
                <div class="hover-detail">Rain 24h: ${d.current?.rainfall_24h_mm ?? '--'}mm</div>
                <div class="hover-detail">Soil: ${d.current?.soil_moisture != null ? (d.current.soil_moisture * 100).toFixed(0) + '%' : '--'}</div>
                <div class="hover-detail">River: ${d.current?.river_discharge_ratio != null ? d.current.river_discharge_ratio.toFixed(2) + '\u00d7 avg' : '--'}</div>
                <span class="coord-latlon">${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}</span>
            `;
        }
    },

    hideHoverInfo() {
        this._hoverDistrict = null;
    },

    updateHoverPosition(e) {
        const coordDiv = document.getElementById('coord-display');
        if (coordDiv) {
            coordDiv.style.left = (e.containerPoint.x + 15) + 'px';
            coordDiv.style.top = (e.containerPoint.y + 15) + 'px';
            if (this._hoverDistrict) {
                const d = this.getDistrictData(this._hoverDistrict);
                const latlon = coordDiv.querySelector('.coord-latlon');
                if (latlon) latlon.textContent = `${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`;
            }
        }
    },

    flyTo(lat, lon, zoom) {
        this.map.flyTo([lat, lon], zoom || 14, { duration: 0.8 });
    }
};
