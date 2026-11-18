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

    function activateKpiTarget(card, targetUrl, targetTab) {
        if (!document.body || document.body.dataset.kpiClick === 'false') return;
        if (targetTab) {
            var alpineRoot = card ? card.closest('[x-data]') : null;
            if (alpineRoot && alpineRoot._x_dataStack && alpineRoot._x_dataStack[0]) {
                var data = alpineRoot._x_dataStack[0];
                if (typeof data.setTab === 'function') {
                    data.setTab(targetTab);
                } else if ('activeTab' in data) {
                    data.activeTab = targetTab;
                }
            }
            var scrollAnchor = document.querySelector('.folder-tabs-bar') ||
                               (card && card.closest('.row, .kpi-bento-grid') ? card.closest('.row, .kpi-bento-grid').nextElementSibling : null);
            if (scrollAnchor && typeof scrollAnchor.scrollIntoView === 'function') {
                setTimeout(function () {
                    scrollAnchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 60);
            }
            return;
        }
        if (targetUrl) {
            window.location.href = targetUrl;
        }
    }

    window.navigateDesignStudioKpiCard = function (evt, targetUrl) {
        if (evt && evt.target && evt.target.closest('a, button, input, select, .bi-info-circle, .kpi-nav-pill, .kpi-details-nav-link')) return;
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
            var targetTab = card.getAttribute('data-target-tab');
            if (!targetTab) {
                var alpineClick = card.getAttribute('@click') || card.getAttribute('x-on:click') || '';
                var mTab = alpineClick.match(/setTab\(\s*['"]([^'"]+)['"]\s*\)/);
                if (mTab) {
                    targetTab = mTab[1];
                    card.setAttribute('data-target-tab', targetTab);
                }
            }
            var detailsEl = card.querySelector('.widget-hover-details');
            if (detailsEl && detailsEl.parentElement && detailsEl.parentElement !== card && detailsEl.parentElement.classList.contains('card-body')) {
                card.appendChild(detailsEl);
            }
            if ((targetUrl || targetTab) && !card.querySelector('.kpi-nav-pill')) {
                var headerRow = card.querySelector('.card-body > .d-flex.justify-content-between') || card.querySelector('.d-flex.justify-content-between');
                if (headerRow) {
                    var pill = document.createElement('a');
                    pill.href = targetUrl || 'javascript:void(0)';
                    pill.className = 'kpi-nav-pill ms-2';
                    pill.title = targetTab ? 'Zum Bereich springen' : 'Zur Detailseite';
                    pill.setAttribute('aria-label', pill.title);
                    pill.innerHTML = '<i class="bi bi-arrow-up-right"></i>';
                    pill.addEventListener('click', function (ev) {
                        ev.stopPropagation();
                        if (targetTab) {
                            ev.preventDefault();
                            activateKpiTarget(card, null, targetTab);
                        }
                    });
                    headerRow.appendChild(pill);
                }
            }
            if (detailsEl) {
                if ((targetUrl || targetTab) && !detailsEl.querySelector('.kpi-details-nav-link')) {
                    var footerLink = document.createElement('a');
                    footerLink.href = targetUrl || 'javascript:void(0)';
                    footerLink.className = 'kpi-details-nav-link';
                    footerLink.innerHTML = '<span>' + (targetTab ? 'Zum Bereich' : 'Zur Detailseite') + '</span><i class="bi bi-arrow-right ms-1"></i>';
                    footerLink.addEventListener('click', function (ev) {
                        ev.stopPropagation();
                        if (targetTab) {
                            ev.preventDefault();
                            activateKpiTarget(card, null, targetTab);
                        }
                    });
                    detailsEl.appendChild(footerLink);
                }
                if (!card.querySelector('.kpi-expand-hint')) {
                    var metricVal = card.querySelector('.metric-value') || card.querySelector('.card-body') || card;
                    var hint = document.createElement('div');
                    hint.className = 'kpi-expand-hint';
                    hint.setAttribute('aria-hidden', 'true');
                    hint.innerHTML = '<i class="bi bi-chevron-down"></i>';
                    if (metricVal === card && detailsEl.parentElement === card) {
                        card.insertBefore(hint, detailsEl);
                    } else {
                        metricVal.appendChild(hint);
                    }
                }
            }
            if (!card.dataset.kpiTouchBound) {
                card.dataset.kpiTouchBound = '1';
                var onclickAttr = card.getAttribute('onclick') || '';
                if (onclickAttr.indexOf('navigateDesignStudioKpiCard') === -1) {
                    card.addEventListener('click', function (ev) {
                        if (ev.target && ev.target.closest('a, button, input, select, .bi-info-circle, .kpi-nav-pill, .kpi-details-nav-link, .widget-hover-details')) return;
                        if (isTouchPrimary() && detailsEl) {
                            ev.stopPropagation();
                            toggleTouchKpiDetails(card);
                            return;
                        }
                        if (targetTab && !(card.hasAttribute('@click') || card.hasAttribute('x-on:click'))) {
                            activateKpiTarget(card, targetUrl, targetTab);
                        }
                    }, true);
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
