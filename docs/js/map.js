/* ============================================
   FloodKH — Map Module (Leaflet)
   ============================================ */

const FloodMap = (() => {
  let map = null;
  let markersLayer = null;
  let boundaryLayer = null;

  const RISK_COLORS = {
    LOW: '#22c55e',
    MODERATE: '#eab308',
    HIGH: '#f97316',
    CRITICAL: '#ef4444'
  };

  const RISK_ORDER = { CRITICAL: 0, HIGH: 1, MODERATE: 2, LOW: 3 };

  function init() {
    map = L.map('map', {
      center: [12.5, 105.0],
      zoom: 7,
      zoomControl: true,
      attributionControl: true,
      minZoom: 6,
      maxZoom: 14
    });

    // Dark tile layer - CartoDB Dark Matter
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map);

    // Initialize markers layer
    markersLayer = L.layerGroup().addTo(map);

    // Add legend
    addLegend();

    // Add Cambodia boundary outline
    addCambodiaBoundary();

    // Fix map size on sidebar toggle
    setTimeout(() => map.invalidateSize(), 300);
  }

  function addLegend() {
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
      const div = L.DomUtil.create('div', 'legend-control');
      div.innerHTML = `
        <h4 data-i18n="legend_title">${I18n.t('legend_title')}</h4>
        <div class="legend-item"><span class="legend-dot" style="background:${RISK_COLORS.CRITICAL}"></span> ${I18n.t('critical')}</div>
        <div class="legend-item"><span class="legend-dot" style="background:${RISK_COLORS.HIGH}"></span> ${I18n.t('high')}</div>
        <div class="legend-item"><span class="legend-dot" style="background:${RISK_COLORS.MODERATE}"></span> ${I18n.t('moderate')}</div>
        <div class="legend-item"><span class="legend-dot" style="background:${RISK_COLORS.LOW}"></span> ${I18n.t('low')}</div>
      `;
      return div;
    };
    legend.addTo(map);
  }

  function addCambodiaBoundary() {
    // Simplified Cambodia boundary polygon
    const cambodiaBoundary = {
      type: 'Feature',
      properties: { name: 'Cambodia' },
      geometry: {
        type: 'Polygon',
        coordinates: [[
          [102.35, 10.49], [102.35, 10.55], [103.07, 10.27], [103.50, 10.55],
          [103.68, 10.47], [104.05, 10.41], [104.28, 10.52], [104.82, 10.39],
          [105.08, 10.61], [105.31, 10.85], [105.40, 10.96], [105.60, 11.01],
          [105.85, 11.19], [106.00, 11.05], [106.15, 11.02], [106.19, 11.05],
          [106.41, 11.01], [106.57, 11.19], [106.70, 11.56], [106.78, 11.95],
          [106.83, 12.08], [106.98, 12.34], [106.97, 12.73], [107.10, 12.90],
          [107.31, 12.99], [107.39, 13.12], [107.50, 13.31], [107.60, 13.54],
          [107.48, 13.67], [107.52, 14.00], [107.55, 14.20], [107.53, 14.37],
          [107.51, 14.49], [107.35, 14.57], [107.18, 14.60], [107.00, 14.49],
          [106.83, 14.31], [106.56, 14.23], [106.39, 14.33], [106.19, 14.31],
          [106.00, 14.37], [105.86, 14.26], [105.68, 14.34], [105.50, 14.35],
          [105.38, 14.34], [105.18, 14.35], [105.02, 14.26], [104.87, 14.34],
          [104.77, 14.43], [104.59, 14.39], [104.42, 14.37], [104.23, 14.40],
          [104.05, 14.36], [103.86, 14.33], [103.68, 14.35], [103.52, 14.29],
          [103.34, 14.26], [103.19, 14.33], [103.02, 14.25], [102.89, 14.14],
          [102.73, 13.84], [102.55, 13.61], [102.48, 13.44], [102.33, 13.32],
          [102.37, 13.04], [102.51, 12.85], [102.49, 12.67], [102.60, 12.43],
          [102.72, 12.26], [102.76, 12.01], [102.94, 11.78], [103.11, 11.56],
          [103.13, 11.37], [103.19, 11.17], [103.25, 11.00], [103.10, 10.88],
          [102.93, 10.78], [102.73, 10.64], [102.54, 10.53], [102.35, 10.49]
        ]]
      }
    };

    boundaryLayer = L.geoJSON(cambodiaBoundary, {
      style: {
        color: 'rgba(255,255,255,0.2)',
        weight: 1.5,
        fillColor: 'rgba(59,130,246,0.03)',
        fillOpacity: 1,
        dashArray: '4,4'
      }
    }).addTo(map);
  }

  function getMarkerRadius(score) {
    // Scale from 8 (score=0) to 25 (score=100)
    return Math.max(8, Math.min(25, 8 + (score / 100) * 17));
  }

  function updateMarkers(locations) {
    markersLayer.clearLayers();

    // Sort so higher risk renders on top
    const sorted = [...locations].sort((a, b) =>
      (RISK_ORDER[b.risk_level] || 3) - (RISK_ORDER[a.risk_level] || 3)
    );

    sorted.forEach(loc => {
      const color = RISK_COLORS[loc.risk_level] || RISK_COLORS.LOW;
      const radius = getMarkerRadius(loc.risk_score);
      const isKhmer = I18n.getLang() === 'km';
      const displayName = isKhmer && loc.name_km ? loc.name_km : loc.name;

      const marker = L.circleMarker([loc.lat, loc.lon], {
        radius: radius,
        fillColor: color,
        color: color,
        weight: 2,
        opacity: 0.9,
        fillOpacity: 0.35
      });

      marker.bindPopup(createPopupContent(loc), {
        maxWidth: 320,
        minWidth: 260
      });

      marker.on('mouseover', function () {
        this.setStyle({ fillOpacity: 0.6, weight: 3 });
      });
      marker.on('mouseout', function () {
        this.setStyle({ fillOpacity: 0.35, weight: 2 });
      });

      marker.locationData = loc;
      markersLayer.addLayer(marker);
    });
  }

  function createPopupContent(loc) {
    const isKhmer = I18n.getLang() === 'km';
    const name = loc.name;
    const nameKm = loc.name_km || '';
    const riskClass = loc.risk_level.toLowerCase();

    const factorsHtml = (loc.factors || []).map(f =>
      `<span class="popup-factor-tag">${f}</span>`
    ).join('');

    return `
      <div class="popup-title">${name}</div>
      ${nameKm ? `<div class="popup-subtitle">${nameKm}</div>` : ''}
      <div style="margin-bottom:8px;">
        <span class="risk-badge ${riskClass}">${loc.risk_level}</span>
        <span style="margin-left:8px;font-weight:600;color:${RISK_COLORS[loc.risk_level]}">${loc.risk_score}/100</span>
      </div>
      <div class="popup-metrics">
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('rainfall_24h')}</span>
          <span class="popup-metric-value">${loc.rainfall_24h_mm} mm</span>
        </div>
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('rainfall_3d')}</span>
          <span class="popup-metric-value">${loc.rainfall_3d_mm} mm</span>
        </div>
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('rainfall_7d')}</span>
          <span class="popup-metric-value">${loc.rainfall_7d_mm} mm</span>
        </div>
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('forecast_3d')}</span>
          <span class="popup-metric-value">${loc.forecast_3d_mm} mm</span>
        </div>
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('soil_moisture')}</span>
          <span class="popup-metric-value">${(loc.soil_moisture * 100).toFixed(0)}%</span>
        </div>
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('river_discharge')}</span>
          <span class="popup-metric-value">${loc.river_discharge_m3s} m\u00B3/s</span>
        </div>
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('river_avg')}</span>
          <span class="popup-metric-value">${loc.river_discharge_avg_m3s} m\u00B3/s</span>
        </div>
        <div class="popup-metric">
          <span class="popup-metric-label">${I18n.t('elevation')}</span>
          <span class="popup-metric-value">${loc.elevation_m} m</span>
        </div>
      </div>
      ${factorsHtml ? `
        <div class="popup-factors">
          <span class="popup-metric-label">${I18n.t('factors')}</span><br>
          ${factorsHtml}
        </div>
      ` : ''}
    `;
  }

  function flyTo(lat, lon, zoom) {
    if (map) {
      map.flyTo([lat, lon], zoom || 10, { duration: 1.2 });
    }
  }

  function invalidateSize() {
    if (map) {
      setTimeout(() => map.invalidateSize(), 50);
    }
  }

  return { init, updateMarkers, flyTo, invalidateSize };
})();
