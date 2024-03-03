
        const chatContainer = document.querySelector('#chat_container');
        const form = document.querySelector('#chat_form');

        // Initialize with initial message
        chatContainer.innerHTML += `
            <div class="wrapper user">
                <div class="chat">
                    <div class="profile">
                        <img src="{% static 'user.svg' %}" alt="User">
                    </div>
                    <div class="message">{{ initial_message }}</div>
                </div>
            </div>
        `;

        form.addEventListener('submit', handleSubmit);

        function handleSubmit(event) {
            event.preventDefault();
            const formData = new FormData(form);
            const prompt = formData.get('prompt');

            // Your AJAX request here to send the message to the server
            // Use fetch or other AJAX methods as needed
            
            // Example AJAX request using fetch
            fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'  // Include CSRF token if using CSRF protection
                },
                body: JSON.stringify({ prompt: prompt })
            })
            .then(response => response.json())
            .then(data => handleResponse(data))
            .catch(error => console.error('Error:', error));
        }

        function handleResponse(data) {
            // Handle response from the server
            // Update the chatContainer with bot's response
            chatContainer.innerHTML += `
                <div class="wrapper ai">
                    <div class="chat">
                        <div class="profile">
                            <img src="{% static 'bot.svg' %}" alt="Bot">
                        </div>
                        <div class="message">${data.bot}</div>
                    </div>
                </div>
            `;
        }