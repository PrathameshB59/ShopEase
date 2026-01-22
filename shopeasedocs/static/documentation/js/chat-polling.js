/**
 * ShopEase Documentation - Developer Chat AJAX Polling
 * Handles real-time message updates using polling
 */

class ChatPoller {
    constructor(threadId, pollingInterval = 5000) {
        this.threadId = threadId;
        this.pollingInterval = pollingInterval;
        this.lastMessageTimestamp = null;
        this.isPolling = false;
        this.pollTimer = null;
        this.currentUserId = null;
        this.messageContainer = document.getElementById('messages-container');
        this.messageForm = document.getElementById('message-form');

        this.init();
    }

    init() {
        // Get current user ID from data attribute
        const userDataEl = document.querySelector('[data-user-id]');
        if (userDataEl) {
            this.currentUserId = parseInt(userDataEl.dataset.userId);
        }

        // Set initial timestamp from latest message
        const messages = this.messageContainer.querySelectorAll('.message-item');
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            this.lastMessageTimestamp = lastMessage.dataset.timestamp;
        }

        // Start polling
        this.startPolling();

        // Handle message form submission
        if (this.messageForm) {
            this.messageForm.addEventListener('submit', (e) => this.handleMessageSubmit(e));
        }

        // Handle scroll to bottom button
        this.initScrollToBottom();

        // Stop polling when leaving page
        window.addEventListener('beforeunload', () => this.stopPolling());
    }

    startPolling() {
        if (this.isPolling) return;

        this.isPolling = true;
        this.poll();
    }

    stopPolling() {
        this.isPolling = false;
        if (this.pollTimer) {
            clearTimeout(this.pollTimer);
            this.pollTimer = null;
        }
    }

    async poll() {
        if (!this.isPolling) return;

        try {
            const url = new URL(window.location.origin + `/dev/chat/${this.threadId}/messages/`);
            if (this.lastMessageTimestamp) {
                url.searchParams.append('since', this.lastMessageTimestamp);
            }

            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.messages && data.messages.length > 0) {
                this.appendNewMessages(data.messages);

                // Update last timestamp
                const lastMessage = data.messages[data.messages.length - 1];
                this.lastMessageTimestamp = lastMessage.created_at;

                // Scroll to bottom if user is near bottom
                this.scrollToBottomIfNeeded();
            }

            // Update thread status if changed
            if (data.thread_status) {
                this.updateThreadStatus(data.thread_status);
            }

        } catch (error) {
            console.error('Polling error:', error);
        }

        // Schedule next poll
        if (this.isPolling) {
            this.pollTimer = setTimeout(() => this.poll(), this.pollingInterval);
        }
    }

    appendNewMessages(messages) {
        messages.forEach(message => {
            if (!this.messageExists(message.id)) {
                const messageElement = this.createMessageElement(message);
                this.messageContainer.appendChild(messageElement);

                // Animate new message
                messageElement.classList.add('message-fade-in');
            }
        });
    }

    messageExists(messageId) {
        return this.messageContainer.querySelector(`[data-message-id="${messageId}"]`) !== null;
    }

    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `message-item ${message.author_id === this.currentUserId ? 'sent' : 'received'}`;
        div.dataset.messageId = message.id;
        div.dataset.timestamp = message.created_at;

        const timestamp = new Date(message.created_at).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        div.innerHTML = `
            <div class="message-bubble">
                <div class="message-header">
                    <strong>${this.escapeHtml(message.author)}</strong>
                    <small class="text-muted ms-2">${timestamp}</small>
                    ${message.is_edited ? '<span class="badge bg-secondary ms-2">Edited</span>' : ''}
                </div>
                <div class="message-content">${this.escapeHtml(message.content)}</div>
                ${message.attachment_url ? `
                    <div class="message-attachment">
                        <a href="${message.attachment_url}" target="_blank" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-paperclip"></i> Attachment
                        </a>
                    </div>
                ` : ''}
            </div>
        `;

        return div;
    }

    async handleMessageSubmit(e) {
        e.preventDefault();

        const formData = new FormData(this.messageForm);
        const contentInput = this.messageForm.querySelector('textarea[name="content"]');

        if (!contentInput.value.trim()) {
            return;
        }

        // Disable form while sending
        this.messageForm.querySelectorAll('input, textarea, button').forEach(el => {
            el.disabled = true;
        });

        try {
            const response = await fetch(`/dev/chat/${this.threadId}/post/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Clear form
                contentInput.value = '';
                const fileInput = this.messageForm.querySelector('input[type="file"]');
                if (fileInput) {
                    fileInput.value = '';
                }

                // Append message immediately (don't wait for polling)
                if (!this.messageExists(data.message.id)) {
                    const messageElement = this.createMessageElement(data.message);
                    this.messageContainer.appendChild(messageElement);
                    messageElement.classList.add('message-fade-in');

                    // Update last timestamp
                    this.lastMessageTimestamp = data.message.created_at;
                }

                // Scroll to bottom
                this.scrollToBottom();
            } else {
                alert('Failed to send message: ' + (data.error || 'Unknown error'));
            }

        } catch (error) {
            console.error('Send message error:', error);
            alert('Failed to send message. Please try again.');
        } finally {
            // Re-enable form
            this.messageForm.querySelectorAll('input, textarea, button').forEach(el => {
                el.disabled = false;
            });
            contentInput.focus();
        }
    }

    initScrollToBottom() {
        const scrollBtn = document.getElementById('scroll-to-bottom');
        if (scrollBtn) {
            scrollBtn.addEventListener('click', () => this.scrollToBottom());
        }

        // Show/hide scroll button based on scroll position
        if (this.messageContainer) {
            this.messageContainer.addEventListener('scroll', () => {
                if (scrollBtn) {
                    const isAtBottom = this.isScrolledToBottom();
                    scrollBtn.style.display = isAtBottom ? 'none' : 'block';
                }
            });
        }
    }

    scrollToBottom(smooth = true) {
        if (this.messageContainer) {
            this.messageContainer.scrollTo({
                top: this.messageContainer.scrollHeight,
                behavior: smooth ? 'smooth' : 'auto'
            });
        }
    }

    scrollToBottomIfNeeded() {
        if (this.isScrolledToBottom(100)) {
            this.scrollToBottom();
        }
    }

    isScrolledToBottom(threshold = 50) {
        if (!this.messageContainer) return true;

        const { scrollTop, scrollHeight, clientHeight } = this.messageContainer;
        return scrollHeight - scrollTop - clientHeight < threshold;
    }

    updateThreadStatus(status) {
        const statusBadge = document.getElementById('thread-status');
        if (statusBadge) {
            statusBadge.textContent = status;
            statusBadge.className = 'badge';

            switch (status) {
                case 'OPEN':
                    statusBadge.classList.add('bg-success');
                    break;
                case 'RESOLVED':
                    statusBadge.classList.add('bg-primary');
                    break;
                case 'ARCHIVED':
                    statusBadge.classList.add('bg-secondary');
                    break;
            }
        }
    }

    getCookie(name) {
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat poller when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        const threadId = chatContainer.dataset.threadId;
        if (threadId) {
            window.chatPoller = new ChatPoller(parseInt(threadId));
        }
    }
});
