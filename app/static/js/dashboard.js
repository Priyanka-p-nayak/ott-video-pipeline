// Dashboard logic: fetch real data from our Flask APIs and populate the page.

async function loadSummaryStats() {
    try {
        const response = await fetch('/stats/summary');
        const data = await response.json();

        document.getElementById('total-videos').textContent = data.total_videos;
        document.getElementById('total-views').textContent = data.total_views;
        document.getElementById('avg-watch-time').textContent = data.average_watch_time_seconds + 's';
        document.getElementById('concurrent-viewers').textContent = data.concurrent_viewers;
    } catch (error) {
        console.error('Failed to load summary stats:', error);
    }
}

async function loadVideoList() {
    try {
        const response = await fetch('/videos/list');
        const data = await response.json();

        const tbody = document.getElementById('video-list-body');
        tbody.innerHTML = '';

        if (data.videos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No videos uploaded yet</td></tr>';
            return;
        }

        data.videos.forEach(video => {
            const row = document.createElement('tr');
            const progressPercent = video.status === 'completed' ? 100
                : video.status === 'processing' ? 50
                : video.status === 'failed' ? 100
                : 10;
            const progressColor = video.status === 'completed' ? 'bg-success'
                : video.status === 'failed' ? 'bg-danger'
                : 'bg-primary';

            row.innerHTML = `
                <td><code>${video.job_id.substring(0, 8)}...</code></td>
                <td><span class="badge ${badgeClassFor(video.status)}">${video.status}</span></td>
                <td>
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar ${progressColor}" style="width: ${progressPercent}%"></div>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Failed to load video list:', error);
    }
}

function badgeClassFor(status) {
    switch (status) {
        case 'completed': return 'bg-success';
        case 'processing': return 'bg-primary';
        case 'failed': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

function renderViewsChart() {
    const ctx = document.getElementById('viewsChart');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Views',
                data: [12, 19, 8, 15, 22, 30, 18],
                borderColor: '#4e5fff',
                backgroundColor: 'rgba(78, 95, 255, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

function renderEventChart() {
    const ctx = document.getElementById('eventChart');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Play', 'Pause', 'Buffer', 'Complete'],
            datasets: [{
                data: [45, 20, 10, 25],
                backgroundColor: ['#4e5fff', '#ffb020', '#ff5252', '#22c55e']
            }]
        },
        options: { responsive: true }
    });
}

// Run everything once the page has fully loaded
document.addEventListener('DOMContentLoaded', () => {
    loadSummaryStats();
    loadVideoList();
    renderViewsChart();
    renderEventChart();

    // Auto-refresh stats and video list every 5 seconds
    setInterval(() => {
        loadSummaryStats();
        loadVideoList();
    }, 5000);
});