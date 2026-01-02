/**
 * OpenCode Usage Dashboard - Main JavaScript
 *
 * Client-side dashboard logic that fetches live data from /api/data
 * and renders multiple views: overview, sessions, models, providers, tools, optimization
 */

// ============================================================================
// Configuration & Constants
// ============================================================================

// Color palette for model visualization (consistent across charts and progress bars)
const modelColors = {
    'Claude Sonnet 4.5 (AWS Bedrock)': '#3B82F6',
    'Claude Haiku 4.5 (AWS Bedrock)': '#60A5FA',
    'Gemini 2.5 Pro (Google)': '#10B981',
    'Gemini 2.5 Flash (Google)': '#34D399',
    'Gemini 2.5 Flash Lite (Google)': '#6EE7B7',
    'Gemini 3.0 Pro Preview (Google)': '#8B5CF6',
    'Amazon.Nova Pro (AWS Bedrock)': '#F59E0B',
    // Fallback for old names without provider
    'Claude Sonnet 4.5': '#3B82F6',
    'Claude Haiku 4.5': '#60A5FA',
    'Gemini 2.5 Pro': '#10B981',
    'Gemini 2.5 Flash': '#34D399',
    'Gemini 2.5 Flash Lite': '#6EE7B7',
    'Gemini 3.0 Pro Preview': '#8B5CF6',
    'Amazon.Nova Pro': '#F59E0B',
    'default': '#6B7280'
};

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Formats large numbers with K/M suffixes
 * @param {number} num - Number to format
 * @returns {string} Formatted number (e.g., "1.5M", "23.4K")
 */
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

/**
 * Formats cost values as currency
 * @param {number} cost - Cost value
 * @returns {string} Formatted cost (e.g., "$12.45")
 */
function formatCost(cost) {
    return '$' + cost.toFixed(2);
}

/**
 * Formats percentage values
 * @param {number} value - Percentage value
 * @returns {string} Formatted percentage (e.g., "85.3%")
 */
function formatPercent(value) {
    return value.toFixed(1) + '%';
}

/**
 * Calculates maximum cost from model list (for normalizing progress bars)
 * @param {Array} models - Array of model objects with cost property
 * @returns {number} Maximum cost value
 */
function calculateMaxCost(models) {
    return Math.max(...models.map(m => m.cost));
}

/**
 * Gets the color for a specific model name
 * @param {string} modelName - Model name
 * @returns {string} Hex color code
 */
function getModelColor(modelName) {
    return modelColors[modelName] || modelColors['default'];
}

// ============================================================================
// Page Renderers
// ============================================================================

/**
 * Page generator functions that return HTML for each dashboard view
 * Each function reads from window.opencodeData and returns formatted HTML
 */
