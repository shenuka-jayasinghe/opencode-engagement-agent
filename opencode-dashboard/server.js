#!/usr/bin/env node
/**
 * OpenCode Dashboard Server
 *
 * Express server that provides live OpenCode usage analytics.
 * Reads message data from ~/.local/share/opencode/storage/message/
 * and serves a real-time dashboard with cost and token metrics.
 */

import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readdir, readFile, stat } from 'fs/promises';
import { existsSync } from 'fs';
import { homedir } from 'os';

// Configuration
const PORT = 3030;
const MESSAGE_DIR = join(homedir(), '.local/share/opencode/storage/message');
const MAX_RECENT_SESSIONS = 10;
const MAX_TOP_MODELS = 5;
const DEFAULT_DATE_RANGE_DAYS = 7;

// Time constants for session age calculation
const MS_PER_MINUTE = 60000;
const MS_PER_HOUR = 3600000;
const MS_PER_DAY = 86400000;
const MS_PER_TWO_DAYS = 172800000;

// Cache pricing constants (for cost savings calculation)
const CACHE_READ_COST_PER_MILLION = 0.003;
const CACHE_DISCOUNT_RATE = 0.9;

// Setup paths
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Initialize Express app
const app = express();

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Formats a model ID into a human-readable name with optional provider suffix
 * @param {string} modelId - Raw model ID (e.g., 'anthropic.claude-sonnet-4-5-20250929-v1:0')
 * @param {string|null} providerId - Provider ID (e.g., 'amazon-bedrock')
 * @param {boolean} includeProvider - Whether to append provider name in parentheses
 * @returns {string} Formatted model name (e.g., 'Claude Sonnet 4.5 (AWS Bedrock)')
 */
