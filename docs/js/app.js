/**
 * FloodKH — Main Application Controller
 */
const App = {
    data: null,
    historyData: null,
    currentTimeStep: 'current',

    async init() {
        try {
            await this.loadData();
            FloodMap.init(this.data);
            Timeline.init(this.data);
            Dashboard.init(this.data, this.historyData);
            I18n.init();
            this.setupEventListeners();
            this.updateTimestamp();
        } catch (err) {
            this.showError('Failed to load flood data. Please try again later.');
            console.error(err);
        }
    },

    async loadData() {
        const [predResp, histResp] = await Promise.all([
            fetch('data/flood_predictions.json'),
            fetch('data/flood_history.json').catch(() => null)
        ]);
        if (!predResp.ok) throw new Error('Failed to fetch predictions');
        this.data = await predResp.json();
        if (histResp && histResp.ok) {
            this.historyData = await histResp.json();
        }
    },

    setupEventListeners() {
        document.querySelectorAll('.nav-btn[data-view]').forEach(btn => {
            btn.addEventListener('click', () => this.switchView(btn.dataset.view));
        });

        const sidebarToggle = document.getElementById('sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.getElementById('sidebar').classList.toggle('collapsed');
            });
        }
    },

    switchView(view) {
        document.querySelectorAll('.nav-btn[data-view]').forEach(b => b.classList.remove('active'));
        document.querySelector(`[data-view="${view}"]`)?.classList.add('active');
        document.getElementById('map-container').classList.toggle('hidden', view !== 'map');
        document.getElementById('dashboard-view').classList.toggle('hidden', view !== 'dashboard');
        if (view === 'map') FloodMap.map?.invalidateSize();
        if (view === 'dashboard') Dashboard.refresh();
    },

    setTimeStep(step) {
        this.currentTimeStep = step;
        FloodMap.updateForTimeStep(step);
        Dashboard.updateForTimeStep(step);
    },

    updateTimestamp() {
        const el = document.getElementById('update-time');
        if (this.data?.generated_at) {
            const d = new Date(this.data.generated_at);
            el.textContent = d.toLocaleString();
        }
    },

    showError(msg) {
        const banner = document.createElement('div');
        banner.className = 'error-banner';
        banner.textContent = msg;
        document.body.prepend(banner);
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
