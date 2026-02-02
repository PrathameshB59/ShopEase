/* ============================================
   ShopEase Documentation - Flowchart Generator
   Auto-generate flowcharts from code using Mermaid.js
   ============================================ */

/**
 * FlowchartGenerator - Automatically create visual flowcharts from code
 */
class FlowchartGenerator {
    constructor(codeSnippet, options = {}) {
        this.code = codeSnippet;
        this.language = options.language || 'python';
        this.container = options.container || document.getElementById('flowchart-container');
        this.includeComments = options.includeComments || false;
        this.maxDepth = options.maxDepth || 5;

        this.nodes = [];
        this.edges = [];
        this.nodeIdCounter = 0;
    }

    /**
     * Generate flowchart from code
     */
    generate() {
        if (!this.code || !this.container) {
            console.error('Code or container not provided');
            return;
        }

        // Parse code based on language
        switch (this.language.toLowerCase()) {
            case 'python':
                this.parsePython();
                break;
            case 'javascript':
            case 'js':
                this.parseJavaScript();
                break;
            default:
                this.parseGeneric();
        }

        // Generate Mermaid syntax
        const mermaidSyntax = this.generateMermaidSyntax();

        // Render flowchart
        this.render(mermaidSyntax);
    }

    /**
     * Parse Python code
     */
    parsePython() {
        const lines = this.code.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('#'));

        let startNode = this.addNode('Start', 'start');
        let currentNode = startNode;

