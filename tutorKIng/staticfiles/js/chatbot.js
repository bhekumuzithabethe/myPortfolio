const messagesList = document.getElementsByClassName('messages-list')[0];
const messageForm = document.getElementsByClassName('message-form')[0];
const messageInput = document.getElementsByClassName('message-input')[0];

messageForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (message.length === 0) return;

  // Add user's message
  const messageItem = document.createElement('li');
  messageItem.classList.add('message', 'sent');
  messageItem.innerHTML = `
    <div class="message-text">
        <div class="message-sender"><b>You</b></div>
        <div class="message-content">${message}</div>
    </div>`;
  messagesList.appendChild(messageItem);
  messageInput.value = '';
  messagesList.scrollTop = messagesList.scrollHeight;

  // Show typing indicator
  const typingIndicator = document.createElement('li');
  typingIndicator.classList.add('typing-indicator');
  typingIndicator.innerHTML = `
    <div class="dots">
        <h4>Hang in there, I'll respond to you in a moment.</h4><span></span><span></span><span></span>
    </div>`;
  messagesList.appendChild(typingIndicator);
  messagesList.scrollTop = messagesList.scrollHeight;

  // Send message to backend
  fetch('', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      'csrfmiddlewaretoken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      'message': message
    })
  })
  .then(response => response.json())
  .then(data => {
    messagesList.removeChild(typingIndicator);

    // Format response with line breaks
    const formattedResponse = data.response.replace(/\n/g, '<br>');

    const responseItem = document.createElement('li');
    responseItem.classList.add('message', 'received');
    responseItem.innerHTML = `
      <div class="message-text">
          <div class="message-sender"><b>Thabethe AI</b></div>
          <div class="message-content">${formattedResponse}</div>
      </div>`;
    messagesList.appendChild(responseItem);
    messagesList.scrollTop = messagesList.scrollHeight;
  })
  .catch(error => {
    messagesList.removeChild(typingIndicator);
    console.error('Error:', error);
    alert('Failed to send your message. Please try again later.');
  });
});