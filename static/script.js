document.addEventListener("DOMContentLoaded", () => {

    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chat-messages");
    const welcomeScreen = document.getElementById("welcome-screen");
    const actionLinks = document.querySelectorAll(".action-link");
    const newChatBtn = document.getElementById("new-chat");

    chatForm.addEventListener("submit", (event) => {
        event.preventDefault();
        handleUserMessage();
    });

    actionLinks.forEach(link => {
        link.addEventListener("click", (event) => {
            event.preventDefault();
            const message = link.getAttribute("data-message");
            userInput.value = message;
            handleUserMessage();
        });
    });

    newChatBtn.addEventListener("click", () => {
        window.location.reload();
    });


    async function handleUserMessage() {
        const message = userInput.value.trim();
        if (message === "") return;

        const welcomeScreen = document.getElementById("welcome-screen");
        if (welcomeScreen && welcomeScreen.style.display !== 'none') {
            welcomeScreen.style.display = 'none';
        }

        addMessageToChat(message, "user");

        userInput.value = "";

        const typingMessage = addMessageToChat("Typing...", "bot", true);

        try {
            const response = await fetch("http://127.0.0.1:5000/run", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ user_input: message })
            });

            if (!response.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await response.json();
            /*const botResponse = data.response || "Sorry, I couldn't understand that.";*/
            const botResponse = data.agent_output || data.response || "Sorry, I couldn't understand that.";

            chatMessages.removeChild(typingMessage);

            addMessageToChat(botResponse, "bot");

        } catch (error) {
            console.error("Error:", error);
            if (typingMessage) chatMessages.removeChild(typingMessage);
            addMessageToChat("Error: Could not connect to the bot.", "bot");
        }
    }

    function addMessageToChat(text, sender, isTyping = false) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", `${sender}-message`);

        const avatarIcon = sender === "user" ? "person" : "smart_toy";

        let content;
        if (isTyping) {
            content = `
            <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
            </div>
            `;
        } else {
            content = `<p>${text}</p>`;
        }

        messageElement.innerHTML = `
        <span class="material-symbols-outlined avatar">${avatarIcon}</span>
        <div class="message-content">
        ${content}
        ${!isTyping ? `<span class="timestamp">${getCurrentTimestamp()}</span>` : ''}
        </div>
        `;

        chatMessages.appendChild(messageElement);

        chatMessages.scrollTop = chatMessages.scrollHeight;

        return messageElement;
    }

    function getCurrentTimestamp() {
        return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

});
