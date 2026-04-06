/* ============================================
   FloodKH — Main Application
   ============================================ */

(function () {
  'use strict';

  let floodData = null;
  let historyData = null;
  let sidebarOpen = true;
  const isMobile = () => window.innerWidth <= 768;

  // --- Initialize ---
  document.addEventListener('DOMContentLoaded', () => {
    I18n.init();
    Dashboard.init();
    FloodMap.init();

    setupSidebar();
    setupNav();
    setupLangToggle();
    updateLangButton();

    // On mobile, start with sidebar closed
    if (isMobile()) {
      closeSidebar();
    }

    // Fetch data
    loadData();
  });

  // --- Data Loading ---
  async function loadData() {
    showError(false);
    try {
      const [statusRes, historyRes] = await Promise.all([
        fetch('data/flood_status.json'),
        fetch('data/flood_history.json').catch(() => null)
      ]);

      if (!statusRes.ok) throw new Error(`HTTP ${statusRes.status}`);
      floodData = await statusRes.json();

      if (historyRes && historyRes.ok) {
        historyData = await historyRes.json();
      }

      renderAll();
    } catch (err) {
      console.error('Failed to load data:', err);
      showError(true);
    }
  }

  function renderAll() {
    if (!floodData || !floodData.locations) return;

    const locations = floodData.locations;

    // Update map
    FloodMap.updateMarkers(locations);

    // Update sidebar
    Dashboard.updateSummary(floodData);
    Dashboard.updateTable(locations);
    Dashboard.updatePredictions(locations);
    Dashboard.updateTimestamp(floodData.updated_at);

    // Update dashboard view
    Dashboard.renderDashboard(locations, historyData);
  }

  // --- Sidebar ---
  function setupSidebar() {
    const toggle = document.getElementById('sidebarToggle');
    const overlay = document.getElementById('sidebarOverlay');

    toggle.addEventListener('click', () => {
      if (sidebarOpen) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    overlay.addEventListener('click', closeSidebar);
  }

  function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('mainContent');
    const overlay = document.getElementById('sidebarOverlay');

    sidebarOpen = true;
    sidebar.classList.remove('collapsed');
    main.classList.remove('sidebar-collapsed');

    if (isMobile()) {
      sidebar.classList.add('open');
      overlay.classList.add('active');
    }

    FloodMap.invalidateSize();
  }

  function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('mainContent');
    const overlay = document.getElementById('sidebarOverlay');

    sidebarOpen = false;
    sidebar.classList.add('collapsed');
    sidebar.classList.remove('open');
    main.classList.add('sidebar-collapsed');
    overlay.classList.remove('active');

    FloodMap.invalidateSize();
  }

  // --- Navigation ---
  function setupNav() {
    document.querySelectorAll('.nav-link[data-view]').forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const view = link.dataset.view;

        // Update active nav
        document.querySelectorAll('.nav-link[data-view]').forEach(l => l.classList.remove('active'));
        link.classList.add('active');

        // Switch views
        document.querySelectorAll('.view-map, .view-dashboard').forEach(v => v.classList.remove('active'));

        if (view === 'map') {
          document.getElementById('viewMap').classList.add('active');
          FloodMap.invalidateSize();
        } else if (view === 'dashboard') {
          document.getElementById('viewDashboard').classList.add('active');
        }
      });
    });
  }

  // --- Language ---
  function setupLangToggle() {
    document.getElementById('langToggle').addEventListener('click', () => {
      const newLang = I18n.toggleLang();
      updateLangButton();
      // Re-render data-dependent content
      if (floodData) {
        renderAll();
      }
    });
  }

  function updateLangButton() {
    const label = document.getElementById('langLabel');
    label.textContent = I18n.getLang() === 'en' ? 'KH' : 'EN';
  }

  // --- Error Banner ---
  function showError(visible) {
    let banner = document.querySelector('.error-banner');
    if (!banner) {
      banner = document.createElement('div');
      banner.className = 'error-banner';
      banner.textContent = I18n.t('error_fetch');
      document.body.appendChild(banner);
    }
    banner.classList.toggle('visible', visible);
  }

})();
