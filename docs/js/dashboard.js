/**
 * FloodKH Dashboard Module — Summary cards, district rankings, charts, river gauge.
 */
const Dashboard = {
    data: null,
    historyData: null,
    charts: {},

    init(data, historyData) {
        this.data = data;
        this.historyData = historyData;
        this.renderSummaryCards('current');
        this.renderDistrictRanking('current');
        this.renderSourceStatus();
        this.renderRiverGauge();
    },

    renderSummaryCards(step) {
        if (!this.data?.districts) return;
        const counts = { 0: 0, 1: 0, 2: 0, 3: 0 };
        this.data.districts.forEach(d => {
            const info = step === 'current' ? d.current : d.forecast?.[step];
            counts[info?.level ?? 0]++;
        });
        document.getElementById('count-normal').textContent = counts[0];
        document.getElementById('count-watch').textContent = counts[1];
        document.getElementById('count-warning').textContent = counts[2];
        document.getElementById('count-emergency').textContent = counts[3];
    },

    renderDistrictRanking(step) {
        const container = document.getElementById('district-ranking');
        if (!container || !this.data?.districts) return;

        const sorted = [...this.data.districts].sort((a, b) => {
            const sa = step === 'current' ? a.current?.score : a.forecast?.[step]?.score;
            const sb = step === 'current' ? b.current?.score : b.forecast?.[step]?.score;
            return (sb || 0) - (sa || 0);
        });

        const colors = { 0: '#22c55e', 1: '#eab308', 2: '#f97316', 3: '#ef4444' };

        container.innerHTML = sorted.map(d => {
            const info = step === 'current' ? d.current : d.forecast?.[step];
            const level = info?.level ?? 0;
            const score = info?.score ?? 0;
            return `
                <div class="district-rank-item" onclick="FloodMap.flyTo(${d.lat}, ${d.lon}); FloodMap.showDistrictPopup('${d.id}')">
                    <div class="rank-indicator" style="background:${colors[level]}"></div>
                    <div class="rank-info">
                        <span class="rank-name">${d.name}</span>
                        <span class="rank-name-km">${d.name_km}</span>
                    </div>
                    <div class="rank-score">
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:${score}%;background:${colors[level]}"></div>
                        </div>
                        <span class="score-value">${score}</span>
                    </div>
                </div>
            `;
        }).join('');
    },

    renderSourceStatus() {
        const container = document.getElementById('source-indicators');
        if (!container || !this.data?.data_sources_status) return;

        const labels = {
            open_meteo: 'Open-Meteo',
            sentinel_1: 'Sentinel-1 SAR',
            sentinel_2: 'Sentinel-2',
            nasa_gpm: 'NASA GPM',
            river_discharge: 'River Discharge'
        };

        container.innerHTML = Object.entries(this.data.data_sources_status).map(([key, status]) => {
            const isLive = status === 'ok';
            return `<div class="source-item">
                <span class="source-dot ${isLive ? 'live' : 'stub'}"></span>
                <span class="source-name">${labels[key] || key}</span>
                <span class="source-status-text">${status}</span>
            </div>`;
        }).join('');
    },

    renderRiverGauge() {
        const container = document.getElementById('river-gauge');
        if (!container || !this.data?.districts) return;

        // Average river discharge ratio across districts
        let totalRatio = 0, count = 0;
        this.data.districts.forEach(d => {
            const r = d.current?.river_discharge_ratio;
            if (r != null) { totalRatio += r; count++; }
        });
        const ratio = count > 0 ? totalRatio / count : 0;
        const pct = Math.min(ratio / 2.5 * 100, 100);
        let color = '#22c55e';
        if (ratio > 2.0) color = '#ef4444';
        else if (ratio > 1.6) color = '#f97316';
        else if (ratio > 1.3) color = '#eab308';

        container.innerHTML = `
            <div class="gauge-container">
                <div class="gauge-bar">
                    <div class="gauge-fill" style="height:${pct}%;background:${color}"></div>
                </div>
                <div class="gauge-labels">
                    <span class="gauge-value">${ratio.toFixed(2)}\u00d7</span>
                    <span class="gauge-label" data-i18n="avg_ratio">vs average</span>
                </div>
                <div class="gauge-thresholds">
                    <span style="bottom:40%">1.0\u00d7</span>
                    <span style="bottom:64%">1.6\u00d7</span>
                    <span style="bottom:80%">2.0\u00d7</span>
                </div>
            </div>
        `;
    },

    updateForTimeStep(step) {
        this.renderSummaryCards(step);
        this.renderDistrictRanking(step);
    },

    refresh() {
        this.renderDashboardCharts();
    },

    renderDashboardCharts() {
        const container = document.getElementById('dashboard-view');
        if (!container) return;

        container.innerHTML = `
            <div class="dashboard-grid">
                <div class="chart-card"><h3 data-i18n="risk_distribution">Risk Distribution</h3><canvas id="chart-donut"></canvas></div>
                <div class="chart-card"><h3 data-i18n="rainfall_forecast">72h Rainfall Forecast</h3><canvas id="chart-rainfall"></canvas></div>
                <div class="chart-card full-width"><h3 data-i18n="district_scores">District Risk Scores</h3><canvas id="chart-scores"></canvas></div>
            </div>
        `;

        I18n.applyTranslations();
        this._renderDonut();
        this._renderRainfall();
        this._renderScores();
    },

    _renderDonut() {
        const ctx = document.getElementById('chart-donut');
        if (!ctx) return;
        const counts = { 0: 0, 1: 0, 2: 0, 3: 0 };
        (this.data?.districts || []).forEach(d => { counts[d.current?.level ?? 0]++; });
        if (this.charts.donut) this.charts.donut.destroy();
        this.charts.donut = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Normal', 'Watch', 'Warning', 'Emergency'],
                datasets: [{ data: [counts[0], counts[1], counts[2], counts[3]], backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444'], borderWidth: 0 }]
            },
            options: { responsive: true, plugins: { legend: { labels: { color: '#e0e6f0' } } } }
        });
    },

    _renderRainfall() {
        const ctx = document.getElementById('chart-rainfall');
        if (!ctx) return;
        const ds = this.data?.districts || [];
        const avg = (key) => ds.reduce((s, d) => s + (d.current?.[key] || 0), 0) / (ds.length || 1);
        const vals = [avg('rainfall_24h_mm'), avg('forecast_24h_mm'), avg('forecast_48h_mm'), avg('forecast_72h_mm')];
        if (this.charts.rainfall) this.charts.rainfall.destroy();
        this.charts.rainfall = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Past 24h', '+24h', '+48h', '+72h'],
                datasets: [{ label: 'Avg Rainfall (mm)', data: vals.map(v => v.toFixed(1)), backgroundColor: ['#3b82f6', '#60a5fa', '#93bbfd', '#bfdbfe'], borderWidth: 0 }]
            },
            options: {
                responsive: true,
                scales: { y: { ticks: { color: '#8892a4' }, grid: { color: '#2a3548' } }, x: { ticks: { color: '#8892a4' }, grid: { display: false } } },
                plugins: { legend: { display: false } }
            }
        });
    },

    _renderScores() {
        const ctx = document.getElementById('chart-scores');
        if (!ctx) return;
        const sorted = [...(this.data?.districts || [])].sort((a, b) => (b.current?.score || 0) - (a.current?.score || 0));
        const colors = { 0: '#22c55e', 1: '#eab308', 2: '#f97316', 3: '#ef4444' };
        if (this.charts.scores) this.charts.scores.destroy();
        this.charts.scores = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sorted.map(d => d.name),
                datasets: [{ label: 'Risk Score', data: sorted.map(d => d.current?.score || 0), backgroundColor: sorted.map(d => colors[d.current?.level || 0]), borderWidth: 0 }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: { x: { max: 100, ticks: { color: '#8892a4' }, grid: { color: '#2a3548' } }, y: { ticks: { color: '#e0e6f0', font: { size: 11 } }, grid: { display: false } } },
                plugins: { legend: { display: false } }
            }
        });
    }
};