const pages = {
    overview: function() {
        const data = window.opencodeData;
        const topModels = data.models.slice(0, 5);
        const recentSessions = data.sessions.slice(0, 5);
        const maxModelCost = calculateMaxCost(topModels);
        
        const inputPct = ((data.totals.inputTokens / data.totals.tokens) * 100).toFixed(1);
        const outputPct = ((data.totals.outputTokens / data.totals.tokens) * 100).toFixed(1);
        
        return `
            <main class="space-y-6">
                <!-- Info Box: Cache Explanation -->
                <div class="p-4 bg-purple-600/10 border border-purple-600/30 rounded-lg">
                    <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-purple-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <div class="text-sm">
                            <p class="text-purple-300 font-medium mb-1">About LLM Prompt Caching</p>
                            <p class="text-purple-200/80"><strong>This dashboard tracks LLM-level prompt caching</strong> (AWS Bedrock, Google AI), which caches repeated context in prompts to reduce costs by ~90% on cached tokens. This is different from Vector DB caching (personal-knowledge MCP), which is not currently tracked in OpenCode message logs.</p>
                        </div>
                    </div>
                </div>
                
                <!-- KPI Cards -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- Total Cost -->
                    <div class="bg-dark-surface border border-dark-border rounded-xl p-6 card-hover animate-slide-in">
                        <div class="flex items-start justify-between mb-4">
                            <div>
                                <p class="text-sm text-gray-400 mb-1">Total Cost</p>
                                <h3 class="text-3xl font-bold text-white">${formatCost(data.totals.cost)}</h3>
                            </div>
                            <div class="p-3 bg-blue-600/20 rounded-lg">
                                <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="text-sm text-gray-400">${data.totals.sessionCount} sessions</div>
                    </div>
                    
                    <!-- Total Tokens -->
                    <div class="bg-dark-surface border border-dark-border rounded-xl p-6 card-hover animate-slide-in" style="animation-delay: 0.1s;">
                        <div class="flex items-start justify-between mb-4">
                            <div>
                                <p class="text-sm text-gray-400 mb-1">Total Tokens</p>
                                <h3 class="text-3xl font-bold text-white">${formatNumber(data.totals.tokens)}</h3>
                            </div>
                            <div class="p-3 bg-green-600/20 rounded-lg">
                                <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="flex items-center gap-2">
                            <div class="flex-1 bg-dark-bg rounded-full h-2 overflow-hidden">
                                <div class="bg-green-500 h-full" style="width: ${inputPct}%;"></div>
                            </div>
                            <span class="text-sm text-gray-400">${inputPct}% input</span>
                        </div>
                    </div>
                    
                    <!-- Cache Efficiency -->
                    <div class="bg-dark-surface border border-dark-border rounded-xl p-6 card-hover animate-slide-in" style="animation-delay: 0.2s;">
                        <div class="flex items-start justify-between mb-4">
                            <div>
                                <p class="text-sm text-gray-400 mb-1">LLM Prompt Cache</p>
                                <h3 class="text-3xl font-bold text-white">${formatNumber(data.totals.cacheReadTokens)}</h3>
                            </div>
                            <div class="p-3 bg-purple-600/20 rounded-lg">
                                <svg class="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="text-sm text-gray-400">
                            ${formatPercent((data.totals.cacheReadTokens / (data.totals.inputTokens + data.totals.cacheReadTokens)) * 100)} cache hit rate
                        </div>
                    </div>
                    
                    <!-- Avg Cost per Session -->
                    <div class="bg-dark-surface border border-dark-border rounded-xl p-6 card-hover animate-slide-in" style="animation-delay: 0.3s;">
                        <div class="flex items-start justify-between mb-4">
                            <div>
                                <p class="text-sm text-gray-400 mb-1">Avg Cost/Session</p>
                                <h3 class="text-3xl font-bold text-white">${formatCost(data.totals.cost / data.totals.sessionCount)}</h3>
                            </div>
                            <div class="p-3 bg-amber-600/20 rounded-lg">
                                <svg class="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                            </div>
                        </div>
                        <div class="text-sm text-gray-400">
                            ${formatNumber(Math.round(data.totals.tokens / data.totals.sessionCount))} tokens/session
                        </div>
                    </div>
                </div>
                
                <!-- Cost Trend Chart -->
                <div class="bg-dark-surface border border-dark-border rounded-xl p-6 animate-slide-in" style="animation-delay: 0.4s;">
                    <div class="flex items-center justify-between mb-6">
                        <div>
                            <h3 class="text-lg font-semibold text-white">Cost Trend</h3>
                            <p class="text-sm text-gray-400 mt-1">Daily spending breakdown by model</p>
                        </div>
                        <div id="chartLegend" class="flex flex-wrap gap-4 text-sm">
                            <!-- Legend will be populated dynamically -->
                        </div>
                    </div>
                    <div class="h-64">
                        <canvas id="costTrendChart"></canvas>
                    </div>
                </div>
                
                <!-- Model Usage & Recent Sessions -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Model Usage -->
                    <div class="bg-dark-surface border border-dark-border rounded-xl p-6 animate-slide-in" style="animation-delay: 0.5s;">
                        <h3 class="text-lg font-semibold text-white mb-6">Top Models by Cost</h3>
                        <div class="space-y-4">
                            ${topModels.map(model => `
                                <div class="flex items-center gap-4">
                                    <div class="flex-1">
                                        <div class="flex items-center justify-between mb-2">
                                            <span class="text-sm font-medium text-white">${model.name}</span>
                                            <span class="text-sm text-gray-400">${formatCost(model.cost)}</span>
                                        </div>
                                        <div class="w-full bg-dark-bg rounded-full h-2 overflow-hidden">
                                            <div class="h-full" style="width: ${(model.cost / maxModelCost * 100).toFixed(1)}%; background-color: ${getModelColor(model.name)};"></div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    
                    <!-- Recent Sessions -->
                    <div class="bg-dark-surface border border-dark-border rounded-xl p-6 animate-slide-in" style="animation-delay: 0.6s;">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-lg font-semibold text-white">Recent Sessions</h3>
                            <a href="#" onclick="showPage('sessions')" class="text-sm text-blue-500 hover:text-blue-400 transition">View All →</a>
                        </div>
                        <div class="space-y-3">
                            ${recentSessions.map(session => `
                                <div class="flex items-center gap-4 p-3 bg-dark-bg rounded-lg hover:bg-dark-bg/60 transition cursor-pointer">
                                    <div class="flex-1 min-w-0">
                                        <p class="text-sm font-medium text-white truncate font-mono">${session.shortId}</p>
                                        <p class="text-xs text-gray-400">${session.timeAgo} • ${session.messageCount} messages</p>
                                    </div>
                                    <div class="text-right">
                                        <p class="text-sm font-medium text-white">${formatCost(session.cost)}</p>
                                        <span class="inline-block px-2 py-0.5 bg-green-600/20 text-green-500 text-xs rounded-full">Completed</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </main>
        `;
    },
    
    sessions: function() {
        const data = window.opencodeData;
        const sessions = data.sessions;
        
        return `
            <main class="space-y-6">
                <div class="bg-dark-surface border border-dark-border rounded-xl p-6">
                    <h3 class="text-lg font-semibold text-white mb-6">All Sessions (${sessions.length})</h3>
                    
                    <!-- Sessions Table -->
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="text-left text-sm text-gray-400 border-b border-dark-border">
                                    <th class="pb-3 font-medium">Session ID</th>
                                    <th class="pb-3 font-medium">Time</th>
                                    <th class="pb-3 font-medium">Duration</th>
                                    <th class="pb-3 font-medium">Messages</th>
                                    <th class="pb-3 font-medium">Tool Calls</th>
                                    <th class="pb-3 font-medium">Tokens</th>
                                    <th class="pb-3 font-medium">Cost</th>
                                </tr>
                            </thead>
                            <tbody class="text-sm">
                                ${sessions.slice(0, 50).map(session => `
                                    <tr class="border-b border-dark-border hover:bg-dark-bg/50 transition">
                                        <td class="py-4 text-white font-mono text-xs">${session.shortId}</td>
                                        <td class="py-4 text-gray-400">${session.timeAgo}</td>
                                        <td class="py-4 text-gray-400">${session.duration}</td>
                                        <td class="py-4 text-gray-400">${session.messageCount}</td>
                                        <td class="py-4 text-white font-medium">${session.totalToolCalls || 0}</td>
                                        <td class="py-4 text-gray-400">${formatNumber(session.tokens)}</td>
                                        <td class="py-4 text-white font-medium">${formatCost(session.cost)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                    
                    ${sessions.length > 50 ? `
                        <div class="mt-6 text-center text-sm text-gray-400">
                            Showing first 50 of ${sessions.length} sessions
                        </div>
                    ` : ''}
                </div>
            </main>
        `;
    },
    
    models: function() {
        const data = window.opencodeData;
        const models = data.models;
        const maxCost = calculateMaxCost(models);
        
        return `
            <main class="space-y-6">
                <!-- Info Box -->
                <div class="p-4 bg-purple-600/10 border border-purple-600/30 rounded-lg">
                    <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-purple-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <div class="text-sm">
                            <p class="text-purple-300 font-medium mb-1">About Cache Hit %</p>
                            <p class="text-purple-200/80">Prompt caching reduces input token costs by ~90% on cache hits. Higher percentages mean more cost savings.</p>
                        </div>
                    </div>
                </div>
                
                <!-- Model Analytics -->
                <div class="bg-dark-surface border border-dark-border rounded-xl p-6">
                    <h3 class="text-lg font-semibold text-white mb-6">Model Analytics</h3>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead>
                                <tr class="text-left text-sm text-gray-400 border-b border-dark-border">
                                    <th class="pb-3 font-medium">Model</th>
                                    <th class="pb-3 font-medium">Calls</th>
                                    <th class="pb-3 font-medium">Tokens</th>
                                    <th class="pb-3 font-medium">Cost</th>
                                    <th class="pb-3 font-medium">Avg/Call</th>
                                    <th class="pb-3 font-medium">Cache Hit %</th>
                                </tr>
                            </thead>
                            <tbody class="text-sm">
                                ${models.map(model => `
                                    <tr class="border-b border-dark-border hover:bg-dark-bg/50 transition">
                                        <td class="py-4 text-white font-medium">${model.name}</td>
                                        <td class="py-4 text-gray-400">${model.calls.toLocaleString()}</td>
                                        <td class="py-4 text-gray-400">${formatNumber(model.tokens)}</td>
                                        <td class="py-4 text-white font-medium">${formatCost(model.cost)}</td>
                                        <td class="py-4 text-gray-400">${formatCost(model.avgCostPerCall)}</td>
                                        <td class="py-4">
                                            <div class="flex items-center gap-2">
                                                <span class="text-gray-400">${formatPercent(model.cacheHitPct)}</span>
                                                <span class="text-xs text-green-500">~${formatCost(model.estimatedCacheSavings)} saved</span>
                                            </div>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        `;
    },
    
    providers: function() {
        const data = window.opencodeData;
        const providers = data.providers;
        const totalCost = providers.reduce((sum, p) => sum + p.cost, 0);
        
        return `
            <main class="space-y-6">
                <!-- Provider Cards -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    ${providers.map(provider => `
                        <div class="bg-dark-surface border border-dark-border rounded-xl p-6">
                            <h3 class="text-lg font-semibold text-white mb-4">${provider.name}</h3>
                            <div class="space-y-3">
                                <div>
                                    <p class="text-sm text-gray-400">Total Cost</p>
                                    <p class="text-2xl font-bold text-white">${formatCost(provider.cost)}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-400">Total Calls</p>
                                    <p class="text-lg font-semibold text-white">${provider.calls.toLocaleString()}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-400">Avg Cost/Call</p>
                                    <p class="text-lg font-semibold text-white">${formatCost(provider.avgCostPerCall)}</p>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <!-- Cost Distribution -->
                <div class="bg-dark-surface border border-dark-border rounded-xl p-6">
                    <h3 class="text-lg font-semibold text-white mb-6">Cost Distribution</h3>
                    <div class="space-y-4">
                        ${providers.map(provider => `
                            <div>
                                <div class="flex items-center justify-between mb-2">
                                    <span class="text-sm text-white">${provider.name}</span>
                                    <span class="text-sm text-gray-400">${formatCost(provider.cost)} (${formatPercent(provider.cost / totalCost * 100)})</span>
                                </div>
                                <div class="w-full bg-dark-bg rounded-full h-3 overflow-hidden">
                                    <div class="bg-blue-500 h-full" style="width: ${(provider.cost / totalCost * 100).toFixed(1)}%;"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </main>
        `;
    },
    
    tools: function() {
        const data = window.opencodeData;
        const tools = data.tools;
        const totalCalls = tools.reduce((sum, t) => sum + t.calls, 0);
        
        return `
            <main class="space-y-6">
                <div class="bg-dark-surface border border-dark-border rounded-xl p-6">
                    <h3 class="text-lg font-semibold text-white mb-6">Tool Usage (${totalCalls.toLocaleString()} total calls)</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        ${tools.map(tool => `
                            <div class="bg-dark-bg border border-dark-border rounded-lg p-6">
                                <h4 class="text-lg font-semibold text-white mb-4">${tool.name}</h4>
                                <div class="space-y-3">
                                    <div>
                                        <p class="text-sm text-gray-400">Total Calls</p>
                                        <p class="text-2xl font-bold text-white">${tool.calls.toLocaleString()}</p>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-400">Success Rate</p>
                                        <p class="text-lg font-semibold text-white">${formatPercent(tool.successRate)}</p>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </main>
        `;
    },
    
    optimization: function() {
        return `
            <main class="space-y-6">
                <div class="bg-dark-surface border border-dark-border rounded-xl p-6">
                    <h3 class="text-lg font-semibold text-white mb-6">Cost Optimization Opportunities</h3>
                    <div class="text-center text-gray-400 py-12">
                        <p>Optimization recommendations will appear here based on your usage patterns.</p>
                        <p class="mt-2 text-sm">Check back after more data is collected.</p>
                    </div>
                </div>
            </main>
        `;
    },
    
    settings: function() {
        return `
            <main class="space-y-6">
                <div class="bg-dark-surface border border-dark-border rounded-xl p-6">
                    <h3 class="text-lg font-semibold text-white mb-6">Settings</h3>
                    
                    <div class="space-y-4">
                        <div class="p-4 bg-dark-bg rounded-lg">
                            <p class="text-sm text-white font-medium">Data Source</p>
                            <p class="text-xs text-gray-400 mt-1">~/.local/share/opencode/storage/message/</p>
                        </div>
                        
                        <div class="p-4 bg-dark-bg rounded-lg">
                            <p class="text-sm text-white font-medium">Last Updated</p>
                            <p class="text-xs text-gray-400 mt-1" id="last-updated">Loading...</p>
                        </div>
                        
                        <button onclick="window.location.reload()" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition">
                            Refresh Data
                        </button>
                    </div>
                </div>
            </main>
        `;
    }
};

// ============================================================================
// Navigation & Page Management
// ============================================================================

/**
 * Switches between different dashboard pages
 * Updates navigation state, page title, and renders the selected page
 * @param {string} pageName - Name of page to display (overview, sessions, etc.)
 */
function showPage(pageName) {
    const titles = {
        overview: 'Overview',
        sessions: 'Sessions',
        models: 'Model Analytics',
        providers: 'Provider Comparison',
        tools: 'Tool Usage',
        optimization: 'Cost Optimization',
        settings: 'Settings'
    };
    
    document.getElementById('page-title').textContent = titles[pageName];
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('bg-blue-600', 'text-white');
        item.classList.add('text-gray-400');
    });
    const activeItem = document.querySelector(`[data-page="${pageName}"]`);
    if (activeItem) {
        activeItem.classList.add('bg-blue-600', 'text-white');
        activeItem.classList.remove('text-gray-400');
    }
    
    // Render page
    document.getElementById('content-container').innerHTML = pages[pageName]();
    
    // Initialize chart if overview
    if (pageName === 'overview') {
        setTimeout(initChart, 100);
    }
}

/**
 * Updates the chart legend with model colors
 * @param {Array} datasets - Chart.js datasets with backgroundColor property
 */
function updateLegend(datasets) {
    const legendEl = document.getElementById('chartLegend');
    if (!legendEl) return;

    legendEl.innerHTML = datasets.map(dataset => `
        <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full" style="background-color: ${dataset.backgroundColor}"></div>
            <span class="text-gray-400">${dataset.label}</span>
        </div>
    `).join('');
}

// ============================================================================
// Chart Initialization
// ============================================================================

/**
 * Initializes the cost trend stacked bar chart
 * Creates a Chart.js instance with model-specific colors and tooltips
 */
function initChart() {
    const canvas = document.getElementById('costTrendChart');
    if (!canvas) return;

    const data = window.opencodeData;
    const ctx = canvas.getContext('2d');

    // Build datasets from the data
    const datasets = [];
    const modelDatasets = data.dailyCosts.datasets;

    for (const [modelName, modelData] of Object.entries(modelDatasets)) {
        datasets.push({
            label: modelName,
            data: modelData,
            backgroundColor: modelColors[modelName] || modelColors['default'],
            borderWidth: 0
        });
    }

    // Update the legend
    updateLegend(datasets);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.dailyCosts.labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1a1a1a',
                    borderColor: '#27272a',
                    borderWidth: 1,
                    titleColor: '#ffffff',
                    bodyColor: '#a1a1aa',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': $' + context.parsed.y.toFixed(2);
                        },
                        footer: function(tooltipItems) {
                            let total = 0;
                            tooltipItems.forEach(item => {
                                total += item.parsed.y;
                            });
                            return '\nTotal: $' + total.toFixed(2);
                        }
                    },
                    footerColor: '#ffffff',
                    footerFont: {
                        weight: 'bold'
                    }
                }
            },
            scales: {
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: { color: '#27272a', drawBorder: false },
                    ticks: {
                        color: '#a1a1aa',
                        callback: function(value) { return '$' + value.toFixed(0); }
                    }
                },
                x: {
                    stacked: true,
                    grid: { display: false, drawBorder: false },
                    ticks: { color: '#a1a1aa' }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
}

// ============================================================================
// Dashboard Initialization
// ============================================================================

/**
 * Initializes the dashboard after data is loaded
 * Sets up the initial view, chart, and event listeners
 */
function initializeDashboard() {
    // Check if data is loaded
    if (!window.opencodeData) {
        console.error('OpenCode data not loaded!');
        return;
    }

    // Show data update time
    const updateTime = document.getElementById('last-updated');
    if (updateTime) {
        updateTime.textContent = new Date().toLocaleString();
    }

    showPage('overview');
}

// Initialize on data load
document.addEventListener('dataLoaded', initializeDashboard);

// Also try on DOMContentLoaded in case data is already loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.opencodeData) {
        initializeDashboard();
    }
});
