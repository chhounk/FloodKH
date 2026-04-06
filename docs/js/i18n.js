/* ============================================
   FloodKH — Internationalization (EN / KH)
   ============================================ */

const I18n = (() => {
  const translations = {
    en: {
      // Nav
      nav_map: 'Map',
      nav_dashboard: 'Dashboard',
      nav_methodology: 'Methodology',

      // Summary
      national_summary: 'National Summary',
      critical: 'Critical',
      high: 'High',
      moderate: 'Moderate',
      low: 'Low',

      // Table
      locations: 'Locations',
      th_location: 'Location',
      th_risk: 'Risk',
      th_score: 'Score',
      th_rain24h: 'Rain 24h',
      th_forecast: 'Forecast',

      // Predictions
      predictions: '3-Day Forecast',

      // Dashboard
      dashboard_title: 'Monitoring Dashboard',
      last_updated: 'Last Updated',

      // Popup
      risk_level: 'Risk Level',
      risk_score: 'Risk Score',
      rainfall_24h: 'Rainfall 24h',
      rainfall_3d: 'Rainfall 3d',
      rainfall_7d: 'Rainfall 7d',
      forecast_3d: 'Forecast 3d',
      soil_moisture: 'Soil Moisture',
      river_discharge: 'River Discharge',
      river_avg: 'Avg Discharge',
      elevation: 'Elevation',
      factors: 'Contributing Factors',

      // Legend
      legend_title: 'Risk Levels',

      // Misc
      no_data: 'No data available',
      loading: 'Loading...',
      error_fetch: 'Failed to load data. Please try again later.',
      mm: 'mm',
      m3s: 'm\u00B3/s',
      meters: 'm',

      // Province names
      prov_phnom_penh: 'Phnom Penh',
      prov_siem_reap: 'Siem Reap',
      prov_battambang: 'Battambang',
      prov_kampong_cham: 'Kampong Cham',
      prov_prey_veng: 'Prey Veng',
      prov_takeo: 'Takeo',
      prov_kandal: 'Kandal',
      prov_kampong_thom: 'Kampong Thom',
      prov_pursat: 'Pursat',
      prov_kampong_speu: 'Kampong Speu',
      prov_svay_rieng: 'Svay Rieng',
      prov_kratie: 'Kratie',
      prov_stung_treng: 'Stung Treng',
      prov_kampong_chhnang: 'Kampong Chhnang',
      prov_banteay_meanchey: 'Banteay Meanchey',
      prov_kampot: 'Kampot',
      prov_koh_kong: 'Koh Kong',
      prov_preah_vihear: 'Preah Vihear',
      prov_ratanakiri: 'Ratanakiri',
      prov_mondulkiri: 'Mondulkiri',
      prov_tbong_khmum: 'Tbong Khmum',
      prov_preah_sihanouk: 'Preah Sihanouk',
      prov_pailin: 'Pailin',
      prov_kep: 'Kep',
      prov_oddar_meanchey: 'Oddar Meanchey'
    },

    km: {
      // Nav
      nav_map: '\u0795\u07C2\u1793\u1791\u17B8',
      nav_dashboard: '\u1795\u17D2\u1791\u17B6\u17C6\u1784\u1782\u17D2\u179A\u17B6\u17B6\u17B6\u17B6\u17B6',
      nav_methodology: '\u179C\u17B7\u1792\u17B8\u179F\u17B6\u179F\u17D2\u178F\u17D2\u179A',

      // Summary
      national_summary: '\u179F\u1789\u17D2\u1789\u17B6\u179F\u1784\u17D2\u1781\u17C1\u1794\u1787\u17B6\u178F\u17B7',
      critical: '\u1792\u17D2\u1784\u1793\u17CB\u1792\u17D2\u1784\u179A',
      high: '\u1781\u17D2\u1796\u179F\u17CB',
      moderate: '\u1798\u1792\u17D2\u1799\u1798',
      low: '\u1791\u17B6\u1794',

      // Table
      locations: '\u1791\u17B8\u178F\u17B6\u17C6\u1784',
      th_location: '\u1791\u17B8\u178F\u17B6\u17C6\u1784',
      th_risk: '\u17A0\u17B6\u1793\u17B7\u1797\u17D0\u1799',
      th_score: '\u1796\u17B7\u1793\u17D2\u1791\u17BB',
      th_rain24h: '\u1797\u17D2\u179B\u17C0\u1784 24h',
      th_forecast: '\u1780\u17B6\u179A\u1796\u17D2\u1799\u17B6\u1780\u179A\u178E\u17CD',

      // Predictions
      predictions: '\u1780\u17B6\u179A\u1796\u17D2\u1799\u17B6\u1780\u179A\u178E\u17CD 3\u1790\u17D2\u1784\u17C3',

      // Dashboard
      dashboard_title: '\u1795\u17D2\u1791\u17B6\u17C6\u1784\u1782\u17D2\u179A\u17B6\u1794\u17CB\u1794\u17B6\u179A\u17B6\u1798\u17C9\u17C2\u178F',
      last_updated: '\u1794\u1785\u17D2\u1785\u17BB\u1794\u17D2\u1794\u1793\u17D2\u1793\u1797\u17B6\u1796\u1785\u17BB\u1784\u1780\u17D2\u179A\u17C4\u1799',

      // Popup
      risk_level: '\u1780\u1798\u17D2\u179A\u17B7\u178F\u17A0\u17B6\u1793\u17B7\u1797\u17D0\u1799',
      risk_score: '\u1796\u17B7\u1793\u17D2\u1791\u17BB\u17A0\u17B6\u1793\u17B7\u1797\u17D0\u1799',
      rainfall_24h: '\u1794\u179A\u17B7\u1798\u17B6\u178E\u1791\u17B9\u1780\u1797\u17D2\u179B\u17C0\u1784 24h',
      rainfall_3d: '\u1794\u179A\u17B7\u1798\u17B6\u178E\u1791\u17B9\u1780\u1797\u17D2\u179B\u17C0\u1784 3\u1790\u17D2\u1784\u17C3',
      rainfall_7d: '\u1794\u179A\u17B7\u1798\u17B6\u178E\u1791\u17B9\u1780\u1797\u17D2\u179B\u17C0\u1784 7\u1790\u17D2\u1784\u17C3',
      forecast_3d: '\u1780\u17B6\u179A\u1796\u17D2\u1799\u17B6\u1780\u179A\u178E\u17CD 3\u1790\u17D2\u1784\u17C3',
      soil_moisture: '\u179F\u17C6\u178E\u17B6\u17C6\u178A\u17B8',
      river_discharge: '\u1794\u179A\u17B7\u1798\u17B6\u178E\u1791\u17B9\u1780\u1791\u17C0',
      river_avg: '\u1798\u1792\u17D2\u1799\u1798\u1794\u179A\u17B7\u1798\u17B6\u178E\u1791\u17B9\u1780',
      elevation: '\u1780\u1798\u17D2\u1796\u179F\u17CB',
      factors: '\u1780\u178F\u17D2\u178F\u17B6\u179C\u17B7\u1780\u17B6',

      // Legend
      legend_title: '\u1780\u1798\u17D2\u179A\u17B7\u178F\u17A0\u17B6\u1793\u17B7\u1797\u17D0\u1799',

      // Misc
      no_data: '\u1798\u17B7\u1793\u1798\u17B6\u1793\u1791\u17B7\u1793\u17D2\u1793\u1793\u17D0\u1799',
      loading: '\u1780\u17C6\u1796\u17BB\u1784\u1791\u17B6\u1789...',
      error_fetch: '\u1794\u179A\u17B6\u1787\u17D0\u1799\u1780\u17D2\u1793\u17BB\u1784\u1780\u17B6\u179A\u1791\u17B6\u1789\u1799\u1780\u1791\u17B7\u1793\u17D2\u1793\u1793\u17D0\u1799\u17D4',
      mm: '\u1798\u17B8\u179B\u17B8\u1798\u17C2\u178F',
      m3s: '\u1798\u17C3/\u179C\u17B7',
      meters: '\u1798\u17C2\u178F',

      // Province names in Khmer
      prov_phnom_penh: '\u1797\u17D2\u1793\u17C6\u1796\u17C1\u1789',
      prov_siem_reap: '\u179F\u17C0\u1798\u179A\u17B6\u1794',
      prov_battambang: '\u1794\u17B6\u178F\u17CB\u178A\u17C6\u1794\u1784',
      prov_kampong_cham: '\u1780\u17C6\u1796\u1784\u17CB\u1785\u17B6\u1798',
      prov_prey_veng: '\u1796\u17D2\u179A\u17C3\u179C\u17C2\u1784',
      prov_takeo: '\u178F\u17B6\u1780\u17C2\u179C',
      prov_kandal: '\u1780\u178E\u17D2\u178F\u17B6\u179B',
      prov_kampong_thom: '\u1780\u17C6\u1796\u1784\u17CB\u1790\u17C6',
      prov_pursat: '\u1796\u17C4\u1792\u17B7\u17CD\u179F\u17B6\u178F\u17CB',
      prov_kampong_speu: '\u1780\u17C6\u1796\u1784\u17CB\u179F\u17D2\u1796\u17BA',
      prov_svay_rieng: '\u179F\u17D2\u179C\u17B6\u1799\u179A\u17C0\u1784',
      prov_kratie: '\u1780\u17D2\u179A\u1785\u17C1\u17C7',
      prov_stung_treng: '\u179F\u17D2\u1791\u17B9\u1784\u178F\u17D2\u179A\u17C2\u1784',
      prov_kampong_chhnang: '\u1780\u17C6\u1796\u1784\u17CB\u1786\u17D2\u1793\u17B6\u17C6\u1784',
      prov_banteay_meanchey: '\u1794\u1793\u17D2\u1791\u17B6\u1799\u1798\u17B6\u1793\u1787\u17D0\u1799',
      prov_kampot: '\u1780\u17C6\u1796\u178F',
      prov_koh_kong: '\u1780\u17C4\u17C7\u1780\u17C4\u1784',
      prov_preah_vihear: '\u1796\u17D2\u179A\u17C7\u179C\u17B7\u17A0\u17B6\u179A',
      prov_ratanakiri: '\u179A\u178F\u17D2\u1793\u1782\u17B7\u179A\u17B8',
      prov_mondulkiri: '\u1798\u178E\u17D2\u178C\u179B\u1782\u17B7\u179A\u17B8',
      prov_tbong_khmum: '\u178F\u17D2\u1794\u17C4\u1784\u1781\u17D2\u1798\u17BB\u17C6',
      prov_preah_sihanouk: '\u1796\u17D2\u179A\u17C7\u179F\u17B8\u17A0\u1793\u17BB',
      prov_pailin: '\u1794\u17C9\u17C3\u179B\u17B7\u1793',
      prov_kep: '\u1780\u17C2\u1794',
      prov_oddar_meanchey: '\u17A7\u178F\u17D2\u178F\u179A\u1798\u17B6\u1793\u1787\u17D0\u1799'
    }
  };

  let currentLang = localStorage.getItem('floodkh_lang') || 'en';

  function t(key) {
    const dict = translations[currentLang] || translations.en;
    return dict[key] || translations.en[key] || key;
  }

  function getLang() {
    return currentLang;
  }

  function setLang(lang) {
    currentLang = lang;
    localStorage.setItem('floodkh_lang', lang);
    applyTranslations();
    if (lang === 'km') {
      document.body.classList.add('lang-km');
    } else {
      document.body.classList.remove('lang-km');
    }
  }

  function toggleLang() {
    setLang(currentLang === 'en' ? 'km' : 'en');
    return currentLang;
  }

  function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = t(key);
    });
  }

  function init() {
    const saved = localStorage.getItem('floodkh_lang');
    if (saved) {
      currentLang = saved;
    }
    if (currentLang === 'km') {
      document.body.classList.add('lang-km');
    }
    applyTranslations();
  }

  return { t, getLang, setLang, toggleLang, init };
})();
