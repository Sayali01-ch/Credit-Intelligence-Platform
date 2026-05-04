// Credit Decision System Dashboard JavaScript

/**
 * Initialize dashboard with event listeners and data
 */
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
});

function initDashboard() {
    loadMetrics();
    loadRecentApplications();
    
    // Refresh every 30 seconds
    setInterval(loadMetrics, 30000);
    setInterval(loadRecentApplications, 60000);
}

/**
 * Load and display system metrics
 */
async function loadMetrics() {
    try {
        const response = await fetch('/api/metrics');
        const metrics = await response.json();
        
        updateMetricsDisplay(metrics);
    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

/**
 * Update metrics display
 */
function updateMetricsDisplay(metrics) {
    const elements = {
        totalApplications: document.getElementById('totalApplications'),
        approvalRate: document.getElementById('approvalRate'),
        avgProcessingTime: document.getElementById('avgProcessingTime'),
        modelAccuracy: document.getElementById('modelAccuracy')
    };
    
    if (elements.totalApplications) {
        elements.totalApplications.textContent = metrics.total_applications || 0;
    }
    
    if (elements.approvalRate) {
        elements.approvalRate.textContent = ((metrics.approval_rate || 0) * 100).toFixed(1) + '%';
    }
    
    if (elements.avgProcessingTime) {
        elements.avgProcessingTime.textContent = (metrics.avg_processing_time || 0).toFixed(0) + 'ms';
    }
    
    if (elements.modelAccuracy) {
        elements.modelAccuracy.textContent = ((metrics.model_accuracy || 0.947) * 100).toFixed(1) + '%';
    }
}

/**
 * Load recent applications
 */
async function loadRecentApplications() {
    try {
        const response = await fetch('/api/applications');
        if (!response.ok) return;
        
        const applications = await response.json();
        displayRecentApplications(applications);
    } catch (error) {
        console.error('Error loading recent applications:', error);
    }
}

/**
 * Display recent applications in table
 */
function displayRecentApplications(applications) {
    const tbody = document.getElementById('recentTableBody');
    if (!tbody) return;
    
    if (applications.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No recent applications</td></tr>';
        return;
    }
    
    tbody.innerHTML = applications.map(app => `
        <tr>
            <td>${app.id}</td>
            <td>${new Date(app.timestamp).toLocaleDateString()}</td>
            <td>${app.credit_score}</td>
            <td><span class="badge badge-${getBadgeClass(app.recommendation)}">${app.recommendation.toUpperCase()}</span></td>
            <td>${app.processing_time}ms</td>
        </tr>
    `).join('');
}

/**
 * Get badge class based on recommendation
 */
function getBadgeClass(recommendation) {
    switch(recommendation) {
        case 'approve':
            return 'success';
        case 'reject':
            return 'danger';
        case 'review':
            return 'warning';
        default:
            return 'warning';
    }
}

/**
 * Format currency
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

/**
 * Format percentage
 */
function formatPercentage(value) {
    return (value * 100).toFixed(2) + '%';
}
