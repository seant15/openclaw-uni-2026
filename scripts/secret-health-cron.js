#!/usr/bin/env node
/**
 * Secret Management Health Check Cron Job
 * 
 * This script runs daily to:
 * 1. Check secret access patterns
 * 2. Detect failures or anomalies
 * 3. Report health status to Slack
 * 4. Recommend upgrade if needed
 * 
 * Run via cron:
 *   0 9 * * * cd /data/workspace && node scripts/secret-health-cron.js
 * 
 * Or manually:
 *   node scripts/secret-health-cron.js [--report]
 */

const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const SLACK_BOT_TOKEN = process.env.SLACK_BOT_TOKEN;
const SLACK_ALERT_CHANNEL = process.env.SLACK_ALERT_CHANNEL || 'C06UQC665MX';

if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set');
    process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

// Health check configuration
const CONFIG = {
    // Thresholds for health assessment
    thresholds: {
        maxDailyFailures: 5,           // Max failed access attempts per day
        maxFailureRate: 0.1,           // Max 10% failure rate
        maxAvgResponseTime: 500,       // Max 500ms average response time
        minDailyAccesses: 10,          // Min expected daily accesses
        criticalSecretsExpiring: 3     // Alert if 3+ secrets expiring soon
    },
    
    // Days to look back for trend analysis
    trendDays: 7
};

/**
 * Calculate daily stats
 */
async function calculateDailyStats(date = new Date()) {
    const dateStr = date.toISOString().split('T')[0];
    
    // Call the database function
    await supabase.rpc('calculate_daily_secret_stats', { p_date: dateStr });
    
    // Fetch the calculated stats
    const { data: stats } = await supabase
        .from('secret_management_stats')
        .select('*')
        .eq('date', dateStr)
        .single();
    
    return stats;
}

/**
 * Get trend analysis
 */
async function getTrendAnalysis(days = CONFIG.trendDays) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    const { data: stats } = await supabase
        .from('secret_management_stats')
        .select('*')
        .gte('date', startDate.toISOString().split('T')[0])
        .order('date', { ascending: true });
    
    if (!stats || stats.length === 0) {
        return null;
    }
    
    // Calculate trends
    const totalAccesses = stats.reduce((sum, s) => sum + s.total_accesses, 0);
    const totalFailures = stats.reduce((sum, s) => sum + s.failed_accesses, 0);
    const avgFailureRate = totalAccesses > 0 ? totalFailures / totalAccesses : 0;
    
    const avgHealthScore = stats.reduce((sum, s) => sum + (s.health_score || 0), 0) / stats.length;
    
    const daysWithIssues = stats.filter(s => s.health_status !== 'healthy').length;
    
    // Trend direction
    const firstHalf = stats.slice(0, Math.floor(stats.length / 2));
    const secondHalf = stats.slice(Math.floor(stats.length / 2));
    
    const firstHalfAvg = firstHalf.reduce((sum, s) => sum + s.health_score, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, s) => sum + s.health_score, 0) / secondHalf.length;
    
    const trend = secondHalfAvg > firstHalfAvg ? 'improving' : 
                  secondHalfAvg < firstHalfAvg ? 'declining' : 'stable';
    
    return {
        daysAnalyzed: stats.length,
        totalAccesses,
        totalFailures,
        avgFailureRate: (avgFailureRate * 100).toFixed(2) + '%',
        avgHealthScore: Math.round(avgHealthScore),
        daysWithIssues,
        trend,
        dailyStats: stats
    };
}

/**
 * Check for expiring secrets
 */
async function checkExpiringSecrets() {
    const { data: secrets } = await supabase
        .from('secrets')
        .select('*')
        .eq('is_active', true)
        .not('expires_at', 'is', null)
        .lte('expires_at', new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString())
        .order('expires_at', { ascending: true });
    
    if (!secrets) return { count: 0, secrets: [] };
    
    const now = new Date();
    const withDaysRemaining = secrets.map(s => ({
        ...s,
        daysRemaining: Math.ceil((new Date(s.expires_at) - now) / (1000 * 60 * 60 * 24))
    }));
    
    return {
        count: secrets.length,
        critical: withDaysRemaining.filter(s => s.daysRemaining <= 7),
        warning: withDaysRemaining.filter(s => s.daysRemaining > 7 && s.daysRemaining <= 14),
        info: withDaysRemaining.filter(s => s.daysRemaining > 14),
        secrets: withDaysRemaining
    };
}

/**
 * Generate health assessment
 */
