// API Base URL
const API_BASE = '/api/v1';

// Global data
let allCustomers = [];
let currentFilter = 'all';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
});

// Load all data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadCustomerScores(),
            loadFollowups()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

// Load customer scores
async function loadCustomerScores() {
    try {
        const response = await fetch(`${API_BASE}/customers/payment-scores`);
        if (!response.ok) throw new Error('Failed to fetch scores');
        
        allCustomers = await response.json();
        updateStats();
        displayCustomers(allCustomers);
    } catch (error) {
        console.error('Error loading scores:', error);
        document.getElementById('customersTableBody').innerHTML = `
            <tr><td colspan="7" class="loading-cell" style="color: var(--danger-color);">
                Failed to load customer data. Please refresh.
            </td></tr>
        `;
    }
}

// Update statistics
function updateStats() {
    const total = allCustomers.length;
    const low = allCustomers.filter(c => c.risk_level === 'low').length;
    const medium = allCustomers.filter(c => c.risk_level === 'medium').length;
    const high = allCustomers.filter(c => c.risk_level === 'high').length;
    
    document.getElementById('totalCustomers').textContent = total;
    document.getElementById('lowRiskCount').textContent = low;
    document.getElementById('mediumRiskCount').textContent = medium;
    document.getElementById('highRiskCount').textContent = high;
}

