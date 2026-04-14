// RAG Production Frontend JavaScript

class RAGFrontend {
    constructor() {
        this.apiBase = ''; // Use relative URLs to avoid CORS issues
        this.documents = [];
        this.currentStatus = 'connecting';
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkHealth();
        this.loadDocuments();
        this.loadStats();
        
        // Initialize Mermaid
        if (typeof mermaid !== 'undefined') {
            mermaid.initialize({ 
                startOnLoad: false,
                theme: 'default',
                securityLevel: 'loose'
            });
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => this.checkHealth(), 30000);
        setInterval(() => this.loadStats(), 30000);
    }

    bindEvents() {
        // File upload
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        // Drag and drop
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0]);
                }
            });
        }

        // Chat functionality
        const questionInput = document.getElementById('questionInput');
        const askBtn = document.getElementById('askBtn');
        
        askBtn.addEventListener('click', () => this.askQuestion());
        questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.askQuestion();
            }
        });

        // Refresh buttons
        document.getElementById('refreshBtn').addEventListener('click', () => this.checkHealth());
        document.getElementById('refreshDocsBtn').addEventListener('click', () => this.loadDocuments());
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBase}/health`);
            const data = await response.json();
            
            this.updateStatus(data.status === 'healthy' ? 'online' : 'offline');
            
            if (data.status === 'healthy') {
                this.enableChat();
            } else {
                this.disableChat();
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.updateStatus('offline');
            this.disableChat();
        }
    }

    updateStatus(status) {
        this.currentStatus = status;
        const statusElement = document.getElementById('status');
        const statusDot = statusElement.querySelector('i');
        
        statusElement.className = 'status-indicator';
        
        switch (status) {
            case 'online':
                statusElement.classList.add('online');
                statusElement.innerHTML = '<i class="fas fa-circle status-dot online"></i>Online';
                break;
            case 'offline':
                statusElement.classList.add('offline');
                statusElement.innerHTML = '<i class="fas fa-circle status-dot offline"></i>Offline';
                break;
            case 'connecting':
                statusElement.classList.add('connecting');
                statusElement.innerHTML = '<i class="fas fa-circle status-dot connecting"></i>Connecting...';
                break;
        }
    }

    enableChat() {
        document.getElementById('questionInput').disabled = false;
        document.getElementById('askBtn').disabled = false;
    }

    disableChat() {
        document.getElementById('questionInput').disabled = true;
        document.getElementById('askBtn').disabled = true;
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFileUpload(file);
        }
    }

    async handleFileUpload(file) {
        if (file.type !== 'application/pdf') {
            this.showToast('Please upload a PDF file', 'error');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            this.showToast('File size must be less than 10MB', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        this.showUploadProgress(0);

        try {
            const response = await fetch(`${this.apiBase}/upload-pdf`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }

            const result = await response.json();
            this.hideUploadProgress();
            this.showToast(`Document "${file.name}" uploaded successfully!`, 'success');
            this.loadDocuments();
            this.loadStats();

        } catch (error) {
            console.error('Upload error:', error);
            this.hideUploadProgress();
            this.showToast(`Upload failed: ${error.message}`, 'error');
        }
    }

    showUploadProgress(percent) {
        document.getElementById('uploadProgress').classList.remove('hidden');
        document.getElementById('progressBar').style.width = `${percent}%`;
        document.getElementById('progressPercent').textContent = `${percent}%`;
    }

    hideUploadProgress() {
        document.getElementById('uploadProgress').classList.add('hidden');
        document.getElementById('fileInput').value = '';
    }

    async loadDocuments() {
        try {
            const response = await fetch(`${this.apiBase}/documents`);
            const data = await response.json();
            
            this.documents = data.documents || [];
            this.renderDocuments();
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.showToast('Failed to load documents', 'error');
        }
    }

    renderDocuments() {
        const container = document.getElementById('documentsList');
        
        if (this.documents.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-sm">No documents uploaded yet</p>';
            return;
        }

        container.innerHTML = this.documents.map(doc => `
            <div class="document-item" data-id="${doc.id}">
                <div class="document-item-header">
                    <div class="document-item-title" title="${doc.filename}">
                        <i class="fas fa-file-pdf text-red-500 mr-2"></i>
                        ${doc.filename}
                    </div>
                    <div class="document-item-actions">
                        <button class="btn-icon delete" onclick="ragFrontend.deleteDocument('${doc.id}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="document-item-meta">
                    ${doc.chunk_count} chunks · ${this.formatFileSize(doc.file_size)} · ${this.formatDate(doc.uploaded_at)}
                </div>
            </div>
        `).join('');
    }

    async deleteDocument(documentId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/documents/${documentId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Delete failed');
            }

            this.showToast('Document deleted successfully', 'success');
            this.loadDocuments();
            this.loadStats();

        } catch (error) {
            console.error('Delete error:', error);
            this.showToast(`Delete failed: ${error.message}`, 'error');
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            const data = await response.json();
            
            document.getElementById('docCount').textContent = data.document_count || 0;
            document.getElementById('chunkCount').textContent = data.total_chunks || 0;
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    async askQuestion() {
        const questionInput = document.getElementById('questionInput');
        const question = questionInput.value.trim();
        
        if (!question) {
            return;
        }

        const maxChunks = parseInt(document.getElementById('maxChunks').value);
        
        // Add user message
        this.addMessage('user', question);
        questionInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch(`${this.apiBase}/ask`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    max_context_chunks: maxChunks
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to get answer');
            }

            const result = await response.json();
            this.hideTypingIndicator();
            this.addMessage('ai', result.answer, result);

        } catch (error) {
            console.error('Question error:', error);
            this.hideTypingIndicator();
            this.addMessage('ai', `Sorry, I encountered an error: ${error.message}`);
        }
    }

    addMessage(sender, content, metadata = null) {
        const chatMessages = document.getElementById('chatMessages');
        
        // Remove welcome message if it exists
        const welcomeMessage = chatMessages.querySelector('.text-center');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        const avatar = sender === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        let messageContent = `
            <div class="chat-avatar ${sender}">${avatar}</div>
            <div class="chat-content">
                <div class="chat-bubble">${this.formatMessage(content)}</div>
                <div class="chat-time">${this.formatTime(new Date())}</div>
            </div>
        `;

        // Add sources if available
        if (metadata && metadata.sources && metadata.sources.length > 0) {
            messageContent += this.renderSources(metadata.sources);
        }

        // Add follow-up questions if available
        if (metadata && metadata.follow_up_questions && metadata.follow_up_questions.length > 0) {
            messageContent += this.renderFollowUpQuestions(metadata.follow_up_questions);
        }

        messageDiv.innerHTML = messageContent;
        chatMessages.appendChild(messageDiv);
        
        // Render Mermaid diagrams if any
        this.renderMermaidDiagramsInElement(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Bind follow-up question clicks
        if (metadata && metadata.follow_up_questions) {
            this.bindFollowUpQuestions(messageDiv);
        }
    }

    renderSources(sources) {
        return `
            <div class="sources-section">
                <div class="sources-title">Sources</div>
                ${sources.map(source => `
                    <div class="source-item">
                        <div class="source-text">${source.text_preview}</div>
                        <div class="source-meta">Document ${source.document_id} · Chunk ${source.chunk_index}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderFollowUpQuestions(questions) {
        return `
            <div class="followup-section">
                <div class="followup-title">Follow-up Questions</div>
                ${questions.map(question => `
                    <button class="followup-question" data-question="${question}">
                        ${question}
                    </button>
                `).join('')}
            </div>
        `;
    }

    bindFollowUpQuestions(messageDiv) {
        const followUpButtons = messageDiv.querySelectorAll('.followup-question');
        followUpButtons.forEach(button => {
            button.addEventListener('click', () => {
                const question = button.getAttribute('data-question');
                document.getElementById('questionInput').value = question;
                document.getElementById('questionInput').focus();
            });
        });
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const indicator = document.createElement('div');
        indicator.className = 'chat-message ai';
        indicator.id = 'typingIndicator';
        indicator.innerHTML = `
            <div class="chat-avatar ai"><i class="fas fa-robot"></i></div>
            <div class="chat-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        chatMessages.appendChild(indicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <i class="${icons[type]} toast-icon"></i>
            <div class="toast-message">${message}</div>
            <i class="fas fa-times toast-close" onclick="this.parentElement.remove()"></i>
        `;

        container.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    formatMessage(content) {
        // Handle Mermaid diagrams first
        content = this.renderMermaidDiagrams(content);
        
        // Convert URLs to links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        content = content.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
        
        // Convert markdown-style formatting to HTML
        content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold
        content = content.replace(/\*(.*?)\*/g, '<em>$1</em>'); // Italic
        
        // Convert bullet points
        content = content.replace(/^[\s]*[-*]\s+(.+)$/gm, '<li>$1</li>');
        content = content.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // Convert numbered lists
        content = content.replace(/^[\s]*\d+\.\s+(.+)$/gm, '<li>$1</li>');
        
        // Convert line breaks to <br> for remaining content
        content = content.replace(/\n\n/g, '</p><p>');
        content = content.replace(/\n/g, '<br>');
        
        // Wrap in paragraphs if not already
        if (!content.includes('<p>') && !content.includes('<ul>') && !content.includes('mermaid')) {
            content = '<p>' + content + '</p>';
        }
        
        return content;
    }

    renderMermaidDiagrams(content) {
        // Replace Mermaid code blocks with div elements that will be rendered
        const mermaidRegex = /```mermaid\n([\s\S]*?)```/g;
        let diagramIndex = 0;
        
        content = content.replace(mermaidRegex, (match, diagramCode) => {
            const diagramId = `mermaid-diagram-${Date.now()}-${diagramIndex++}`;
            return `<div class="mermaid-diagram-container">
                <div class="mermaid-diagram" id="${diagramId}" data-mermaid="${encodeURIComponent(diagramCode.trim())}">
                    <div class="mermaid-loading">Loading diagram...</div>
                </div>
            </div>`;
        });
        
        return content;
    }

    async renderMermaidDiagramsInElement(element) {
        if (typeof mermaid === 'undefined') return;
        
        const mermaidContainers = element.querySelectorAll('.mermaid-diagram');
        
        for (const container of mermaidContainers) {
            try {
                const diagramCode = decodeURIComponent(container.getAttribute('data-mermaid'));
                const diagramId = container.id;
                
                // Clear loading message
                container.innerHTML = '';
                
                // Render the diagram
                const { svg } = await mermaid.render(diagramId + '-svg', diagramCode);
                container.innerHTML = svg;
                
            } catch (error) {
                console.error('Error rendering Mermaid diagram:', error);
                container.innerHTML = `<div class="mermaid-error">Error rendering diagram: ${error.message}</div>`;
            }
        }
    }

    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize the frontend when DOM is loaded
let ragFrontend;
document.addEventListener('DOMContentLoaded', () => {
    ragFrontend = new RAGFrontend();
});