function assessHealth(today, trend, expiring) {
    const issues = [];
    const recommendations = [];
    
    // Check today's stats
    if (today.failed_accesses > CONFIG.thresholds.maxDailyFailures) {
        issues.push({
            severity: 'critical',
            message: `High failure count: ${today.failed_accesses} failed accesses today`
        });
    }
    
    if (today.total_accesses > 0) {
        const failureRate = today.failed_accesses / today.total_accesses;
        if (failureRate > CONFIG.thresholds.maxFailureRate) {
            issues.push({
                severity: 'warning',
                message: `High failure rate: ${(failureRate * 100).toFixed(1)}%`
            });
        }
    }
    
    if (today.total_accesses < CONFIG.thresholds.minDailyAccesses) {
        issues.push({
            severity: 'info',
            message: `Low activity: Only ${today.total_accesses} accesses today`
        });
    }
    
    // Check trend
    if (trend) {
        if (trend.daysWithIssues > 2) {
            issues.push({
                severity: 'warning',
                message: `${trend.daysWithIssues} days with issues in the last ${trend.daysAnalyzed} days`
            });
        }
        
        if (trend.trend === 'declining') {
            issues.push({
                severity: 'warning',
                message: 'Health trend is declining over the past week'
            });
        }
    }
    
    // Check expiring secrets
    if (expiring.critical.length > 0) {
        issues.push({
            severity: 'critical',
            message: `${expiring.critical.length} secrets expiring within 7 days`
        });
    } else if (expiring.warning.length > 0) {
        issues.push({
            severity: 'warning',
            message: `${expiring.warning.length} secrets expiring within 14 days`
        });
    }
    
    // Generate recommendations
    if (issues.filter(i => i.severity === 'critical').length > 0) {
        recommendations.push({
            priority: 'urgent',
            action: 'Review critical issues immediately',
            details: 'Check failed access logs and expiring secrets'
        });
    }
    
    if (trend && trend.avgFailureRate > 0.05) {
        recommendations.push({
            priority: 'high',
            action: 'Consider upgrading secret management solution',
            details: 'Current failure rate suggests scalability issues'
        });
    }
    
    if (expiring.count > 5) {
        recommendations.push({
            priority: 'medium',
            action: 'Implement automated secret rotation',
            details: 'Manual rotation is becoming burdensome'
        });
    }
    
    // Overall health status
    const criticalCount = issues.filter(i => i.severity === 'critical').length;
    const warningCount = issues.filter(i => i.severity === 'warning').length;
    
    let overallStatus = 'healthy';
    if (criticalCount > 0) overallStatus = 'critical';
    else if (warningCount > 1) overallStatus = 'degraded';
    
    return {
        status: overallStatus,
        score: today.health_score || 100,
        issues,
        recommendations
    };
}

/**
 * Send Slack notification
 */
async function sendSlackNotification(assessment, today, trend, expiring) {
    if (!SLACK_BOT_TOKEN) {
        console.log('⚠️  SLACK_BOT_TOKEN not set, skipping notification');
        return;
    }
    
    const statusEmoji = {
        'healthy': '🟢',
        'degraded': '🟡',
        'critical': '🔴'
    };
    
    const blocks = [
        {
            type: 'header',
            text: {
                type: 'plain_text',
                text: `${statusEmoji[assessment.status]} Secret Management Daily Report`,
                emoji: true
            }
        },
        {
            type: 'section',
            fields: [
                {
                    type: 'mrkdwn',
                    text: `*Health Score:*\n${assessment.score}/100`
                },
                {
                    type: 'mrkdwn',
                    text: `*Status:*\n${assessment.status.toUpperCase()}`
                },
                {
                    type: 'mrkdwn',
                    text: `*Today's Accesses:*\n${today.total_accesses} (${today.successful_accesses} ✅ / ${today.failed_accesses} ❌)`
                },
                {
                    type: 'mrkdwn',
                    text: `*7-Day Trend:*\n${trend ? trend.trend : 'N/A'}`
                }
            ]
        }
    ];
    
    // Add issues section if any
    if (assessment.issues.length > 0) {
        const issueText = assessment.issues.map(i => {
            const emoji = i.severity === 'critical' ? '🔴' : 
                          i.severity === 'warning' ? '🟠' : '🔵';
            return `${emoji} ${i.message}`;
        }).join('\n');
        
        blocks.push({
            type: 'section',
            text: {
                type: 'mrkdwn',
                text: `*Issues Detected:*\n${issueText}`
            }
        });
    }
    
    // Add expiring secrets section
    if (expiring.count > 0) {
        blocks.push({
            type: 'section',
            text: {
                type: 'mrkdwn',
                text: `*Expiring Secrets:*\n🔴 ${expiring.critical.length} within 7 days\n🟠 ${expiring.warning.length} within 14 days\n🔵 ${expiring.info.length} within 30 days`
            }
        });
    }
    
    // Add recommendations if any
    if (assessment.recommendations.length > 0) {
        const recText = assessment.recommendations.map(r => {
            const emoji = r.priority === 'urgent' ? '🚨' : 
                          r.priority === 'high' ? '⚠️' : '💡';
            return `${emoji} *${r.action}*\n   ${r.details}`;
        }).join('\n\n');
        
        blocks.push({
            type: 'section',
            text: {
                type: 'mrkdwn',
                text: `*Recommendations:*\n\n${recText}`
            }
        });
    }
    
    // Add action buttons
    blocks.push({
        type: 'actions',
        elements: [
            {
                type: 'button',
                text: {
                    type: 'plain_text',
                    text: 'View Details',
                    emoji: true
                },
                url: `${SUPABASE_URL}/project/default/editor`
            },
            {
                type: 'button',
                text: {
                    type: 'plain_text',
                    text: 'Run Health Check',
                    emoji: true
                },
                action_id: 'run_health_check'
            }
        ]
    });
    
    // Send to Slack
    const response = await fetch('https://slack.com/api/chat.postMessage', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${SLACK_BOT_TOKEN}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            channel: SLACK_ALERT_CHANNEL,
            blocks: blocks,
            text: `Secret Management Report: ${assessment.status.toUpperCase()} (${assessment.score}/100)`
        })
    });
    
    const result = await response.json();
    if (!result.ok) {
        console.error('❌ Failed to send Slack notification:', result.error);
    } else {
        console.log('✅ Slack notification sent');
    }
}

