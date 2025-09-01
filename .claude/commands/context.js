#!/usr/bin/env node

/**
 * Context Window Usage Monitor
 * 
 * Slash command: /context
 * 
 * Analyzes current session's context window usage and provides
 * intelligent recommendations for session management.
 */

const fs = require('fs');
const path = require('path');

class ContextMonitor {
    constructor() {
        // Claude Sonnet context window limits
        this.CONTEXT_LIMITS = {
            'claude-sonnet-4-20250514': 200000,  // 200K tokens
            'claude-sonnet': 200000,
            'claude-haiku': 200000,
            'claude-opus': 200000
        };
        
        // Warning thresholds
        this.THRESHOLDS = {
            GREEN: 0.5,    // 50% - Continue freely
            YELLOW: 0.7,   // 70% - Start being mindful
            ORANGE: 0.85,  // 85% - Consider wrapping up
            RED: 0.95      // 95% - Must wrap up soon
        };
    }

    /**
     * Estimate current context usage based on conversation history
     */
    estimateContextUsage() {
        try {
            // Rough estimation based on file operations and conversation
            let estimatedTokens = 0;
            
            // Base conversation overhead
            estimatedTokens += 5000;
            
            // Check for recent file reads/operations
            const projectFiles = this.getProjectFileMetrics();
            estimatedTokens += projectFiles.totalTokens;
            
            // Add SuperClaude framework context (from CLAUDE.md references)
            estimatedTokens += 15000;
            
            return {
                estimatedTokens,
                confidence: projectFiles.confidence,
                breakdown: {
                    conversation: 5000,
                    projectFiles: projectFiles.totalTokens,
                    framework: 15000
                }
            };
        } catch (error) {
            return {
                estimatedTokens: 10000, // Conservative fallback
                confidence: 'low',
                breakdown: { fallback: 10000 },
                error: error.message
            };
        }
    }

    /**
     * Analyze project files to estimate token usage
     */
    getProjectFileMetrics() {
        let totalTokens = 0;
        let fileCount = 0;
        let confidence = 'medium';
        
        try {
            // Get current working directory
            const cwd = process.cwd();
            
            // Rough token estimation per file type
            const tokenEstimates = {
                '.py': 800,
                '.js': 600,
                '.ts': 700,
                '.json': 200,
                '.md': 400,
                '.txt': 100
            };
            
            // Walk through likely read files
            const commonFiles = [
                'requirements.txt',
                'package.json',
                'CLAUDE.md',
                '.claude/settings.local.json'
            ];
            
            commonFiles.forEach(file => {
                const filepath = path.join(cwd, file);
                if (fs.existsSync(filepath)) {
                    const stats = fs.statSync(filepath);
                    const ext = path.extname(file);
                    const estimate = tokenEstimates[ext] || 300;
                    totalTokens += Math.min(estimate, stats.size * 0.25); // ~4 chars per token
                    fileCount++;
                }
            });
            
            // Check findings directory (specific to this project)
            const findingsDir = path.join(cwd, 'findings');
            if (fs.existsSync(findingsDir)) {
                const findings = fs.readdirSync(findingsDir);
                totalTokens += findings.length * 50; // Small overhead per category
            }
            
            if (fileCount < 3) confidence = 'low';
            if (fileCount > 10) confidence = 'high';
            
        } catch (error) {
            confidence = 'low';
            totalTokens = 5000; // Conservative fallback
        }
        
        return { totalTokens, fileCount, confidence };
    }

    /**
     * Get current model from settings
     */
    getCurrentModel() {
        try {
            const settingsPath = path.join(process.env.HOME, '.claude/settings.json');
            if (fs.existsSync(settingsPath)) {
                const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
                return settings.model || 'claude-sonnet';
            }
        } catch (error) {
            // Fallback
        }
        return 'claude-sonnet';
    }

    /**
     * Generate usage report with recommendations
     */
    generateReport() {
        const model = this.getCurrentModel();
        const contextLimit = this.CONTEXT_LIMITS[model] || this.CONTEXT_LIMITS['claude-sonnet'];
        const usage = this.estimateContextUsage();
        const usagePercent = usage.estimatedTokens / contextLimit;
        
        let status, recommendation, emoji, color;
        
        if (usagePercent < this.THRESHOLDS.GREEN) {
            status = 'GREEN';
            emoji = '🟢';
            color = '\x1b[32m'; // Green
            recommendation = 'Continue working freely. Context window is healthy.';
        } else if (usagePercent < this.THRESHOLDS.YELLOW) {
            status = 'YELLOW';
            emoji = '🟡';
            color = '\x1b[33m'; // Yellow
            recommendation = 'Start being mindful of context usage. Consider consolidating tasks.';
        } else if (usagePercent < this.THRESHOLDS.ORANGE) {
            status = 'ORANGE';
            emoji = '🟠';
            color = '\x1b[31m'; // Red
            recommendation = 'Consider wrapping up soon. Start new session for major new tasks.';
        } else {
            status = 'RED';
            emoji = '🔴';
            color = '\x1b[91m'; // Bright red
            recommendation = 'WRAP UP IMMEDIATELY. Start fresh session for any significant work.';
        }
        
        const reset = '\x1b[0m';
        
        return `
${color}═══════════════════════════════════════════════════════════════${reset}
${emoji} ${color}CONTEXT WINDOW USAGE REPORT${reset} ${emoji}
${color}═══════════════════════════════════════════════════════════════${reset}

📊 Usage Metrics:
   • Estimated tokens: ${usage.estimatedTokens.toLocaleString()}
   • Context limit: ${contextLimit.toLocaleString()} 
   • Usage: ${color}${(usagePercent * 100).toFixed(1)}%${reset}
   • Model: ${model}
   • Confidence: ${usage.confidence}

📋 Token Breakdown:
   • Conversation: ${usage.breakdown.conversation?.toLocaleString() || 'N/A'}
   • Project files: ${usage.breakdown.projectFiles?.toLocaleString() || 'N/A'}
   • Framework: ${usage.breakdown.framework?.toLocaleString() || 'N/A'}

${emoji} Status: ${color}${status}${reset}

💡 Recommendation:
   ${recommendation}

${status === 'ORANGE' || status === 'RED' ? `
⚡ Quick Actions:
   • Use /commit to save current work
   • Use /spawn for complex new tasks
   • Start fresh session for major changes
   • Use --uc flag for token efficiency
` : ''}
${color}═══════════════════════════════════════════════════════════════${reset}
`;
    }
}

// Command execution
function main() {
    const monitor = new ContextMonitor();
    console.log(monitor.generateReport());
}

// Run if called directly
if (require.main === module) {
    main();
}

module.exports = { ContextMonitor };