async function sendMessage() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;
    
    const chatMsgs = document.getElementById('chatMessages');
    chatMsgs.innerHTML += `<div class="message msg-user">${msg}</div>`;
    input.value = '';
    
    try {
        const res = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question: msg})
        });
        const data = await res.json();
        
        chatMsgs.innerHTML += `<div class="message msg-bot">${data.answer}</div>`;
        chatMsgs.scrollTop = chatMsgs.scrollHeight;
    } catch (e) {
        chatMsgs.innerHTML += `<div class="message msg-bot" style="color:var(--danger)">Error connecting to AI.</div>`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chatInput');
    if (input) {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});
