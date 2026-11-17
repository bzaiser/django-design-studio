(function () {
    function enhanceKpiCards(root) {
        var scope = root || document;
        scope.querySelectorAll('.metric-card').forEach(function (card) {
            if (!card.style.getPropertyValue('--card-accent')) {
                var inlineStyle = card.getAttribute('style') || '';
                var hexMatch = inlineStyle.match(/#[0-9a-fA-F]{6}\b/);
                if (hexMatch) {
                    card.style.setProperty('--card-accent', hexMatch[0]);
                }
            }
            if (!card.querySelector('.kpi-decor-clip')) {
                var clip = document.createElement('div');
                clip.className = 'kpi-decor-clip';
                var spot = document.createElement('div');
                spot.className = 'kpi-spotlight';
                clip.appendChild(spot);
                var iconEl = card.querySelector('.bi:not(.bi-info-circle):not(.bi-calendar3):not(.bi-file-earmark-text):not(.bi-box-arrow-up-right)');
                if (iconEl) {
                    var wm = document.createElement('i');
                    var iconClasses = Array.from(iconEl.classList).filter(function (c) {
                        return c === 'bi' || c.indexOf('bi-') === 0;
                    });
                    wm.className = iconClasses.join(' ') + ' kpi-watermark-icon';
                    clip.appendChild(wm);
                }
                card.insertBefore(clip, card.firstChild);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () { enhanceKpiCards(document); });
    document.body.addEventListener('htmx:afterSettle', function (e) { enhanceKpiCards(e.target || document); });
    document.body.addEventListener('htmx:oobAfterSwap', function (e) { enhanceKpiCards(e.target || document); });

    document.addEventListener('pointermove', function (e) {
        if (!document.body || document.body.dataset.kpiSpotlight === 'false') return;
        var card = e.target && e.target.closest ? e.target.closest('.metric-card') : null;
        if (!card) return;
        var rect = card.getBoundingClientRect();
        card.style.setProperty('--mouse-x', (e.clientX - rect.left) + 'px');
        card.style.setProperty('--mouse-y', (e.clientY - rect.top) + 'px');
    }, { passive: true });
})();
