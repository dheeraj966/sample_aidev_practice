document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const askAiCheckbox = document.getElementById('ask-ai');
    const messagesContainer = document.getElementById('messages');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatList = document.getElementById('chat-list');

    let currentChatId = null;
    let chats = [];

    // Function to fetch chats
    async function fetchChats() {
        try {
            const response = await fetch('/api/chats');
            if (!response.ok) {
                throw new Error('Failed to fetch chats');
            }
            chats = await response.json();
            renderChatList();
            createNewChat();
        } catch (error) {
            console.error('Error fetching chats:', error);
        }
    }

    // Function to render the chat list
    function renderChatList() {
        chatList.innerHTML = '';
        chats.forEach(chatId => {
            const li = document.createElement('li');
            li.textContent = `Chat ${chatId.substring(0, 8)}...`;
            li.dataset.chatId = chatId;
            if (chatId === currentChatId) {
                li.classList.add('active');
            }
            li.addEventListener('click', () => switchChat(chatId));
            chatList.appendChild(li);
        });
    }

    // Function to switch chat
    function switchChat(chatId) {
        currentChatId = chatId;
        messagesContainer.innerHTML = ''; // Clear messages
        fetchMessages();

        // Move the switched chat to the top of the chats array
        const index = chats.indexOf(chatId);
        if (index > -1) {
            chats.splice(index, 1);
            chats.unshift(chatId);
        }
        renderChatList(); // Re-render to update active class and order
    }

    // Function to create a new chat
    async function createNewChat() {
        try {
            const response = await fetch('/api/chats', { method: 'POST' });
            if (!response.ok) {
                throw new Error('Failed to create new chat');
            }
            const data = await response.json();
            const newChatId = data.chat_id;
            chats.unshift(newChatId);
            switchChat(newChatId);
        } catch (error)
        {
            console.error('Error creating new chat:', error);
        }
    }

    // Function to fetch messages for the current chat
    async function fetchMessages() {
        if (!currentChatId) return;
        try {
            const response = await fetch(`/api/messages/${currentChatId}`);
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
        messagesContainer.innerHTML = ''; // Clear existing messages
        messages.forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.className = message.is_ai ? 'message ai-message' : 'message';
            
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
        });
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Function to send a message
    async function sendMessage(text, askAi) {
        if (!currentChatId) return;
        try {
            const response = await fetch(`/api/messages/${currentChatId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    text: text,
                    ask_ai: askAi
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send message');
            }
            
            const newMessages = await response.json();
            // Append new messages to the current view
            newMessages.forEach(message => {
                const messageElement = document.createElement('div');
                messageElement.className = message.is_ai ? 'message ai-message' : 'message';
                
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
            });
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
        } catch (error) {
            console.error('Error sending message:', error);
        }
    }

    // Initial fetch
    fetchChats();

    // Event Listeners
    newChatBtn.addEventListener('click', createNewChat);

    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const text = messageInput.value.trim();
        if (!text) return;
        
        const askAi = askAiCheckbox.checked;
        
        messageInput.value = '';
        sendMessage(text, askAi);
    });
});