function formatModelName(modelId, providerId = null, includeProvider = true) {
    const mapping = {
        'claude-sonnet-4.5': 'Claude Sonnet 4.5',
        'claude-haiku-4.5': 'Claude Haiku 4.5',
        'gemini-2.5-pro': 'Gemini 2.5 Pro',
        'gemini-2.5-flash': 'Gemini 2.5 Flash',
        'gemini-2.5-flash-lite': 'Gemini 2.5 Flash Lite',
        'gemini-3-pro-preview': 'Gemini 3.0 Pro Preview',
    };

    const normalized = modelId.toLowerCase()
        .replace('anthropic.', '')
        .replace('google/', '')
        .replace('-v1:0', '')
        .replace('-20250929', '')
        .replace('-20250514', '');

    let modelName = mapping[normalized];
    if (!modelName) {
        if (normalized.includes('claude-sonnet-4')) modelName = 'Claude Sonnet 4.5';
        else if (normalized.includes('claude-haiku')) modelName = 'Claude Haiku 4.5';
        else modelName = normalized.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    if (includeProvider && providerId) {
        const providerMap = {
            'amazon-bedrock': 'AWS Bedrock',
            'google': 'Google',
            'github': 'GitHub Copilot'
        };
        const providerName = providerMap[providerId.toLowerCase()] || providerId;
        modelName = `${modelName} (${providerName})`;
    }

    return modelName;
}

/**
 * Formats a provider ID into a human-readable name
 * @param {string} providerId - Raw provider ID (e.g., 'amazon-bedrock')
 * @returns {string} Formatted provider name (e.g., 'AWS Bedrock')
 */
function formatProviderName(providerId) {
    const mapping = {
        'amazon-bedrock': 'AWS Bedrock',
        'google': 'Google AI Studio',
        'github': 'GitHub Copilot'
    };
    return mapping[providerId.toLowerCase()] || providerId;
}

// ============================================================================
// Data Processing Functions
// ============================================================================

/**
 * Parses all OpenCode message data from disk
 * Reads session directories and aggregates usage metrics
 * @returns {Promise<Object>} Parsed data with sessions, models, providers, tools, and totals
 * @throws {Error} If message directory doesn't exist
 */
async function parseMessages() {
    if (!existsSync(MESSAGE_DIR)) {
        throw new Error(`Message directory not found: ${MESSAGE_DIR}`);
    }

    const sessions = {};
    const models = {};
    const providers = {};
    const tools = {};
    const dailyCosts = {};
    const dailyCostsByModel = {};

    let totalCost = 0;
    let totalTokens = 0;
    let totalInputTokens = 0;
    let totalOutputTokens = 0;
    let totalCacheRead = 0;
    let totalCacheWrite = 0;

    const sessionDirs = await readdir(MESSAGE_DIR);

    for (const sessionDir of sessionDirs) {
        if (!sessionDir.startsWith('ses_')) continue;

        const sessionPath = join(MESSAGE_DIR, sessionDir);
        const sessionStat = await stat(sessionPath);
        if (!sessionStat.isDirectory()) continue;

        const sessionId = sessionDir;
        let sessionCost = 0;
        let sessionTokens = 0;
        let sessionStart = null;
        let sessionEnd = null;
        const sessionModels = {};
        const sessionTools = {};

        const messageFiles = await readdir(sessionPath);

        for (const msgFile of messageFiles) {
            if (!msgFile.endsWith('.json')) continue;

            try {
                const msgPath = join(sessionPath, msgFile);
                const msgContent = await readFile(msgPath, 'utf8');
                const msg = JSON.parse(msgContent);

                // Extract model and provider
                const modelId = msg.modelID || 'unknown';
                const providerId = msg.providerID || 'unknown';

                // Extract timing
                const createdTs = msg.time?.created || 0;
                if (createdTs) {
                    const createdDt = new Date(createdTs);
                    if (!sessionStart || createdDt < sessionStart) sessionStart = createdDt;
                    if (!sessionEnd || createdDt > sessionEnd) sessionEnd = createdDt;

                    // Daily costs
                    const dateKey = createdDt.toISOString().split('T')[0];
                    dailyCosts[dateKey] = (dailyCosts[dateKey] || 0) + (msg.cost || 0);

                    // Track costs by model per day
                    if (modelId && modelId !== 'unknown') {
                        if (!dailyCostsByModel[dateKey]) dailyCostsByModel[dateKey] = {};
                        dailyCostsByModel[dateKey][modelId] = (dailyCostsByModel[dateKey][modelId] || 0) + (msg.cost || 0);
                    }
                }

                // Extract cost and tokens
                const cost = msg.cost || 0;
                const inputTok = msg.tokens?.input || 0;
                const outputTok = msg.tokens?.output || 0;
                const cacheRead = msg.tokens?.cache?.read || 0;
                const cacheWrite = msg.tokens?.cache?.write || 0;

                sessionCost += cost;
                sessionTokens += inputTok + outputTok + cacheRead + cacheWrite;

                totalCost += cost;
                totalTokens += inputTok + outputTok + cacheRead + cacheWrite;
                totalInputTokens += inputTok;
                totalOutputTokens += outputTok;
                totalCacheRead += cacheRead;
                totalCacheWrite += cacheWrite;

                // Model tracking
                if (modelId && modelId !== 'unknown') {
                    if (!models[modelId]) {
                        models[modelId] = {
                            calls: 0,
                            tokens: 0,
                            cost: 0,
                            cache_read: 0,
                            cache_write: 0,
                            input_tokens: 0,
                            output_tokens: 0,
                            provider_id: providerId
                        };
                    }
                    models[modelId].calls++;
                    models[modelId].cost += cost;
                    models[modelId].tokens += inputTok + outputTok;
                    models[modelId].input_tokens += inputTok;
                    models[modelId].output_tokens += outputTok;
                    models[modelId].cache_read += cacheRead;
                    models[modelId].cache_write += cacheWrite;
                    sessionModels[modelId] = (sessionModels[modelId] || 0) + 1;
                }

                // Provider tracking
                if (providerId && providerId !== 'unknown') {
                    if (!providers[providerId]) {
                        providers[providerId] = { calls: 0, cost: 0 };
                    }
                    providers[providerId].calls++;
                    providers[providerId].cost += cost;
                }

                // Tool tracking
                const content = msg.content || [];
                if (Array.isArray(content)) {
                    for (const item of content) {
                        if (item.type === 'tool-use') {
                            const toolName = item.name || 'unknown';
                            sessionTools[toolName] = (sessionTools[toolName] || 0) + 1;
                            if (!tools[toolName]) {
                                tools[toolName] = { calls: 0, success: 0, failed: 0 };
                            }
                            tools[toolName].calls++;
                            tools[toolName].success++;
                        }
                    }
                }
            } catch (err) {
                // Skip invalid messages
                continue;
            }
        }

        // Store session data
        if (sessionStart) {
            const durationSeconds = sessionEnd ? (sessionEnd - sessionStart) / 1000 : 0;
            const now = new Date();
            const delta = now - sessionStart;
            let timeAgo;

            if (delta < MS_PER_HOUR) {
                timeAgo = `${Math.floor(delta / MS_PER_MINUTE)} minutes ago`;
            } else if (delta < MS_PER_DAY) {
                timeAgo = `${Math.floor(delta / MS_PER_HOUR)} hours ago`;
            } else if (delta < MS_PER_TWO_DAYS) {
                timeAgo = 'Yesterday';
            } else {
                timeAgo = `${Math.floor(delta / MS_PER_DAY)} days ago`;
            }

            sessions[sessionId] = {
                id: sessionId,
                message_count: messageFiles.filter(f => f.endsWith('.json')).length,
                cost: sessionCost,
                tokens: sessionTokens,
                start: sessionStart.toISOString(),
                end: sessionEnd?.toISOString(),
                duration_seconds: durationSeconds,
                time_ago: timeAgo,
                tools: sessionTools
            };
        }
    }

    return {
        sessions,
        models,
        providers,
        tools,
        daily_costs: dailyCosts,
        daily_costs_by_model: dailyCostsByModel,
        totals: {
            cost: totalCost,
            tokens: totalTokens,
            input_tokens: totalInputTokens,
            output_tokens: totalOutputTokens,
            cache_read_tokens: totalCacheRead,
            cache_write_tokens: totalCacheWrite,
            session_count: Object.keys(sessions).length
        }
    };
}

/**
 * Formats parsed data for dashboard consumption
 * Applies date range filtering and sorts data by relevance
 * @param {Object} data - Raw parsed data from parseMessages()
 * @param {Object} options - Formatting options
 * @param {number} options.days - Number of days to include (default: 7)
 * @param {string} options.startDate - Start date in YYYY-MM-DD format
 * @param {string} options.endDate - End date in YYYY-MM-DD format
 * @returns {Object} Formatted data ready for dashboard display
 */
function formatDashboardData(data, options = {}) {
    const { sessions, models, providers, tools, daily_costs, daily_costs_by_model, totals } = data;
    const { days = DEFAULT_DATE_RANGE_DAYS, startDate = null, endDate = null } = options;

    // Sort sessions by start time (most recent first)
    const sortedSessions = Object.values(sessions)
        .sort((a, b) => new Date(b.start) - new Date(a.start))
        .slice(0, MAX_RECENT_SESSIONS)
        .map(s => ({
            id: s.id,
            shortId: s.id.substring(0, 20) + '...',
            messageCount: s.message_count,
            cost: s.cost,
            tokens: s.tokens,
            timeAgo: s.time_ago,
            duration: `${Math.floor(s.duration_seconds / 60)}m ${Math.floor(s.duration_seconds % 60)}s`,
            totalToolCalls: Object.values(s.tools).reduce((sum, count) => sum + count, 0),
            tools: s.tools
        }));

    // Sort models by cost
    const sortedModels = Object.entries(models)
        .sort((a, b) => b[1].cost - a[1].cost)
        .slice(0, MAX_TOP_MODELS)
        .map(([modelId, stats]) => {
            const totalInput = stats.input_tokens + stats.cache_read;
            const cacheHitPct = totalInput > 0 ? (stats.cache_read / totalInput * 100) : 0;
            const cacheSavings = stats.cache_read * CACHE_READ_COST_PER_MILLION * CACHE_DISCOUNT_RATE / 1000000;

            return {
                id: modelId,
                name: formatModelName(modelId, stats.provider_id),
                calls: stats.calls,
                tokens: stats.tokens,
                cost: stats.cost,
                avgCostPerCall: stats.cost / stats.calls,
                cacheHitPct,
                estimatedCacheSavings: cacheSavings
            };
        });

    // Sort providers by cost
    const sortedProviders = Object.entries(providers)
        .sort((a, b) => b[1].cost - a[1].cost)
        .map(([providerId, stats]) => ({
            id: providerId,
            name: formatProviderName(providerId),
            calls: stats.calls,
            cost: stats.cost,
            avgCostPerCall: stats.cost / stats.calls
        }));

    // Generate chart data based on date range
    let sortedDates = Object.keys(daily_costs).sort();

    // Filter by date range if specified
    if (startDate && endDate) {
        sortedDates = sortedDates.filter(date => date >= startDate && date <= endDate);
    } else {
        // Use last N days
        sortedDates = sortedDates.slice(-days);
    }

    const chartLabels = sortedDates.map(date => {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const chartDatasets = {};
    const topModelIds = Object.entries(models)
        .sort((a, b) => b[1].cost - a[1].cost)
        .slice(0, MAX_TOP_MODELS)
        .map(([id]) => id);

    for (let i = 0; i < sortedDates.length; i++) {
        const dateStr = sortedDates[i];
        const dateModels = daily_costs_by_model[dateStr] || {};

        for (const modelId of topModelIds) {
            const modelCost = dateModels[modelId] || 0;
            const providerId = models[modelId]?.provider_id || 'unknown';
            const modelName = formatModelName(modelId, providerId);

            if (!chartDatasets[modelName]) {
                chartDatasets[modelName] = new Array(sortedDates.length).fill(0);
            }
            chartDatasets[modelName][i] += modelCost;
        }
    }

    // Sort tools by calls
    const sortedTools = Object.entries(tools)
        .sort((a, b) => b[1].calls - a[1].calls)
        .map(([name, stats]) => ({
            name,
            calls: stats.calls,
            successRate: stats.calls > 0 ? (stats.success / stats.calls * 100) : 100
        }));

    return {
        totals: {
            cost: totals.cost,
            tokens: totals.tokens,
            inputTokens: totals.input_tokens,
            outputTokens: totals.output_tokens,
            cacheReadTokens: totals.cache_read_tokens,
            cacheWriteTokens: totals.cache_write_tokens,
            sessionCount: totals.session_count
        },
        models: sortedModels,
        providers: sortedProviders,
        sessions: sortedSessions,
        tools: sortedTools,
        dailyCosts: {
            labels: chartLabels,
            datasets: chartDatasets
        }
    };
}

// ============================================================================
// API Routes
// ============================================================================

/**
 * GET /api/data
 * Returns formatted OpenCode usage data
 * Query parameters:
 *   - days: number of days to include (default: 7)
 *   - start: start date in YYYY-MM-DD format
 *   - end: end date in YYYY-MM-DD format
 */
app.get('/api/data', async (req, res) => {
    try {
        const rawData = await parseMessages();

        // Parse query parameters for date range
        const options = {};
        if (req.query.days) {
            options.days = parseInt(req.query.days, 10);
        }
        if (req.query.start && req.query.end) {
            options.startDate = req.query.start;
            options.endDate = req.query.end;
        }

        const formattedData = formatDashboardData(rawData, options);
        res.json(formattedData);
    } catch (error) {
        console.error('Error parsing messages:', error);
        res.status(500).json({ error: error.message });
    }
});

// Serve static files (index.html, dashboard.js)
app.use(express.static(__dirname));

// ============================================================================
// Server Initialization
// ============================================================================

app.listen(PORT, () => {
    console.log(`\n🚀 OpenCode Dashboard running at http://localhost:${PORT}`);
    console.log(`📊 Data updates automatically on each page load\n`);
});
