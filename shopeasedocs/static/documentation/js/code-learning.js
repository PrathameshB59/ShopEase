/* ============================================
   ShopEase Documentation - Code Learning Interactive Viewer
   ============================================ */

/**
 * CodeLearningViewer - Interactive code exploration and learning system
 * Features:
 * - Line-by-line code explanations
 * - Execution flow visualization
 * - Variable state tracking
 * - Interactive annotations
 * - Learning progress tracking
 */
class CodeLearningViewer {
    constructor(options = {}) {
        this.codeContainer = options.codeContainer || document.querySelector('.interactive-code');
        this.explanationPanel = options.explanationPanel || document.getElementById('line-explanation-container');
        this.variablesDisplay = options.variablesDisplay || document.getElementById('variables-display');
        this.stackDisplay = options.stackDisplay || document.getElementById('stack-display');
        this.flowchartContainer = options.flowchartContainer || document.getElementById('flowchart-container');

        this.currentLine = null;
        this.executionStep = 0;
        this.isAnimating = false;
        this.variableStates = [];
        this.executionStack = [];

        this.explanations = options.explanations || {};
        this.codeLines = [];

        this.init();
    }

    init() {
        this.parseCodeLines();
        this.attachEventListeners();
        this.setupControls();
        this.initializeTooltips();
    }

    /**
     * Parse code lines from the DOM
     */
    parseCodeLines() {
        const lines = this.codeContainer.querySelectorAll('.code-line');
        lines.forEach((line, index) => {
            const lineNumber = parseInt(line.dataset.line);
            const explanation = this.explanations[`line_${lineNumber}`] || {};

            this.codeLines.push({
                number: lineNumber,
                element: line,
                content: line.querySelector('.line-code').textContent,
                explanation: explanation.explanation || '',
                concepts: explanation.concepts || [],
                relatedLines: explanation.related_lines || [],
                executionOrder: explanation.execution_order || 0,
                variablesAffected: explanation.variables_affected || [],
                difficulty: explanation.difficulty || 'basic',
                quickNote: explanation.quick_note || '',
                commonError: explanation.common_error || ''
            });
        });
    }

    /**
     * Attach event listeners to code lines
     */
    attachEventListeners() {
        this.codeLines.forEach(line => {
            line.element.addEventListener('click', () => {
                this.highlightLine(line.number);
                this.showExplanation(line);
            });

            line.element.addEventListener('mouseenter', () => {
                this.highlightRelatedLines(line.relatedLines);
            });

            line.element.addEventListener('mouseleave', () => {
                this.clearRelatedHighlights();
            });
        });
    }

    /**
     * Setup control buttons
     */
    setupControls() {
        const stepThroughBtn = document.getElementById('step-through-btn');
        const resetBtn = document.getElementById('reset-btn');
        const showFlowBtn = document.getElementById('show-flow-btn');

        if (stepThroughBtn) {
            stepThroughBtn.addEventListener('click', () => this.startStepThrough());
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.reset());
        }

