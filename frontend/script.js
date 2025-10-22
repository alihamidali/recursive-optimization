class RecursionTester {
    constructor() {
        this.baseUrl = 'http://localhost:8000';
        this.wsUrl = 'ws://localhost:8000/ws';
        this.websocket = null;
        this.isConnected = false;

        this.initializeEventListeners();
        this.connectWebSocket();
    }

    initializeEventListeners() {
        document.getElementById('computeSingle').addEventListener('click',
            () => this.computeSingle());
        document.getElementById('stressTest').addEventListener('click',
            () => this.stressTest(5000));
        document.getElementById('optimizedTest').addEventListener('click',
            () => this.optimizedTest(10000));

        document.querySelector('.close').addEventListener('click',
            () => this.hideModal());
    }

    async connectWebSocket() {
        try {
            this.websocket = new WebSocket(this.wsUrl);

            this.websocket.onopen = () => {
                this.isConnected = true;
                console.log('WebSocket connected');
            };

            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };

            this.websocket.onclose = () => {
                this.isConnected = false;
                console.log('WebSocket disconnected');
            };

        } catch (error) {
            console.error('WebSocket connection failed:', error);
        }
    }

    handleWebSocketMessage(data) {
        if (data.type === 'progress') {
            this.updateProgress(data.value);
        } else if (data.type === 'result') {
            this.displayResult(data.data);
            this.hideProgress();
        }
    }

    async computeSingle() {
        const algorithm = document.getElementById('algorithm').value;
        const depth = parseInt(document.getElementById('depth').value);
        const optimized = document.getElementById('optimized').checked;

        this.showProgress();

        try {
            const response = await fetch(`${this.baseUrl}/compute/${algorithm}?depth=${depth}&optimized=${optimized}`, {
                method: 'POST'
            });

            const result = await response.json();
            this.displayResult(result);
            this.hideProgress();

        } catch (error) {
            this.displayError('Computation failed: ' + error.message);
            this.hideProgress();
        }
    }

    async stressTest(numRequests) {
        this.showProgress();
        const algorithm = document.getElementById('algorithm').value;
        const depth = parseInt(document.getElementById('depth').value);
        const optimized = false; // Force unoptimized for stress test

        let completed = 0;
        let errors = 0;
        const startTime = Date.now();

        const requests = Array.from({length: numRequests}, (_, i) => ({
            algorithm,
            depth: depth + (i % 10), // Vary depth slightly
            optimized
        }));

        // Process in batches to avoid overwhelming the server
        const batchSize = 100;
        for (let i = 0; i < requests.length; i += batchSize) {
            const batch = requests.slice(i, i + batchSize);

            const promises = batch.map(async (request) => {
                try {
                    const response = await fetch(
                        `${this.baseUrl}/compute/${request.algorithm}?depth=${request.depth}&optimized=${request.optimized}`,
                        { method: 'POST' }
                    );
                    const result = await response.json();

                    if (!result.success) {
                        errors++;
                        this.logError(`Request ${completed + 1}: ${result.error}`);
                    }

                } catch (error) {
                    errors++;
                    this.logError(`Request ${completed + 1}: ${error.message}`);
                }

                completed++;
                this.updateProgress((completed / numRequests) * 100);
            });

            await Promise.allSettled(promises);
        }

        const totalTime = (Date.now() - startTime) / 1000;
        this.displayMetrics({
            totalRequests: numRequests,
            completed: completed,
            errors: errors,
            totalTime: totalTime,
            requestsPerSecond: completed / totalTime
        });

        this.hideProgress();
    }

    async optimizedTest(numRequests) {
        this.showProgress();
        const algorithm = document.getElementById('algorithm').value;
        const depth = parseInt(document.getElementById('depth').value);
        const optimized = true; // Force optimized

        let completed = 0;
        let errors = 0;
        const startTime = Date.now();

        const requests = Array.from({length: numRequests}, (_, i) => ({
            algorithm,
            depth: depth + (i % 5), // Smaller variation for optimized test
            optimized
        }));

        // Process in larger batches for optimized version
        const batchSize = 200;
        for (let i = 0; i < requests.length; i += batchSize) {
            const batch = requests.slice(i, i + batchSize);

            const promises = batch.map(async (request) => {
                try {
                    const response = await fetch(
                        `${this.baseUrl}/compute/${request.algorithm}?depth=${request.depth}&optimized=${request.optimized}`,
                        { method: 'POST' }
                    );
                    const result = await response.json();

                    if (!result.success) {
                        errors++;
                        this.logError(`Request ${completed + 1}: ${result.error}`);
                    }

                } catch (error) {
                    errors++;
                    this.logError(`Request ${completed + 1}: ${error.message}`);
                }

                completed++;
                this.updateProgress((completed / numRequests) * 100);
            });

            await Promise.allSettled(promises);
        }

        const totalTime = (Date.now() - startTime) / 1000;
        this.displayMetrics({
            totalRequests: numRequests,
            completed: completed,
            errors: errors,
            totalTime: totalTime,
            requestsPerSecond: completed / totalTime
        });

        this.hideProgress();
    }

    showProgress() {
        document.getElementById('progressSection').classList.remove('hidden');
        this.updateProgress(0);
    }

    hideProgress() {
        document.getElementById('progressSection').classList.add('hidden');
    }

    updateProgress(percent) {
        document.getElementById('progressFill').style.width = percent + '%';
        document.getElementById('progressText').textContent =
            Math.round(percent) + '% Complete';
    }

    displayResult(result) {
        const resultElement = document.getElementById('latestResult');

        if (result.success) {
            resultElement.innerHTML = `
                <div class="metric-item success">
                    <span>Success:</span>
                    <span>✓</span>
                </div>
                <div class="metric-item">
                    <span>Result:</span>
                    <span>${typeof result.result === 'object' ? 
                        JSON.stringify(result.result).substring(0, 100) + '...' : 
                        result.result}</span>
                </div>
                <div class="metric-item">
                    <span>Execution Time:</span>
                    <span>${result.execution_time.toFixed(4)}s</span>
                </div>
                <div class="metric-item">
                    <span>Memory Peak:</span>
                    <span>${this.formatBytes(result.memory_peak)}</span>
                </div>
                <div class="metric-item">
                    <span>Recursion Depth:</span>
                    <span>${result.recursion_depth}</span>
                </div>
            `;
        } else {
            resultElement.innerHTML = `
                <div class="metric-item error">
                    <span>Error:</span>
                    <span>✗</span>
                </div>
                <div class="metric-item">
                    <span>Message:</span>
                    <span>${result.error}</span>
                </div>
                <div class="metric-item">
                    <span>Execution Time:</span>
                    <span>${result.execution_time.toFixed(4)}s</span>
                </div>
            `;

            this.showErrorModal(result.error);
        }
    }

    displayMetrics(metrics) {
        const metricsElement = document.getElementById('performanceMetrics');
        metricsElement.innerHTML = `
            <div class="metric-item">
                <span>Total Requests:</span>
                <span>${metrics.totalRequests}</span>
            </div>
            <div class="metric-item">
                <span>Completed:</span>
                <span>${metrics.completed}</span>
            </div>
            <div class="metric-item">
                <span>Errors:</span>
                <span>${metrics.errors}</span>
            </div>
            <div class="metric-item">
                <span>Success Rate:</span>
                <span>${((1 - metrics.errors / metrics.completed) * 100).toFixed(2)}%</span>
            </div>
            <div class="metric-item">
                <span>Total Time:</span>
                <span>${metrics.totalTime.toFixed(2)}s</span>
            </div>
            <div class="metric-item">
                <span>Requests/Second:</span>
                <span>${metrics.requestsPerSecond.toFixed(2)}</span>
            </div>
            <div class="metric-item">
                <span>Timestamp:</span>
                <span>${new Date().toLocaleString()}</span>
            </div>
        `;
    }

    logError(message) {
        const errorLog = document.getElementById('errorLog');
        const timestamp = new Date().toLocaleTimeString();
        errorLog.innerHTML += `[${timestamp}] ${message}\n`;
        errorLog.scrollTop = errorLog.scrollHeight;
    }

    showErrorModal(message) {
        document.getElementById('modalMessage').textContent = message;
        document.getElementById('errorModal').classList.remove('hidden');
    }

    hideModal() {
        document.getElementById('errorModal').classList.add('hidden');
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new RecursionTester();
});