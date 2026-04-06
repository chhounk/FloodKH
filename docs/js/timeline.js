/**
 * FloodKH Timeline Module — 72-hour forecast timeline slider.
 */
const Timeline = {
    steps: ['current', 't24h', 't48h', 't72h'],
    labels: ['Now', '+24h', '+48h', '+72h'],

    init(data) {
        this.data = data;
        const slider = document.getElementById('time-slider');
        if (!slider) return;

        slider.addEventListener('input', (e) => {
            const idx = parseInt(e.target.value);
            const step = this.steps[idx];
            App.setTimeStep(step);
            this.updateActiveLabel(idx);
        });
    },

    updateActiveLabel(index) {
        document.querySelectorAll('.timeline-labels span').forEach((el, i) => {
            el.classList.toggle('active', i === index);
        });
    }
};
