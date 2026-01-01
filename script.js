const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const liveToggle = document.getElementById('live-toggle');


const HARDCODED_CONTEXT = {
    client_id: "9a1b2c3d-4e5f-4a91-8911-2c3d4e500001",
    user_id: "user123",
    lat: 19.564262,
    long: 74.206425
};

let chatHistory = [];



function appendMessage(text, isAi = false, results = []) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isAi ? 'ai-message' : 'user-message'}`;

    // AI message text
    const textNode = document.createElement('div');
    textNode.innerText = text;
    msgDiv.appendChild(textNode);

    // Results if any
    if (results && results.length > 0) {
        const grid = document.createElement('div');
        grid.className = 'results-grid';

        results.forEach(res => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.innerHTML = `
                <h4>${res.name}</h4>
                <div class="result-detail">📞 ${res.phone_number || res.number || 'N/A'}</div>
                <div class="result-detail">📍 ${res.distance || 'N/A'} km</div>
            `;
            grid.appendChild(card);
        });
        msgDiv.appendChild(grid);
    }

    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    const liveMode = liveToggle.checked;
    appendMessage(text, false);

    userInput.value = '';

    // Show loading
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai-message loading';
    loadingDiv.innerText = 'Searching nearby...';
    chatWindow.appendChild(loadingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch('http://localhost:8000/ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: text,
                history: chatHistory.slice(-5),
                live_mode: liveMode,
                ...HARDCODED_CONTEXT
            })

        });

        const data = await response.json();
        chatWindow.removeChild(loadingDiv);

        if (response.ok) {
            appendMessage(data.ai_response, true, data.results);
            // Store in history
            chatHistory.push({ role: 'user', content: text });
            chatHistory.push({ role: 'ai', content: data.ai_response });
            if (chatHistory.length > 10) chatHistory = chatHistory.slice(-10); // Keep buffer
        } else {
            appendMessage(`Error: ${data.detail}`, true);
        }
    } catch (error) {
        chatWindow.removeChild(loadingDiv);
        appendMessage(`Connection error: ${error.message}`, true);
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
