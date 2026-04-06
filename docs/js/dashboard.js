/* ============================================
   FloodKH — Dashboard / Sidebar Module
   ============================================ */

const Dashboard = (() => {
  let currentData = null;
  let historyData = null;
  let sortColumn = 'risk_score';
  let sortDirection = 'desc';
  let sparklineCharts = {};

  const RISK_ORDER = { CRITICAL: 0, HIGH: 1, MODERATE: 2, LOW: 3 };
  const RISK_COLORS = {
    LOW: '#22c55e',
    MODERATE: '#eab308',
    HIGH: '#f97316',
    CRITICAL: '#ef4444'
  };

  function updateSummary(data) {
    const summary = data.national_summary || computeSummary(data.locations);
    document.getElementById('countCritical').textContent = summary.CRITICAL || 0;
    document.getElementById('countHigh').textContent = summary.HIGH || 0;
    document.getElementById('countModerate').textContent = summary.MODERATE || 0;
    document.getElementById('countLow').textContent = summary.LOW || 0;
  }

  function computeSummary(locations) {
    const counts = { LOW: 0, MODERATE: 0, HIGH: 0, CRITICAL: 0 };
    locations.forEach(loc => {
      if (counts.hasOwnProperty(loc.risk_level)) {
        counts[loc.risk_level]++;
      }
    });
    return counts;
  }

  function updateTable(locations) {
    currentData = locations;
    const tbody = document.getElementById('locationTableBody');
    const sorted = sortLocations(locations);
    const isKhmer = I18n.getLang() === 'km';

    tbody.innerHTML = sorted.map(loc => {
      const name = isKhmer && loc.name_km ? loc.name_km : loc.name;
      const riskClass = loc.risk_level.toLowerCase();
      return `
        <tr data-lat="${loc.lat}" data-lon="${loc.lon}" data-name="${loc.name}">
          <td>${name}</td>
          <td><span class="risk-badge ${riskClass}">${I18n.t(loc.risk_level.toLowerCase())}</span></td>
          <td>${loc.risk_score}</td>
          <td>${loc.rainfall_24h_mm}</td>
          <td>${loc.forecast_3d_mm}</td>
        </tr>
      `;
    }).join('');

    // Add click handlers
    tbody.querySelectorAll('tr').forEach(tr => {
      tr.addEventListener('click', () => {
        const lat = parseFloat(tr.dataset.lat);
        const lon = parseFloat(tr.dataset.lon);
        FloodMap.flyTo(lat, lon, 10);
      });
    });

    // Update sort indicators
    updateSortIndicators();
  }

  function sortLocations(locations) {
    return [...locations].sort((a, b) => {
      let va = a[sortColumn];
      let vb = b[sortColumn];

      if (sortColumn === 'risk_level') {
        va = RISK_ORDER[va] ?? 3;
        vb = RISK_ORDER[vb] ?? 3;
      } else if (sortColumn === 'name') {
        va = (va || '').toLowerCase();
        vb = (vb || '').toLowerCase();
        if (sortDirection === 'asc') return va < vb ? -1 : va > vb ? 1 : 0;
        return va > vb ? -1 : va < vb ? 1 : 0;
      }

      if (typeof va === 'number' && typeof vb === 'number') {
        return sortDirection === 'asc' ? va - vb : vb - va;
      }
      return 0;
    });
  }

  function updateSortIndicators() {
    document.querySelectorAll('.location-table thead th').forEach(th => {
      th.classList.remove('sort-asc', 'sort-desc');
      if (th.dataset.sort === sortColumn) {
        th.classList.add(sortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
      }
    });
  }

  function initSortHandlers() {
    document.querySelectorAll('.location-table thead th.sortable').forEach(th => {
      th.addEventListener('click', () => {
        const col = th.dataset.sort;
        if (sortColumn === col) {
          sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
          sortColumn = col;
          sortDirection = col === 'name' ? 'asc' : 'desc';
        }
        if (currentData) {
          updateTable(currentData);
        }
      });
    });
  }

  function updatePredictions(locations) {
    const container = document.getElementById('predictionCards');
    // Show locations with notable forecast
    const notable = [...locations]
      .filter(l => l.forecast_3d_mm > 20)
      .sort((a, b) => b.forecast_3d_mm - a.forecast_3d_mm)
      .slice(0, 5);

    if (notable.length === 0) {
      container.innerHTML = `<p style="color:var(--text-muted);font-size:0.82rem;">${I18n.t('no_data')}</p>`;
      return;
    }

    const isKhmer = I18n.getLang() === 'km';
    container.innerHTML = notable.map(loc => {
      const name = isKhmer && loc.name_km ? loc.name_km : loc.name;
      const currentRisk = loc.risk_level;
      const forecastRisk = predictRisk(loc);
      const currentColor = RISK_COLORS[currentRisk];
      const forecastColor = RISK_COLORS[forecastRisk];
      const arrow = RISK_ORDER[forecastRisk] < RISK_ORDER[currentRisk]
        ? '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 3l5 7H3z"/></svg>'
        : RISK_ORDER[forecastRisk] > RISK_ORDER[currentRisk]
          ? '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 13l5-7H3z"/></svg>'
          : '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M3 8h10"/><rect x="3" y="7" width="10" height="2" rx="1"/></svg>';

      return `
        <div class="prediction-card">
          <span class="prediction-name">${name}</span>
          <span class="prediction-arrow">
            <span class="risk-badge ${currentRisk.toLowerCase()}">${I18n.t(currentRisk.toLowerCase())}</span>
            ${arrow}
            <span class="risk-badge ${forecastRisk.toLowerCase()}">${I18n.t(forecastRisk.toLowerCase())}</span>
          </span>
        </div>
      `;
    }).join('');
  }

  function predictRisk(loc) {
    // Simple heuristic: if forecast is heavy, bump risk level
    const forecast = loc.forecast_3d_mm || 0;
    if (forecast > 150) return 'CRITICAL';
    if (forecast > 80) return 'HIGH';
    if (forecast > 40) return 'MODERATE';
    return loc.risk_level;
  }

  function updateTimestamp(timestamp) {
    const el = document.getElementById('lastUpdated');
    if (!timestamp) {
      el.textContent = '--';
      return;
    }
    try {
      const date = new Date(timestamp);
      const opts = {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit', timeZoneName: 'short'
      };
      el.textContent = date.toLocaleDateString('en-US', opts);
    } catch {
      el.textContent = timestamp;
    }
  }

  // Dashboard view charts
  function renderDashboard(locations, history) {
    historyData = history;
    const grid = document.getElementById('dashboardGrid');
    grid.innerHTML = '';

    // Risk distribution chart
    const distCard = createDashCard('Risk Distribution');
    grid.appendChild(distCard.card);
    renderRiskDistribution(distCard.canvas, locations);

    // Top rainfall chart
    const rainCard = createDashCard('Rainfall 24h (mm)');
    grid.appendChild(rainCard.card);
    renderTopRainfall(rainCard.canvas, locations);

    // Forecast chart
    const forecastCard = createDashCard('3-Day Forecast (mm)');
    grid.appendChild(forecastCard.card);
    renderForecast(forecastCard.canvas, locations);

    // River discharge chart
    const riverCard = createDashCard('River Discharge vs Avg');
    grid.appendChild(riverCard.card);
    renderRiverDischarge(riverCard.canvas, locations);

    // History sparklines for notable locations
    if (history && history.locations) {
      Object.keys(history.locations).slice(0, 4).forEach(locName => {
        const histCard = createDashCard(`${locName} — 30-day Risk Score`);
        grid.appendChild(histCard.card);
        renderHistorySparkline(histCard.canvas, history.locations[locName]);
      });
    }
  }

  function createDashCard(title) {
    const card = document.createElement('div');
    card.className = 'dashboard-card';
    card.innerHTML = `
      <div class="dashboard-card-title">${title}</div>
      <div class="dashboard-chart-container"><canvas></canvas></div>
    `;
    const canvas = card.querySelector('canvas');
    return { card, canvas };
  }

  function chartDefaults() {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#8892a4', font: { size: 11 } } }
      },
      scales: {
        x: { ticks: { color: '#5a6478', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
        y: { ticks: { color: '#5a6478', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
      }
    };
  }

  function renderRiskDistribution(canvas, locations) {
    const counts = computeSummary(locations);
    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['Critical', 'High', 'Moderate', 'Low'],
        datasets: [{
          data: [counts.CRITICAL, counts.HIGH, counts.MODERATE, counts.LOW],
          backgroundColor: [RISK_COLORS.CRITICAL, RISK_COLORS.HIGH, RISK_COLORS.MODERATE, RISK_COLORS.LOW],
          borderWidth: 0,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'right',
            labels: { color: '#8892a4', font: { size: 11 }, padding: 12, usePointStyle: true, pointStyleWidth: 10 }
          }
        }
      }
    });
  }

  function renderTopRainfall(canvas, locations) {
    const top = [...locations].sort((a, b) => b.rainfall_24h_mm - a.rainfall_24h_mm).slice(0, 8);
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: top.map(l => l.name.length > 12 ? l.name.slice(0, 12) + '..' : l.name),
        datasets: [{
          data: top.map(l => l.rainfall_24h_mm),
          backgroundColor: top.map(l => RISK_COLORS[l.risk_level] + '88'),
          borderColor: top.map(l => RISK_COLORS[l.risk_level]),
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        ...chartDefaults(),
        indexAxis: 'y',
        plugins: { legend: { display: false } }
      }
    });
  }

  function renderForecast(canvas, locations) {
    const top = [...locations].sort((a, b) => b.forecast_3d_mm - a.forecast_3d_mm).slice(0, 8);
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: top.map(l => l.name.length > 12 ? l.name.slice(0, 12) + '..' : l.name),
        datasets: [{
          data: top.map(l => l.forecast_3d_mm),
          backgroundColor: top.map(l => RISK_COLORS[l.risk_level] + '66'),
          borderColor: top.map(l => RISK_COLORS[l.risk_level]),
          borderWidth: 1,
          borderRadius: 4
        }]
      },
      options: {
        ...chartDefaults(),
        indexAxis: 'y',
        plugins: { legend: { display: false } }
      }
    });
  }

  function renderRiverDischarge(canvas, locations) {
    const withRiver = locations.filter(l => l.river_discharge_m3s > 0).slice(0, 10);
    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: withRiver.map(l => l.name.length > 10 ? l.name.slice(0, 10) + '..' : l.name),
        datasets: [
          {
            label: 'Current',
            data: withRiver.map(l => l.river_discharge_m3s),
            backgroundColor: '#3b82f688',
            borderColor: '#3b82f6',
            borderWidth: 1,
            borderRadius: 4
          },
          {
            label: 'Average',
            data: withRiver.map(l => l.river_discharge_avg_m3s),
            backgroundColor: '#6366f144',
            borderColor: '#6366f1',
            borderWidth: 1,
            borderRadius: 4
          }
        ]
      },
      options: chartDefaults()
    });
  }

  function renderHistorySparkline(canvas, locHistory) {
    const dates = locHistory.map(h => h.date.slice(5)); // MM-DD
    const scores = locHistory.map(h => h.risk_score);
    new Chart(canvas, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          data: scores,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59,130,246,0.1)',
          fill: true,
          tension: 0.35,
          pointRadius: 1.5,
          pointHoverRadius: 4,
          borderWidth: 2
        }]
      },
      options: {
        ...chartDefaults(),
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#5a6478', font: { size: 9 }, maxTicksLimit: 8 }, grid: { display: false } },
          y: { min: 0, max: 100, ticks: { color: '#5a6478', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.04)' } }
        }
      }
    });
  }

  function init() {
    initSortHandlers();
  }

  return {
    init,
    updateSummary,
    updateTable,
    updatePredictions,
    updateTimestamp,
    renderDashboard
  };
})();
