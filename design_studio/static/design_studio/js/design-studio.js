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

    function animateKpiCounters(root) {
        if (document.body && document.body.getAttribute('data-kpi-animate') === 'false') return;
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        var scope = (root && root.querySelectorAll) ? root : document;
        scope.querySelectorAll('.metric-card h3, .metric-card h4').forEach(function (hEl) {
            if (hEl.dataset.kpiAnimated === '1') return;
            var targetNode = null;
            for (var i = 0; i < hEl.childNodes.length; i++) {
                var n = hEl.childNodes[i];
                if (n.nodeType === 3 && /\d/.test(n.nodeValue)) { targetNode = n; break; }
            }
            if (!targetNode) return;
            var raw = targetNode.textContent;
            var m = raw.match(/^(\s*[+\-−]?\s*)(\d[\d.,]*)(.*)$/);
            if (!m) return;
            var prefix = m[1], numStr = m[2], suffix = m[3];
            var decMatch = numStr.match(/([.,])(\d{1,2})$/);
            var decimals = 0, decSep = ',', thouSep = '.', clean = numStr;
            if (decMatch && !(numStr.indexOf('.') !== -1 && decMatch[1] === '.' && decMatch[2].length === 3)) {
                if (decMatch[1] === ',' || decMatch[2].length <= 2) {
                    decimals = decMatch[2].length;
                    decSep = decMatch[1];
                    thouSep = decSep === ',' ? '.' : ',';
                    clean = numStr.slice(0, numStr.length - decMatch[0].length).replace(/[.,]/g, '') + '.' + decMatch[2];
                }
            } else {
                clean = numStr.replace(/[.,]/g, '');
                if (numStr.indexOf(',') !== -1 && numStr.indexOf('.') === -1) thouSep = ',';
            }
            var targetVal = parseFloat(clean);
            if (isNaN(targetVal) || targetVal === 0) return;
            hEl.dataset.kpiAnimated = '1';
            var duration = 650, startTs = null;
            function formatVal(val) {
                var fixed = val.toFixed(decimals);
                var parts = fixed.split('.');
                var intPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, thouSep);
                return decimals > 0 ? intPart + decSep + parts[1] : intPart;
            }
            function step(ts) {
                if (!startTs) startTs = ts;
                var p = Math.min(1, (ts - startTs) / duration);
                var eased = 1 - Math.pow(1 - p, 3);
                targetNode.textContent = prefix + formatVal(targetVal * eased) + suffix;
                if (p < 1) requestAnimationFrame(step);
                else targetNode.textContent = raw;
            }
            requestAnimationFrame(step);
        });
    }
    document.addEventListener('DOMContentLoaded', function () { animateKpiCounters(document); });
    document.body.addEventListener('htmx:afterSettle', function (e) { animateKpiCounters(e.target || document); });
    document.body.addEventListener('htmx:oobAfterSwap', function (e) { animateKpiCounters(e.target || document); });

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
        if (sbBtn && !sbBtn.dataset.dsSidebarBound) {
            sbBtn.dataset.dsSidebarBound = '1';
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

        // Hoist modals to document.body so table-responsive/card/backdrop-filter stacking contexts never trap them behind backdrop
        document.querySelectorAll('.modal').forEach(function (m) {
            if (m.parentNode !== document.body) document.body.appendChild(m);
        });
    });

    document.addEventListener('show.bs.modal', function (e) {
        if (e.target && e.target.parentNode !== document.body) {
            document.body.appendChild(e.target);
        }
    });

    function updateLiquidGlassOptics() {
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
        var bgLayer = document.querySelector('.app-bg-svg-layer');
        if (bgLayer) {
            var scrollY = window.scrollY || window.pageYOffset || 0;
            bgLayer.style.transform = 'translate3d(0, ' + (-(scrollY * 0.08)).toFixed(1) + 'px, 0)';
        }
        if (!document.body || document.body.getAttribute('data-card-surface') !== 'liquid') return;
        var vh = window.innerHeight || 800;
        document.querySelectorAll('.card, .metric-card, .ds-tab-panel').forEach(function (card) {
            var rect = card.getBoundingClientRect();
            var centerProgress = ((rect.top + rect.height / 2) - vh / 2) / (vh / 2);
            var clamped = Math.max(-1.2, Math.min(1.2, centerProgress));
            var shinePos = 50 + clamped * 38;
            var shineAngle = 125 + clamped * 22;
            card.style.setProperty('--shine-pos', shinePos.toFixed(1) + '%');
            card.style.setProperty('--shine-angle', shineAngle.toFixed(1) + 'deg');
        });
    }
    window.addEventListener('scroll', function () {
        requestAnimationFrame(updateLiquidGlassOptics);
    }, { passive: true });
    window.addEventListener('resize', updateLiquidGlassOptics, { passive: true });
    document.addEventListener('DOMContentLoaded', updateLiquidGlassOptics);

    function updateSeamlessPlate(tabBar, panel) {
        if (!tabBar || !panel) return;
        if (document.body && document.body.getAttribute('data-card-surface') === 'brutal') {
            tabBar.classList.remove('ds-tabs-seamless');
            panel.classList.remove('ds-plate-ready');
            panel.style.removeProperty('--ds-plate-clip');
            return;
        }
        var activeLink = tabBar.querySelector('.nav-link.active');
        var allLinks = tabBar.querySelectorAll('.nav-link');
        if (!activeLink || !allLinks.length) return;
        var firstTop = allLinks[0].getBoundingClientRect().top;
        var isSingleRow = true;
        allLinks.forEach(function (lnk) {
            if (Math.abs(lnk.getBoundingClientRect().top - firstTop) > 10) isSingleRow = false;
        });
        if (!isSingleRow || window.innerWidth < 576) {
            tabBar.classList.remove('ds-tabs-seamless');
            panel.classList.remove('ds-plate-ready');
            panel.style.removeProperty('--ds-plate-clip');
            var oldSvg = panel.querySelector('.ds-tab-outline-svg');
            if (oldSvg) oldSvg.style.display = 'none';
            return;
        }
        var tabH = Math.round(tabBar.offsetHeight) || Math.round(activeLink.offsetHeight) || 44;
        tabBar.style.setProperty('--ds-tab-h', tabH + 'px');
        panel.style.setProperty('--ds-tab-h', tabH + 'px');
        tabBar.classList.add('ds-tabs-seamless');
        panel.classList.add('ds-plate-ready');

        var pRect = panel.getBoundingClientRect();
        var aRect = activeLink.getBoundingClientRect();
        var w = Math.round(panel.offsetWidth);
        var h = Math.round(panel.offsetHeight);
        if (w < 40 || h < tabH + 20) return;

        var scale = (pRect.width > 0 && w > 0) ? (pRect.width / w) : 1;
        var x1 = Math.round(Math.max(0, (aRect.left - pRect.left) / scale));
        var x2 = Math.round(Math.min(w, (aRect.right - pRect.left) / scale));
        var r = 22, tr = 14, flare = 12;
        var d = '';
        if (x1 <= 6) {
            d = 'M 0,' + tr + ' Q 0,0 ' + tr + ',0 L ' + (x2 - tr) + ',0 Q ' + x2 + ',0 ' + x2 + ',' + tr +
                ' L ' + x2 + ',' + (tabH - flare) + ' Q ' + x2 + ',' + tabH + ' ' + (x2 + flare) + ',' + tabH +
                ' L ' + (w - r) + ',' + tabH + ' Q ' + w + ',' + tabH + ' ' + w + ',' + (tabH + r) +
                ' L ' + w + ',' + (h - r) + ' Q ' + w + ',' + h + ' ' + (w - r) + ',' + h +
                ' L ' + r + ',' + h + ' Q 0,' + h + ' 0,' + (h - r) + ' Z';
        } else if (x2 >= w - 6) {
            d = 'M 0,' + (tabH + r) + ' Q 0,' + tabH + ' ' + r + ',' + tabH +
                ' L ' + (x1 - flare) + ',' + tabH + ' Q ' + x1 + ',' + tabH + ' ' + x1 + ',' + (tabH - flare) +
                ' L ' + x1 + ',' + tr + ' Q ' + x1 + ',0 ' + (x1 + tr) + ',0' +
                ' L ' + (w - tr) + ',0 Q ' + w + ',0 ' + w + ',' + tr +
                ' L ' + w + ',' + (h - r) + ' Q ' + w + ',' + h + ' ' + (w - r) + ',' + h +
                ' L ' + r + ',' + h + ' Q 0,' + h + ' 0,' + (h - r) + ' Z';
        } else {
            d = 'M 0,' + (tabH + r) + ' Q 0,' + tabH + ' ' + r + ',' + tabH +
                ' L ' + (x1 - flare) + ',' + tabH + ' Q ' + x1 + ',' + tabH + ' ' + x1 + ',' + (tabH - flare) +
                ' L ' + x1 + ',' + tr + ' Q ' + x1 + ',0 ' + (x1 + tr) + ',0' +
                ' L ' + (x2 - tr) + ',0 Q ' + x2 + ',0 ' + x2 + ',' + tr +
                ' L ' + x2 + ',' + (tabH - flare) + ' Q ' + x2 + ',' + tabH + ' ' + (x2 + flare) + ',' + tabH +
                ' L ' + (w - r) + ',' + tabH + ' Q ' + w + ',' + tabH + ' ' + w + ',' + (tabH + r) +
                ' L ' + w + ',' + (h - r) + ' Q ' + w + ',' + h + ' ' + (w - r) + ',' + h +
                ' L ' + r + ',' + h + ' Q 0,' + h + ' 0,' + (h - r) + ' Z';
        }
        var clipVal = "path('" + d + "')";
        panel.style.setProperty('--ds-plate-clip', clipVal);
        panel.style.clipPath = clipVal;
        panel.style.webkitClipPath = clipVal;

        var svg = panel.querySelector('.ds-tab-outline-svg');
        if (!svg) {
            svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('class', 'ds-tab-outline-svg');
            svg.setAttribute('aria-hidden', 'true');
            var pathEl = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            pathEl.setAttribute('class', 'ds-tab-outline-path');
            svg.appendChild(pathEl);
            panel.insertBefore(svg, panel.firstChild);
        }
        svg.style.display = '';
        svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
        var outlinePath = svg.querySelector('.ds-tab-outline-path');
        if (outlinePath) outlinePath.setAttribute('d', d);
    }

    function initSeamlessTabPlates() {
        document.querySelectorAll('.folder-tabs-bar').forEach(function (bar) {
            var next = bar.nextElementSibling;
            if (next && next.classList.contains('tab-content') && !next.classList.contains('ds-tab-panel')) {
                next.classList.add('ds-tab-panel');
            }
        });
        document.querySelectorAll('.ds-tab-panel').forEach(function (panel) {
            var tabBar = panel.previousElementSibling;
            if (!tabBar || (!tabBar.classList.contains('nav-tabs') && !tabBar.classList.contains('folder-tabs-bar'))) return;
            updateSeamlessPlate(tabBar, panel);
            if (!panel.dataset.dsPlateObserved && typeof ResizeObserver !== 'undefined') {
                panel.dataset.dsPlateObserved = '1';
                new ResizeObserver(function () {
                    updateSeamlessPlate(tabBar, panel);
                }).observe(panel);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initSeamlessTabPlates);
    window.addEventListener('load', initSeamlessTabPlates);
    window.addEventListener('resize', initSeamlessTabPlates, { passive: true });
    document.addEventListener('shown.bs.tab', initSeamlessTabPlates);
    document.body.addEventListener('htmx:afterSettle', initSeamlessTabPlates);
})();
