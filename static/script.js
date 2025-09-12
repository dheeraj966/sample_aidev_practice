document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const askAiCheckbox = document.getElementById('ask-ai');
    const messagesContainer = document.getElementById('messages');

    // Function to fetch messages
    async function fetchMessages() {
        try {
            const response = await fetch('/api/messages');
            if (!response.ok) {
                throw new Error('Failed to fetch messages');
            }
            const messages = await response.json();
            renderMessages(messages);
        } catch (error) {
            console.error('Error fetching messages:', error);
        }
    }

    // Function to render messages
    function renderMessages(messages) {
        // Get existing message IDs
        const existingIds = new Set(
            Array.from(messagesContainer.children)
                .map(element => element.dataset.id)
        );

        // Add only new messages
        messages.forEach(message => {
            if (!existingIds.has(message.id)) {
                const messageElement = document.createElement('div');
                messageElement.className = message.is_ai ? 'message ai-message' : 'message';
                messageElement.dataset.id = message.id;

                // Add AI indicator if it's an AI message
                if (message.is_ai) {
                    const aiIndicator = document.createElement('div');
                    aiIndicator.className = 'ai-indicator';
                    aiIndicator.textContent = 'AI';
                    messageElement.appendChild(aiIndicator);
                }

                const textElement = document.createElement('div');
                if (message.is_ai) {
                    textElement.innerHTML = marked.parse(message.text);
                } else {
                    textElement.textContent = message.text;
                }
                messageElement.appendChild(textElement);

                messagesContainer.appendChild(messageElement);

                // Scroll to bottom
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        });
    }

    // Function to send a message
    async function sendMessage(text, askAi) {
        try {
            console.log(`Sending message: "${text}", ask_ai: ${askAi}`);

            const response = await fetch('/api/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text,
                    ask_ai: askAi
                })
            });

            console.log(`Response status: ${response.status}`);

            if (!response.ok) {
                throw new Error('Failed to send message');
            }

            const messages = await response.json();
            console.log(`Received ${messages.length} messages:`, messages);
            renderMessages(messages);

        } catch (error) {
            console.error('Error sending message:', error);
        }
    }

    // Initial fetch
    fetchMessages();

    // Form submission
    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const text = messageInput.value.trim();
        if (!text) return;

        const askAi = askAiCheckbox.checked;

        messageInput.value = '';
        sendMessage(text, askAi);
    });

    // Poll for new messages
    setInterval(fetchMessages, 6000);
});
