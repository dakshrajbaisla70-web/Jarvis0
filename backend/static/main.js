const chatDiv = document.getElementById('chat');
const input = document.getElementById('input');

function addMessage(role, text) {
  const el = document.createElement('div');
  el.className = 'msg ' + (role === 'user' ? 'user' : 'bot');
  el.textContent = (role === 'user' ? 'You: ' : 'Jarvis: ') + text;
  chatDiv.appendChild(el);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

input.addEventListener('keydown', async (e) => {
  if (e.key === 'Enter') {
    const text = input.value.trim();
    if (!text) return;
    addMessage('user', text);
    input.value = '';

    addMessage('bot', '... thinking ...');
    try {
      const resp = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await resp.json();
      // Remove the "... thinking ..." placeholder
      const last = chatDiv.lastChild;
      if (last && last.textContent.startsWith('Jarvis: ...')) {
        chatDiv.removeChild(last);
      }
      addMessage('bot', data.reply);
    } catch (err) {
      console.error(err);
      addMessage('bot', 'Error: could not reach server');
    }
  }
});
