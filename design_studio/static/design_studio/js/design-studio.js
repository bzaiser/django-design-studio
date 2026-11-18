(function () {
    function isTouchPrimary() {
        return !!(window.matchMedia && window.matchMedia('(hover: none), (pointer: coarse)').matches);
    }

    function toggleTouchKpiDetails(card) {
        if (!card) return false;
        var details = card.querySelector('.widget-hover-details');
        if (!details) return false;
        var willExpand = !card.classList.contains('is-touch-expanded');
        var parentRow = card.closest('.kpi-bento-grid, .row');
        if (parentRow && willExpand) {
            parentRow.querySelectorAll('.widget-expand-card.is-touch-expanded').forEach(function (other) {
                if (other !== card) other.classList.remove('is-touch-expanded');
            });
        }
        card.classList.toggle('is-touch-expanded', willExpand);
        return true;
    }

    window.navigateDesignStudioKpiCard = function (evt, targetUrl) {
        if (evt && evt.target && evt.target.closest('a, button, input, select, .bi-info-circle')) return;
        var card = evt && evt.currentTarget ? evt.currentTarget : (evt && evt.target && evt.target.closest ? evt.target.closest('.metric-card') : null);
        if (isTouchPrimary() && card && card.querySelector('.widget-hover-details')) {
            if (evt && evt.target && evt.target.closest('.widget-hover-details')) return;
            toggleTouchKpiDetails(card);
            return;
        }
        if (evt && evt.target && evt.target.closest('.widget-hover-details')) return;
        if (!document.body || document.body.dataset.kpiClick === 'false' || !targetUrl) return;
        window.location.href = targetUrl;
    };

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
                var iconEl = card.querySelector('.bi:not(.bi-info-circle):not(.bi-calendar3):not(.bi-file-earmark-text):not(.bi-box-arrow-up-right):not(.bi-arrow-up-right):not(.bi-arrow-right):not(.bi-chevron-down)');
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
            var targetUrl = card.getAttribute('data-target-url');
            var detailsEl = card.querySelector('.widget-hover-details');
            if (targetUrl && !card.querySelector('.kpi-nav-pill')) {
                var headerRow = card.querySelector('.card-body > .d-flex.justify-content-between') || card.querySelector('.d-flex.justify-content-between');
                if (headerRow) {
                    var pill = document.createElement('a');
                    pill.href = targetUrl;
                    pill.className = 'kpi-nav-pill ms-2';
                    pill.title = 'Zur Detailseite';
                    pill.setAttribute('aria-label', 'Zur Detailseite');
                    pill.innerHTML = '<i class="bi bi-arrow-up-right"></i>';
                    pill.addEventListener('click', function (ev) { ev.stopPropagation(); });
                    headerRow.appendChild(pill);
                }
            }
            if (detailsEl) {
                if (targetUrl && !detailsEl.querySelector('.kpi-details-nav-link')) {
                    var footerLink = document.createElement('a');
                    footerLink.href = targetUrl;
                    footerLink.className = 'kpi-details-nav-link';
                    footerLink.innerHTML = '<span>Zur Detailseite</span><i class="bi bi-arrow-right ms-1"></i>';
                    footerLink.addEventListener('click', function (ev) { ev.stopPropagation(); });
                    detailsEl.appendChild(footerLink);
                }
                if (!card.querySelector('.kpi-expand-hint')) {
                    var metricVal = card.querySelector('.metric-value') || card.querySelector('.card-body') || card;
                    var hint = document.createElement('div');
                    hint.className = 'kpi-expand-hint';
                    hint.setAttribute('aria-hidden', 'true');
                    hint.innerHTML = '<i class="bi bi-chevron-down"></i>';
                    metricVal.appendChild(hint);
                }
                if (!card.dataset.kpiTouchBound) {
                    card.dataset.kpiTouchBound = '1';
                    var onclickAttr = card.getAttribute('onclick') || '';
                    if (onclickAttr.indexOf('navigateDesignStudioKpiCard') === -1) {
                        card.addEventListener('click', function (ev) {
                            if (!isTouchPrimary()) return;
                            if (ev.target && ev.target.closest('a, button, input, select, .bi-info-circle, .widget-hover-details')) return;
                            toggleTouchKpiDetails(card);
                        });
                    }
                }
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