// Display customers in table
function displayCustomers(customers) {
    const tbody = document.getElementById('customersTableBody');
    
    if (customers.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="7" class="loading-cell">
                No customers found
            </td></tr>
        `;
        return;
    }
    
    tbody.innerHTML = customers.map(customer => `
        <tr>
            <td>
                <div style="font-weight: 600;">${customer.customer_name}</div>
                <div style="font-size: 12px; color: var(--gray-500);">${customer.customer_id}</div>
            </td>
            <td>
                <div class="score-display">
                    <span class="score-number" style="color: ${getScoreColor(customer.risk_level)}">${customer.score.toFixed(1)}</span>
                    <div class="score-bar">
                        <div class="score-fill ${getRiskClass(customer.risk_level)}" style="width: ${customer.score}%"></div>
                    </div>
                </div>
            </td>
            <td><span class="badge badge-${customer.risk_level}">${customer.risk_level}</span></td>
            <td>${customer.action}</td>
            <td>${customer.overdue_count} invoices</td>
            <td>$${customer.total_outstanding.toLocaleString()}</td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="showCustomerDetails('${customer.customer_id}')">
                    View Details
                </button>
            </td>
        </tr>
    `).join('');
}

// Filter customers
function filterCustomers(filter) {
    currentFilter = filter;
    
    // Update active tab
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // If filtering by 'high', call the dedicated high-risk endpoint for better performance and accuracy
    if (filter === 'high') {
        loadHighRiskCustomers();
    } else {
        // Filter client-side from already loaded data
        let filtered = allCustomers;
        if (filter !== 'all') {
            filtered = allCustomers.filter(c => c.risk_level === filter);
        }
        
        displayCustomers(filtered);
    }
}

// Load high-risk customers from dedicated endpoint
async function loadHighRiskCustomers() {
    try {
        const response = await fetch(`${API_BASE}/customers/high-risk`);
        if (!response.ok) throw new Error('Failed to fetch high-risk customers');
        
        const highRiskCustomers = await response.json();
        displayCustomers(highRiskCustomers);
    } catch (error) {
        console.error('Error loading high-risk customers:', error);
        // Fallback to client-side filtering
        const filtered = allCustomers.filter(c => c.risk_level === 'high');
        displayCustomers(filtered);
    }
}

// Search customers
function searchCustomers() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    
    let filtered = currentFilter === 'all' 
        ? allCustomers 
        : allCustomers.filter(c => c.risk_level === currentFilter);
    
    if (query) {
        filtered = filtered.filter(c => 
            c.customer_name.toLowerCase().includes(query) ||
            c.customer_id.toLowerCase().includes(query)
        );
    }
    
    displayCustomers(filtered);
}

// Load followups
async function loadFollowups() {
    try {
        const response = await fetch(`${API_BASE}/customers/followups`);
        if (!response.ok) throw new Error('Failed to fetch followups');
        
        const followups = await response.json();
        displayFollowups(followups);
    } catch (error) {
        console.error('Error loading followups:', error);
    }
}

// Display followups
function displayFollowups(followups) {
    const immediateDiv = document.getElementById('immediateFollowups');
    const reminderDiv = document.getElementById('friendlyReminders');
    
    // Immediate follow-ups
    if (followups.immediate_followup.length === 0) {
        immediateDiv.innerHTML = '<div class="loading-text" style="color: var(--success-color);">✓ No immediate actions needed</div>';
    } else {
        immediateDiv.innerHTML = followups.immediate_followup.map(item => `
            <div class="followup-item immediate" onclick="showCustomerDetails('${item.customer_id}')">
                <div class="followup-customer">${item.customer_name}</div>
                <div class="followup-details">
                    <span>Score: ${item.score.toFixed(1)}</span>
                    <span>Overdue: ${item.overdue_count}</span>
                    <span>Outstanding: $${item.total_outstanding.toLocaleString()}</span>
                </div>
            </div>
        `).join('');
    }
    
    // Friendly reminders
    if (followups.friendly_reminder.length === 0) {
        reminderDiv.innerHTML = '<div class="loading-text" style="color: var(--success-color);">✓ No reminders needed</div>';
    } else {
        reminderDiv.innerHTML = followups.friendly_reminder.map(item => `
            <div class="followup-item reminder" onclick="showCustomerDetails('${item.customer_id}')">
                <div class="followup-customer">${item.customer_name}</div>
                <div class="followup-details">
                    <span>Score: ${item.score.toFixed(1)}</span>
                    <span>Overdue: ${item.overdue_count}</span>
                    <span>Outstanding: $${item.total_outstanding.toLocaleString()}</span>
                </div>
            </div>
        `).join('');
    }
}

// Show customer details modal
async function showCustomerDetails(customerId) {
    const modal = document.getElementById('customerModal');
    const modalBody = document.getElementById('modalBody');
    
    modal.classList.add('active');
    
    // Find customer in already loaded data
    const customer = allCustomers.find(c => c.customer_id === customerId);
    
    if (!customer) {
        modalBody.innerHTML = '<div class="error-message">Customer not found</div>';
        return;
    }
    
    try {
        
        document.getElementById('modalCustomerName').textContent = customer.customer_name;
        
        modalBody.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 24px;">
                <div class="detail-section">
                    <div class="detail-label">Payment Score</div>
                    <div class="detail-value" style="font-size: 36px; font-weight: 700; color: ${getScoreColor(customer.risk_level)}">
                        ${customer.score.toFixed(1)}
                    </div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">Risk Level</div>
                    <div class="detail-value">
                        <span class="badge badge-${customer.risk_level}" style="font-size: 16px; padding: 8px 16px;">
                            ${customer.risk_level}
                        </span>
                    </div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 24px;">
                <div class="detail-section">
                    <div class="detail-label">Recommended Action</div>
                    <div class="detail-value">${customer.action}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">Payment Reliability</div>
                    <div class="detail-value">${Math.round(customer.payment_reliability)}%</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">Avg Payment Delay</div>
                    <div class="detail-value">${Math.round(customer.avg_payment_delay)} days</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">Overdue Invoices</div>
                    <div class="detail-value">${customer.overdue_count}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">Total Invoices</div>
                    <div class="detail-value">${customer.total_invoices}</div>
                </div>
                <div class="detail-section">
                    <div class="detail-label">Total Outstanding</div>
                    <div class="detail-value">$${customer.total_outstanding.toLocaleString()}</div>
                </div>
            </div>
            
            <div class="detail-section">
                <div class="detail-label">Insights</div>
                <div class="insights-box">
                    ${customer.insights || 'No insights available'}
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading customer details:', error);
        modalBody.innerHTML = `
            <div style="text-align: center; color: var(--danger-color); padding: 40px;">
                Failed to load customer details
            </div>
        `;
    }
}

// Close modal
function closeModal() {
    document.getElementById('customerModal').classList.remove('active');
}

// Close modal on outside click
document.getElementById('customerModal').addEventListener('click', (e) => {
    if (e.target.id === 'customerModal') {
        closeModal();
    }
});

// Refresh data
async function refreshData() {
    const btn = event.target.closest('button');
    btn.style.animation = 'spin 0.8s linear infinite';
    
    await loadDashboardData();
    
    btn.style.animation = '';
}

// Helper functions
function getRiskClass(riskLevel) {
    return riskLevel === 'low' ? 'low' : riskLevel === 'medium' ? 'medium' : 'high';
}

function getScoreColor(riskLevel) {
    if (riskLevel === 'low') return 'var(--success-color)';
    if (riskLevel === 'medium') return 'var(--warning-color)';
    return 'var(--danger-color)';
}

function showError(message) {
    console.error(message);
}