        if (showFlowBtn) {
            showFlowBtn.addEventListener('click', () => this.toggleFlowchart());
        }
    }

    /**
     * Initialize Bootstrap tooltips
     */
    initializeTooltips() {
        const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
        tooltips.forEach(tooltip => {
            new bootstrap.Tooltip(tooltip);
        });
    }

    /**
     * Highlight a specific line
     */
    highlightLine(lineNumber) {
        // Remove previous highlights
        this.codeLines.forEach(line => {
            line.element.classList.remove('active');
        });

        // Add highlight to current line
        const targetLine = this.codeLines.find(l => l.number === lineNumber);
        if (targetLine) {
            targetLine.element.classList.add('active');
            this.currentLine = targetLine;

            // Scroll to line if needed
            targetLine.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    /**
     * Show explanation for a line
     */
    showExplanation(line) {
        const explanationHTML = `
            <div class="line-explanation-content">
                <div class="explanation-header">
                    <h5>Line ${line.number} Explanation</h5>
                    <span class="badge bg-${this.getDifficultyColor(line.difficulty)}">
                        ${line.difficulty}
                    </span>
                </div>

                <div class="explanation-body">
                    ${line.explanation ? `<p class="explanation-text">${line.explanation}</p>` : '<p class="text-muted">No detailed explanation available.</p>'}

                    ${line.concepts.length > 0 ? `
                        <div class="concepts-section mt-3">
                            <h6><i class="bi bi-lightbulb"></i> Concepts</h6>
                            <div class="concepts-tags">
                                ${line.concepts.map(concept => `<span class="badge bg-info">${concept}</span>`).join(' ')}
                            </div>
                        </div>
                    ` : ''}

                    ${line.variablesAffected.length > 0 ? `
                        <div class="variables-section mt-3">
                            <h6><i class="bi bi-box"></i> Variables Affected</h6>
                            <div class="variables-list">
                                ${line.variablesAffected.map(v => `<code class="variable-tag">${v}</code>`).join(' ')}
                            </div>
                        </div>
                    ` : ''}

                    ${line.relatedLines.length > 0 ? `
                        <div class="related-lines-section mt-3">
                            <h6><i class="bi bi-link-45deg"></i> Related Lines</h6>
                            <div class="related-lines-list">
                                ${line.relatedLines.map(lineNum =>
                                    `<button class="btn btn-sm btn-outline-primary" onclick="codeLearning.highlightLine(${lineNum})">
                                        Line ${lineNum}
                                    </button>`
                                ).join(' ')}
                            </div>
                        </div>
                    ` : ''}

                    ${line.commonError ? `
                        <div class="alert alert-warning mt-3">
                            <strong><i class="bi bi-exclamation-triangle"></i> Common Mistake:</strong>
                            <p class="mb-0">${line.commonError}</p>
                        </div>
                    ` : ''}

                    ${line.executionOrder > 0 ? `
                        <div class="execution-order mt-3">
                            <small class="text-muted">
                                <i class="bi bi-arrow-right-circle"></i> Execution Order: <strong>${line.executionOrder}</strong>
                            </small>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        this.explanationPanel.innerHTML = explanationHTML;
    }

    /**
     * Highlight related lines
     */
    highlightRelatedLines(relatedLines) {
        relatedLines.forEach(lineNum => {
            const line = this.codeLines.find(l => l.number === lineNum);
            if (line) {
                line.element.classList.add('related');
            }
        });
    }

    /**
     * Clear related line highlights
     */
    clearRelatedHighlights() {
        this.codeLines.forEach(line => {
            line.element.classList.remove('related');
        });
    }

    /**
     * Start step-through execution animation
     */
    async startStepThrough() {
        if (this.isAnimating) {
            this.stopStepThrough();
            return;
        }

        this.isAnimating = true;
        const stepThroughBtn = document.getElementById('step-through-btn');
        if (stepThroughBtn) {
            stepThroughBtn.innerHTML = '<i class="bi bi-pause"></i> Pause';
        }

        // Sort lines by execution order
        const orderedLines = [...this.codeLines]
            .filter(line => line.executionOrder > 0)
            .sort((a, b) => a.executionOrder - b.executionOrder);

        for (const line of orderedLines) {
            if (!this.isAnimating) break;

            this.highlightLine(line.number);
            this.showExplanation(line);
            this.updateVariableState(line);
            this.updateExecutionStack(line);

            // Wait before next step
            await this.sleep(2000);
        }

        this.isAnimating = false;
        if (stepThroughBtn) {
            stepThroughBtn.innerHTML = '<i class="bi bi-play"></i> Step Through';
        }
    }

    /**
     * Stop step-through animation
     */
    stopStepThrough() {
        this.isAnimating = false;
        const stepThroughBtn = document.getElementById('step-through-btn');
        if (stepThroughBtn) {
            stepThroughBtn.innerHTML = '<i class="bi bi-play"></i> Step Through';
        }
    }

    /**
     * Reset the viewer
     */
    reset() {
        this.executionStep = 0;
        this.currentLine = null;
        this.variableStates = [];
        this.executionStack = [];

        // Clear all highlights
        this.codeLines.forEach(line => {
            line.element.classList.remove('active', 'related');
        });

        // Reset explanation panel
        this.explanationPanel.innerHTML = `
            <div class="placeholder">
                <i class="bi bi-cursor"></i>
                <p>Click any line of code to see detailed explanation</p>
            </div>
        `;

        // Clear variable and stack displays
        if (this.variablesDisplay) {
            this.variablesDisplay.innerHTML = '<p class="text-muted small">No variables tracked yet</p>';
        }

        if (this.stackDisplay) {
            this.stackDisplay.innerHTML = '<p class="text-muted small">No function calls yet</p>';
        }
    }

    /**
     * Update variable state display
     */
    updateVariableState(line) {
        if (!this.variablesDisplay || line.variablesAffected.length === 0) return;

        // This is a simplified version - in production, you'd track actual values
        const variablesHTML = `
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Variable</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${line.variablesAffected.map(variable => `
                        <tr>
                            <td><code>${variable}</code></td>
                            <td><span class="badge bg-success">Modified</span></td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        this.variablesDisplay.innerHTML = variablesHTML;
    }

    /**
     * Update execution stack display
     */
    updateExecutionStack(line) {
        if (!this.stackDisplay) return;

        this.executionStack.push(`Line ${line.number}`);

        const stackHTML = `
            <div class="stack-items">
                ${this.executionStack.map((item, index) => `
                    <div class="stack-item" style="margin-left: ${index * 10}px;">
                        <i class="bi bi-arrow-right-short"></i> ${item}
                    </div>
                `).join('')}
            </div>
        `;

        this.stackDisplay.innerHTML = stackHTML;
    }

    /**
     * Toggle flowchart display
     */
    toggleFlowchart() {
        if (!this.flowchartContainer) return;

        if (this.flowchartContainer.style.display === 'none' || !this.flowchartContainer.style.display) {
            this.flowchartContainer.style.display = 'block';
            // If using Mermaid.js, trigger render here
            if (typeof mermaid !== 'undefined') {
                mermaid.init(undefined, this.flowchartContainer);
            }
        } else {
            this.flowchartContainer.style.display = 'none';
        }
    }

    /**
     * Get difficulty badge color
     */
    getDifficultyColor(difficulty) {
        const colors = {
            'basic': 'success',
            'intermediate': 'warning',
            'advanced': 'danger',
            'expert': 'dark'
        };
        return colors[difficulty] || 'secondary';
    }

    /**
     * Sleep utility for animations
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Track time spent on this code
     */
    startTimeTracking() {
        this.startTime = Date.now();

        // Send time update every minute
        setInterval(() => {
            if (this.startTime) {
                const timeSpent = Math.floor((Date.now() - this.startTime) / 1000);
                this.saveProgress({ time_spent: timeSpent });
            }
        }, 60000);
    }

    /**
     * Save learning progress via AJAX
     */
    async saveProgress(data) {
        try {
            const response = await fetch('/docs/code/ajax/save-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            return result.success;
        } catch (error) {
            console.error('Error saving progress:', error);
            return false;
        }
    }
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Bookmark functionality
 */
async function toggleBookmark(codeId) {
    try {
        const response = await fetch('/docs/code/ajax/toggle-bookmark/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ code_id: codeId })
        });

        const data = await response.json();

        if (data.success) {
            const bookmarkBtn = document.querySelector('[data-bookmark-btn]');
            if (bookmarkBtn) {
                if (data.bookmarked) {
                    bookmarkBtn.innerHTML = '<i class="bi bi-bookmark-fill"></i> Bookmarked';
                    bookmarkBtn.classList.add('btn-warning');
                    bookmarkBtn.classList.remove('btn-outline-warning');
                } else {
                    bookmarkBtn.innerHTML = '<i class="bi bi-bookmark"></i> Bookmark';
                    bookmarkBtn.classList.remove('btn-warning');
                    bookmarkBtn.classList.add('btn-outline-warning');
                }
            }
        }
    } catch (error) {
        console.error('Error toggling bookmark:', error);
    }
}

/**
 * Add personal note
 */
async function addNote(codeId, lineNumber, noteText) {
    try {
        const response = await fetch('/docs/code/ajax/add-note/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                code_id: codeId,
                line_number: lineNumber,
                note: noteText
            })
        });

        const data = await response.json();
        return data.success;
    } catch (error) {
        console.error('Error adding note:', error);
        return false;
    }
}

// Global instance
let codeLearning = null;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    const codeContainer = document.querySelector('.interactive-code');

    if (codeContainer) {
        // Get explanations from data attribute or global variable
        const explanations = window.codeExplanations || {};

        codeLearning = new CodeLearningViewer({
            explanations: explanations
        });

        // Start time tracking
        codeLearning.startTimeTracking();
    }
});