/**
 * Main function
 */
async function main() {
    console.log('🔐 Secret Management Health Check');
    console.log('=' .repeat(60));
    console.log(`Date: ${new Date().toISOString()}`);
    console.log();
    
    try {
        // Calculate today's stats
        console.log('📊 Calculating today\'s statistics...');
        const today = await calculateDailyStats();
        console.log(`   Total accesses: ${today.total_accesses}`);
        console.log(`   Successful: ${today.successful_accesses}`);
        console.log(`   Failed: ${today.failed_accesses}`);
        console.log(`   Health score: ${today.health_score}/100`);
        console.log();
        
        // Get trend analysis
        console.log('📈 Analyzing 7-day trend...');
        const trend = await getTrendAnalysis();
        if (trend) {
            console.log(`   Average health score: ${trend.avgHealthScore}/100`);
            console.log(`   Average failure rate: ${trend.avgFailureRate}`);
            console.log(`   Days with issues: ${trend.daysWithIssues}/${trend.daysAnalyzed}`);
            console.log(`   Trend: ${trend.trend}`);
        }
        console.log();
        
        // Check expiring secrets
        console.log('⏰ Checking expiring secrets...');
        const expiring = await checkExpiringSecrets();
        console.log(`   Expiring within 30 days: ${expiring.count}`);
        console.log(`   - Critical (≤7 days): ${expiring.critical.length}`);
        console.log(`   - Warning (≤14 days): ${expiring.warning.length}`);
        console.log(`   - Info (≤30 days): ${expiring.info.length}`);
        console.log();
        
        // Generate health assessment
        console.log('🏥 Generating health assessment...');
        const assessment = assessHealth(today, trend, expiring);
        console.log(`   Overall status: ${assessment.status.toUpperCase()}`);
        console.log(`   Health score: ${assessment.score}/100`);
        console.log(`   Issues found: ${assessment.issues.length}`);
        console.log(`   Recommendations: ${assessment.recommendations.length}`);
        console.log();
        
        // Print issues
        if (assessment.issues.length > 0) {
            console.log('⚠️  Issues:');
            for (const issue of assessment.issues) {
                const emoji = issue.severity === 'critical' ? '🔴' : 
                              issue.severity === 'warning' ? '🟠' : '🔵';
                console.log(`   ${emoji} ${issue.message}`);
            }
            console.log();
        }
        
        // Print recommendations
        if (assessment.recommendations.length > 0) {
            console.log('💡 Recommendations:');
            for (const rec of assessment.recommendations) {
                const emoji = rec.priority === 'urgent' ? '🚨' : 
                              rec.priority === 'high' ? '⚠️' : '💡';
                console.log(`   ${emoji} ${rec.action}`);
                console.log(`      ${rec.details}`);
            }
            console.log();
        }
        
        // Send Slack notification
        if (args.includes('--report') || assessment.status !== 'healthy') {
            await sendSlackNotification(assessment, today, trend, expiring);
        }
        
        // Exit with appropriate code
        console.log('=' .repeat(60));
        if (assessment.status === 'critical') {
            console.log('❌ Health check FAILED - Critical issues detected');
            process.exit(1);
        } else if (assessment.status === 'degraded') {
            console.log('⚠️  Health check WARNING - Issues detected');
            process.exit(0); // Still exit 0 for cron compatibility
        } else {
            console.log('✅ Health check PASSED');
            process.exit(0);
        }
        
    } catch (err) {
        console.error('❌ Health check failed with error:', err.message);
        console.error(err.stack);
        process.exit(1);
    }
}

// Run
const args = process.argv.slice(2);
main();
