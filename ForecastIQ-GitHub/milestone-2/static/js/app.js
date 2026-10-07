/* ============================================================
   ForecastinQ – App JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

    // === SIDEBAR TOGGLE ===
    const sidebar        = document.getElementById('sidebar');
    const toggleSidebar  = document.getElementById('toggleSidebar');
    const sidebarClose   = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    function openSidebar()  { sidebar?.classList.add('open'); sidebarOverlay?.classList.add('open'); }
    function closeSidebar() { sidebar?.classList.remove('open'); sidebarOverlay?.classList.remove('open'); }

    toggleSidebar?.addEventListener('click', () => sidebar?.classList.contains('open') ? closeSidebar() : openSidebar());
    sidebarClose?.addEventListener('click', closeSidebar);
    sidebarOverlay?.addEventListener('click', closeSidebar);

    // === THEME TOGGLE ===
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon   = document.getElementById('themeIcon');
    const html        = document.documentElement;

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        document.cookie = `theme=${theme};path=/;max-age=31536000`;
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
        }
    }

    // Init from cookie
    const savedTheme = document.cookie.split(';').find(c => c.trim().startsWith('theme='));
    if (savedTheme) applyTheme(savedTheme.split('=')[1].trim());

    themeToggle?.addEventListener('click', () => {
        const current = html.getAttribute('data-theme') || 'light';
        applyTheme(current === 'dark' ? 'light' : 'dark');
    });

    // === AUTO-DISMISS FLASH MESSAGES ===
    setTimeout(() => {
        document.querySelectorAll('.flash-message').forEach(el => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            bsAlert?.close();
        });
    }, 5000);

    // === CONFIRM DELETE ===
    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', e => {
            if (!confirm(btn.dataset.confirm || 'Are you sure?')) e.preventDefault();
        });
    });

    // === SEARCH FILTER (client-side table) ===
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const q = searchInput.value.toLowerCase();
            document.querySelectorAll('tbody tr').forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
            });
        });
    }

    // === CHART DEFAULTS ===
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
    Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#64748b';

    // === STOCK BAR ANIMATION ===
    document.querySelectorAll('.stock-fill').forEach(bar => {
        const pct = bar.dataset.pct || 0;
        setTimeout(() => bar.style.width = pct + '%', 100);
    });

    // === TOOLTIP INIT ===
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));

});

// === CHART HELPERS ===
function getChartColors() {
    return {
        primary:  '#4f46e5',
        accent:   '#06b6d4',
        success:  '#10b981',
        warning:  '#f59e0b',
        danger:   '#ef4444',
        grid:     getComputedStyle(document.documentElement).getPropertyValue('--border').trim() || '#e2e8f0',
        text:     getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#64748b',
    };
}

function buildLineChart(ctx, labels, datasets, options = {}) {
    const c = getChartColors();
    return new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' }, tooltip: { mode: 'index' } },
            scales: {
                x: { grid: { color: c.grid }, ticks: { color: c.text } },
                y: { grid: { color: c.grid }, ticks: { color: c.text } },
            },
            ...options
        }
    });
}

function buildBarChart(ctx, labels, datasets, options = {}) {
    const c = getChartColors();
    return new Chart(ctx, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                x: { grid: { display: false }, ticks: { color: c.text } },
                y: { grid: { color: c.grid }, ticks: { color: c.text } },
            },
            ...options
        }
    });
}

function buildDoughnutChart(ctx, labels, data, colors) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{ data, backgroundColor: colors, borderWidth: 2, borderColor: 'transparent', hoverOffset: 6 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: { legend: { position: 'right' } }
        }
    });
}