        lines.forEach((line, index) => {
            // Function definition
            if (line.startsWith('def ')) {
                const funcName = line.match(/def\s+(\w+)/)[1];
                const node = this.addNode(`Function: ${funcName}`, 'process');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // If statement
            else if (line.startsWith('if ')) {
                const condition = line.replace('if ', '').replace(':', '').trim();
                const node = this.addNode(condition, 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // Elif statement
            else if (line.startsWith('elif ')) {
                const condition = line.replace('elif ', '').replace(':', '').trim();
                const node = this.addNode(condition, 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // Else statement
            else if (line.startsWith('else:')) {
                const node = this.addNode('Else', 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // For loop
            else if (line.startsWith('for ')) {
                const loopVar = line.match(/for\s+(\w+)/)[1];
                const node = this.addNode(`Loop: ${loopVar}`, 'process');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // While loop
            else if (line.startsWith('while ')) {
                const condition = line.replace('while ', '').replace(':', '').trim();
                const node = this.addNode(`While: ${condition}`, 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // Return statement
            else if (line.startsWith('return ')) {
                const value = line.replace('return ', '').trim();
                const node = this.addNode(`Return: ${value}`, 'end');
                this.addEdge(currentNode, node);
            }
            // Assignment or function call
            else if (line.includes('=') || line.includes('(')) {
                const description = line.length > 30 ? line.substring(0, 30) + '...' : line;
                const node = this.addNode(description, 'process');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
        });

        // Add end node if not already there
        if (currentNode && currentNode.type !== 'end') {
            const endNode = this.addNode('End', 'end');
            this.addEdge(currentNode, endNode);
        }
    }

    /**
     * Parse JavaScript code
     */
    parseJavaScript() {
        const lines = this.code.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('//'));

        let startNode = this.addNode('Start', 'start');
        let currentNode = startNode;

        lines.forEach(line => {
            // Function declaration
            if (line.startsWith('function ') || line.includes('=>')) {
                const funcName = line.match(/function\s+(\w+)/) ? line.match(/function\s+(\w+)/)[1] : 'Arrow Function';
                const node = this.addNode(`Function: ${funcName}`, 'process');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // If statement
            else if (line.startsWith('if ')) {
                const condition = line.replace('if ', '').replace(/[({]/, '').trim();
                const node = this.addNode(condition, 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // Else if
            else if (line.startsWith('else if ')) {
                const condition = line.replace('else if ', '').replace(/[({]/, '').trim();
                const node = this.addNode(condition, 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // Else
            else if (line.startsWith('else')) {
                const node = this.addNode('Else', 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // For loop
            else if (line.startsWith('for ')) {
                const node = this.addNode('Loop', 'process');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // While loop
            else if (line.startsWith('while ')) {
                const condition = line.replace('while ', '').replace(/[({]/, '').trim();
                const node = this.addNode(`While: ${condition}`, 'decision');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
            // Return
            else if (line.startsWith('return ')) {
                const value = line.replace('return ', '').replace(';', '').trim();
                const node = this.addNode(`Return: ${value}`, 'end');
                this.addEdge(currentNode, node);
            }
            // Assignment or call
            else if (line.includes('=') || line.includes('(')) {
                const description = line.length > 30 ? line.substring(0, 30) + '...' : line.replace(';', '');
                const node = this.addNode(description, 'process');
                this.addEdge(currentNode, node);
                currentNode = node;
            }
        });

        if (currentNode && currentNode.type !== 'end') {
            const endNode = this.addNode('End', 'end');
            this.addEdge(currentNode, endNode);
        }
    }

    /**
     * Generic parser for other languages
     */
    parseGeneric() {
        const startNode = this.addNode('Start', 'start');
        const processNode = this.addNode('Process Code', 'process');
        const endNode = this.addNode('End', 'end');

        this.addEdge(startNode, processNode);
        this.addEdge(processNode, endNode);
    }

    /**
     * Add a node to the flowchart
     */
    addNode(label, type = 'process') {
        const nodeId = `node${this.nodeIdCounter++}`;
        const node = {
            id: nodeId,
            label: label,
            type: type
        };
        this.nodes.push(node);
        return node;
    }

    /**
     * Add an edge between two nodes
     */
    addEdge(fromNode, toNode, label = '') {
        this.edges.push({
            from: fromNode.id,
            to: toNode.id,
            label: label
        });
    }

    /**
     * Generate Mermaid.js syntax
     */
    generateMermaidSyntax() {
        let mermaid = 'flowchart TD\n';

        // Add nodes
        this.nodes.forEach(node => {
            let nodeStr = '';

            switch (node.type) {
                case 'start':
                case 'end':
                    nodeStr = `    ${node.id}([${node.label}])`;
                    break;
                case 'decision':
                    nodeStr = `    ${node.id}{${node.label}}`;
                    break;
                case 'process':
                default:
                    nodeStr = `    ${node.id}[${node.label}]`;
            }

            mermaid += nodeStr + '\n';
        });

        // Add edges
        this.edges.forEach(edge => {
            const edgeLabel = edge.label ? `|${edge.label}|` : '';
            mermaid += `    ${edge.from} ${edgeLabel}-->  ${edge.to}\n`;
        });

        // Add styling
        mermaid += `
    classDef startEnd fill:#d4edda,stroke:#28a745,stroke-width:2px;
    classDef decision fill:#fff3cd,stroke:#ffc107,stroke-width:2px;
    classDef process fill:#cfe2ff,stroke:#0d6efd,stroke-width:2px;
`;

        // Apply classes
        this.nodes.forEach(node => {
            if (node.type === 'start' || node.type === 'end') {
                mermaid += `    class ${node.id} startEnd\n`;
            } else if (node.type === 'decision') {
                mermaid += `    class ${node.id} decision\n`;
            } else {
                mermaid += `    class ${node.id} process\n`;
            }
        });

        return mermaid;
    }

    /**
     * Render the flowchart using Mermaid.js
     */
    render(mermaidSyntax) {
        if (!this.container) return;

        this.container.innerHTML = `<div class="mermaid">${mermaidSyntax}</div>`;

        // Initialize Mermaid if available
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({
                startOnLoad: true,
                theme: 'default',
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true,
                    curve: 'basis'
                }
            });
            mermaid.run({
                querySelector: '.mermaid'
            });
        } else {
            console.warn('Mermaid.js not loaded. Include it in your page to see flowcharts.');
            this.container.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i>
                    Mermaid.js library not loaded. Include it to view flowcharts.
                </div>
            `;
        }
    }

    /**
     * Export flowchart as SVG
     */
    async exportSVG() {
        const svgElement = this.container.querySelector('svg');
        if (!svgElement) return null;

        const serializer = new XMLSerializer();
        return serializer.serializeToString(svgElement);
    }

    /**
     * Download flowchart as PNG
     */
    async downloadPNG(filename = 'flowchart.png') {
        const svgElement = this.container.querySelector('svg');
        if (!svgElement) return;

        const svgData = new XMLSerializer().serializeToString(svgElement);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        const img = new Image();
        img.onload = function() {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);

            canvas.toBlob(blob => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
            });
        };

        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }
}

/**
 * Simple flowchart from Mermaid syntax
 */
function renderMermaidFlowchart(mermaidSyntax, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `<div class="mermaid">${mermaidSyntax}</div>`;

    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({ startOnLoad: true });
        mermaid.run({ querySelector: '.mermaid' });
    }
}

/**
 * Auto-generate flowchart on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    const codeFlowchartContainer = document.getElementById('flowchart-container');
    const codeSnippet = document.getElementById('code-snippet');

    if (codeFlowchartContainer && codeSnippet) {
        const code = codeSnippet.textContent;
        const language = codeSnippet.className.match(/language-(\w+)/)?.[1] || 'python';

        const generator = new FlowchartGenerator(code, {
            language: language,
            container: codeFlowchartContainer
        });

        // Generate button
        const generateBtn = document.getElementById('generate-flowchart-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                generator.generate();
            });
        }

        // Export button
        const exportBtn = document.getElementById('export-flowchart-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                generator.downloadPNG('code-flowchart.png');
            });
        }
    }
});

// Export for global use
window.FlowchartGenerator = FlowchartGenerator;
window.renderMermaidFlowchart = renderMermaidFlowchart;
