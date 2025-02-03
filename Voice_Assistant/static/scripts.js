document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const voiceButton = document.getElementById('voice-input-button');
    const clearButton = document.getElementById('clear-button');
    const toggleVoiceResponseButton = document.getElementById('toggle-voice-response');

    let isRecording = false;
    let mediaRecorder = null;
    let audioChunks = [];
    let voiceResponseEnabled = false;
    const sessionId = Date.now().toString();

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        
        // Add timestamp
        const timestamp = new Date().toLocaleTimeString();
        const timeSpan = document.createElement('span');
        timeSpan.className = 'message-time';
        timeSpan.textContent = timestamp;
        
        // Add message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeSpan);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage(message, type = 'text') {
        try {
            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator';
            typingDiv.textContent = 'AI is typing...';
            chatMessages.appendChild(typingDiv);

            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    type: type,
                    session_id: sessionId,
                    voice_response: voiceResponseEnabled
                })
            });

            // Remove typing indicator
            chatMessages.removeChild(typingDiv);

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            addMessage(data.reply, false);

            // Handle audio response if present and voice response is enabled
            if (data.audio && voiceResponseEnabled) {
                const audio = new Audio(`data:audio/mp3;base64,${data.audio}`);
                audio.play();
            }

        } catch (error) {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = error.message || 'An error occurred. Please try again.';
            chatMessages.appendChild(errorDiv);
        }
    }

    function handleSubmit() {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, true);
            sendMessage(message);
            userInput.value = '';
        }
    }

    async function clearHistory() {
        try {
            await fetch('/api/clear-history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
            
            chatMessages.innerHTML = '';
            addMessage("Chat history cleared!", false);
        } catch (error) {
            console.error('Error clearing history:', error);
        }
    }

    // Event listeners
    sendButton.addEventListener('click', handleSubmit);
    clearButton.addEventListener('click', clearHistory);

    toggleVoiceResponseButton.addEventListener('click', () => {
        voiceResponseEnabled = !voiceResponseEnabled;
        toggleVoiceResponseButton.classList.toggle('active');
        toggleVoiceResponseButton.textContent = voiceResponseEnabled ? '🔊' : '🔇';
    });

    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    });

    // Voice input functionality
    voiceButton.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };

                mediaRecorder.onstop = async () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64Audio = reader.result.split(',')[1];
                        sendMessage(base64Audio, 'voice');
                    };
                };

                mediaRecorder.start();
                isRecording = true;
                voiceButton.classList.add('recording');
            } catch (error) {
                console.error('Error accessing microphone:', error);
                addMessage('Error accessing microphone. Please check your permissions.', false);
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            voiceButton.classList.remove('recording');
        }
    });
});
