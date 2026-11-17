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

(function () {
    document.addEventListener('DOMContentLoaded', function () {
        try {
            if (localStorage.getItem('ds_sidebar_collapsed') === '1') {
                document.body.classList.add('sidebar-collapsed');
            }
        } catch (err) {}
        var sbBtn = document.getElementById('sidebarCollapseBtn');
        if (sbBtn) {
            sbBtn.addEventListener('click', function () {
                document.body.classList.toggle('sidebar-collapsed');
                try {
                    localStorage.setItem('ds_sidebar_collapsed', document.body.classList.contains('sidebar-collapsed') ? '1' : '0');
                } catch (err) {}
            });
        }

        document.querySelectorAll('.nav-pill-track').forEach(function (track) {
            var pill = track.querySelector('.nav-sliding-pill');
            if (!pill) return;
            var currentTarget = null;
            function movePillTo(el) {
                if (!el || window.innerWidth < 992) {
                    pill.style.opacity = '0';
                    return;
                }
                var tRect = track.getBoundingClientRect();
                var elRect = el.getBoundingClientRect();
                pill.style.width = elRect.width + 'px';
                pill.style.height = elRect.height + 'px';
                pill.style.transform = 'translate3d(' + (elRect.left - tRect.left) + 'px, ' + (elRect.top - tRect.top) + 'px, 0)';
                pill.style.opacity = '1';
            }
            track.querySelectorAll('.nav-link').forEach(function (link) {
                link.addEventListener('pointerenter', function () {
                    currentTarget = link;
                    movePillTo(link);
                });
            });
            track.addEventListener('pointerleave', function () {
                currentTarget = null;
                pill.style.opacity = '0';
            });
            window.addEventListener('resize', function () {
                if (currentTarget) movePillTo(currentTarget);
            }, { passive: true });
        });
    });
})();
