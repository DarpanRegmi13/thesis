document.getElementById('chat-form').onsubmit = function(event) {
    event.preventDefault();

    var question = document.getElementById('question').value;
    var chatBox = document.getElementById('chat-box');

    // Add the user's question to the chat
    chatBox.innerHTML += `<div class="user-msg">🧑‍💻 You: ${question}</div>`;  // Corrected with backticks
    document.getElementById('question').value = '';

    // Make the request to the Flask backend
    fetch('http://127.0.0.1:5005/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',  // Change to application/json
        },
        body: JSON.stringify({ question: question })  // Send data as JSON
    })
    .then(response => response.json())
    .then(data => {
        // Add the AI's response to the chat
        chatBox.innerHTML += `<div class="ai-msg">🤖 IR-AI: ${data.answer}</div>`;  // Corrected with backticks
        chatBox.scrollTop = chatBox.scrollHeight;  // Scroll to the bottom
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    })
    .catch(error => {
        console.error('Error:', error);
        chatBox.innerHTML += `<div class="ai-msg">AI: Sorry, something went wrong!</div>`;  // Corrected with backticks
        chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
    });
};


function loadChatHistory(filename) {
    fetch(`http://127.0.0.1:5005/load_session/${filename}`)
        .then(response => response.json())  // Expecting a JSON response
        .then(data => {
            // Log the data to ensure it's an array of messages
            console.log(data);  // Check the data structure

            // Create a new chat container (or modal)
            var newChatBox = document.createElement('div');
            newChatBox.classList.add('loaded-chat-container');  // Add a specific class for styling
            document.body.appendChild(newChatBox);  // Append to the body or a specific section

            // Title for the new chat box
            var chatTitle = document.createElement('h2');
            chatTitle.textContent = 'Loaded Chat History';
            newChatBox.appendChild(chatTitle);

            // Add each message from the history to the new chat box
            data.forEach(msg => {
                var messageDiv = document.createElement('div');
                messageDiv.classList.add(msg.sender === 'user' ? 'user-msg' : 'ai-msg');
                messageDiv.innerHTML = `${msg.sender === 'user' ? 'You' : 'IR-AI'}: ${msg.message}`;
                newChatBox.appendChild(messageDiv);  // Append each message to the new chat box
            });

            // Optional: Add a close button to close the new chat box/modal
            var closeButton = document.createElement('button');
            closeButton.textContent = 'Close';
            closeButton.onclick = function() {
                newChatBox.remove();  // Remove the chat box when closing
            };
            newChatBox.appendChild(closeButton);

            // Scroll to the bottom of the new chat box
            newChatBox.scrollTop = newChatBox.scrollHeight;
        })
        .catch(error => {
            console.error('Error loading session:', error);
            alert('Failed to load chat history');
        });
}



document.getElementById('load-chat-btn').onclick = function() {
    // Request the list of available sessions from the server
    fetch('http://127.0.0.1:5005/get_sessions')
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                alert("No saved chat sessions found.");
                return;
            }

            // Create a dropdown to select a session
            var sessionSelect = document.createElement('select');
            sessionSelect.id = 'session-select';
            data.forEach(session => {
                var option = document.createElement('option');
                option.value = session;
                option.textContent = session;
                sessionSelect.appendChild(option);
            });

            // Append the dropdown to the page
            var loadSection = document.getElementById('load-chat-section');
            loadSection.innerHTML = '';  // Clear previous content
            loadSection.appendChild(sessionSelect);

            // Add a button to load the selected session
            var loadButton = document.createElement('button');
            loadButton.textContent = 'Load Selected Chat';
            loadSection.appendChild(loadButton);

            loadButton.onclick = function() {
                var selectedSession = sessionSelect.value;
                loadChatHistory(selectedSession);
            };
        })
        .catch(error => {
            console.error('Error fetching sessions:', error);
            alert('Could not load saved sessions.');
        });
};

document.getElementById('save-chat-btn').onclick = function() {
    var chatBox = document.getElementById('chat-box');
    var chatHistory = [];

    // Loop through the chat messages and store them
    var messages = chatBox.querySelectorAll('.user-msg, .ai-msg');
    messages.forEach(msg => {
        var sender = msg.classList.contains('user-msg') ? 'user' : 'ai';
        var messageText = msg.innerText.replace(sender === 'user' ? 'You: ' : '🤖 IR-AI: ', '');
        chatHistory.push({ sender: sender, message: messageText });
    });

    // Prompt user for the filename
    var filename = prompt("Enter a name for the chat history file (without extension):");

    if (filename) {
        // Ensure the filename ends with .json
        var finalFilename = filename.endsWith('.json') ? filename : filename + '.json';

        // Save the chat history as a JSON file by sending it to the backend
        fetch('http://127.0.0.1:5005/save_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filename: finalFilename,
                chatHistory: chatHistory
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Chat history saved successfully!');
            } else {
                alert('Error saving chat history');
            }
        })
        .catch(error => {
            console.error('Error saving chat history:', error);
            alert('Failed to save chat history');
        });
    } else {
        alert("Filename is required.");
    }
};



// Handle PDF file upload functionality
document.getElementById('upload-pdf-form').onsubmit = function(event) {
    event.preventDefault();

    var fileInput = document.getElementById('file');
    var formData = new FormData();

    // Append the PDF file to the form data
    formData.append('file', fileInput.files[0]);

    // Make the request to upload the PDF
    fetch('http://127.0.0.1:5005/upload_pdf', {
        method: 'POST',
        body: formData  // Send the form data containing the file
    })
    .then(response => response.json())
    .then(data => {
        // Handle the server response (you can show a success message, etc.)
        if (data.success) {
            alert('PDF uploaded successfully and IncidenceResponseAI got trained!');
        } else {
            alert('Failed to upload PDF');
        }
    })
    .catch(error => {
        console.error('Error uploading PDF:', error);
        alert('Error uploading PDF');
    });
};

