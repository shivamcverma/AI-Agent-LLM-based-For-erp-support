
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const chatMessages = document.getElementById("chatMessages");
const typingIndicator = document.getElementById("typingIndicator");

const CHAT_STORAGE_KEY = "erp_chat_history";
const UNDERSTANDING_STORAGE_KEY = "ERP_LAST_UNDERSTANDING";

const CHAT_EXPIRY_TIME = 24 * 60 * 60 * 1000; // 24 hours


// ==========================================
// EVENTS
// ==========================================

sendButton.addEventListener("click", sendMessage);

messageInput.addEventListener("keydown", function (event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendMessage();
    }
});


// ==========================================
// LOAD CHAT HISTORY
// ==========================================

loadChatHistory();


// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage() {

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    messageInput.value = "";

    sendButton.disabled = true;

    typingIndicator.classList.add("active");


    try {

        console.log("====================================");
        console.log("Sending message:", message);
        console.log("====================================");


        // ======================================
        // SHOW USER MESSAGE IMMEDIATELY
        // ======================================
        
        addMessage(message, "user");

        const schoolId = 1;


        // ======================================
        // GET CONVERSATION HISTORY
        // ======================================

        const conversationHistory =
            getConversationHistory();


        // ======================================
        // GET PREVIOUS NLU CONTEXT
        // ======================================

        const previousUnderstanding =
            getLastUnderstanding();


        console.log(
            "PREVIOUS UNDERSTANDING SENT =",
            previousUnderstanding
        );

        console.log(
            "CONVERSATION HISTORY SENT =",
            conversationHistory
        );


        // ======================================
        // API REQUEST
        // ======================================

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                school_id: schoolId,

                conversation_history:
                    conversationHistory,

                previous_understanding:
                    previousUnderstanding

            })

        });


        console.log(
            "API status:",
            response.status
        );


        // ======================================
        // READ RESPONSE
        // ======================================

        const raw = await response.text();

        console.log(
            "RAW API RESPONSE:",
            raw
        );


        let data;

        try {

            data = JSON.parse(raw);

        } catch (error) {

            console.error(
                "JSON parse error:",
                error
            );

            throw new Error(
                "Invalid JSON response from server."
            );
        }


        console.log(
            "API response:",
            data
        );


        // ======================================
        // SAVE STRUCTURED UNDERSTANDING
        // ======================================

        if (data.understanding) {

            saveLastUnderstanding(
                data.understanding
            );

        } else {

            console.warn(
                "No understanding returned by backend."
            );

        }


        // ======================================
        // HANDLE ERROR
        // ======================================

        if (!response.ok) {

            throw new Error(

                data.detail ||
                data.message ||
                "Something went wrong"

            );

        }


        // ======================================
        // SHOW BOT RESPONSE
        // ======================================

        addMessage(

            data.response ||
            "No response received.",

            "bot",

            data.steps || []

        );


    } catch (error) {

        console.error(
            "Chat request failed:",
            error
        );

        addMessage(

            error.message ||
            "Unable to send your message. Please try again.",

            "bot"

        );


    } finally {

        sendButton.disabled = false;

        typingIndicator.classList.remove("active");

        messageInput.focus();

    }

}


// ==========================================
// SAVE LAST NLU UNDERSTANDING
// ==========================================

function saveLastUnderstanding(understanding) {

    if (!understanding) {

        console.warn(
            "Cannot save empty understanding."
        );

        return;
    }


    const storageObject = {

        understanding: understanding,

        timestamp: Date.now()

    };


    localStorage.setItem(

        UNDERSTANDING_STORAGE_KEY,

        JSON.stringify(storageObject)

    );


    console.log(
        "SAVED UNDERSTANDING =",
        understanding
    );


    // DEBUG: immediately read it back

    const verify =
        localStorage.getItem(
            UNDERSTANDING_STORAGE_KEY
        );


    console.log(
        "LOCAL STORAGE VERIFY =",
        verify
    );
}


// ==========================================
// GET LAST NLU UNDERSTANDING
// ==========================================

function getLastUnderstanding() {

    const stored =
        localStorage.getItem(
            UNDERSTANDING_STORAGE_KEY
        );


    console.log(
        "RAW STORED UNDERSTANDING =",
        stored
    );


    if (!stored) {

        console.log(
            "NO PREVIOUS UNDERSTANDING FOUND"
        );

        return null;
    }


    try {

        const parsed =
            JSON.parse(stored);


        // ==================================
        // CHECK EXPIRY
        // ==================================

        if (

            !parsed.timestamp ||

            (
                Date.now() -
                parsed.timestamp
            ) >= CHAT_EXPIRY_TIME

        ) {

            console.log(
                "PREVIOUS UNDERSTANDING EXPIRED"
            );


            localStorage.removeItem(
                UNDERSTANDING_STORAGE_KEY
            );


            return null;
        }


        console.log(
            "LOADED PREVIOUS UNDERSTANDING =",
            parsed.understanding
        );


        return parsed.understanding || null;


    } catch (error) {

        console.error(
            "Invalid stored understanding:",
            error
        );


        localStorage.removeItem(
            UNDERSTANDING_STORAGE_KEY
        );


        return null;
    }
}


// ==========================================
// ADD MESSAGE
// ==========================================

function addMessage(
    message,
    sender,
    steps = [],
    save = true
) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add("message");

    messageDiv.classList.add(

        sender === "user"
            ? "user-message"
            : "bot-message"

    );


    const avatar =
        document.createElement("div");

    avatar.classList.add("avatar");

    avatar.textContent =
        sender === "user"
            ? "👤"
            : "🤖";


    const content =
        document.createElement("div");

    content.classList.add(
        "message-content"
    );


    const name =
        document.createElement("div");

    name.classList.add(
        "message-name"
    );

    name.textContent =
        sender === "user"
            ? "You"
            : "ERP Assistant";


    const text =
        document.createElement("div");

    text.classList.add(
        "message-text"
    );

    content.appendChild(name);
    content.appendChild(text);

    if (sender === "bot" && save === true) {
        text.textContent = "";
        let i = 0;
        const typingSpeed = 20; // 20 milliseconds per character for better visibility

        function typeWriter() {
            if (i < message.length) {
                text.textContent += message.charAt(i);
                i++;
                chatMessages.scrollTo({
                    top: chatMessages.scrollHeight
                });
                setTimeout(typeWriter, typingSpeed);
            }
        }
        typeWriter();
    } else {
        text.textContent = message;
    }

    // ======================================
    // SHOW STEPS
    // ======================================

    if (steps && steps.length > 0) {

        const stepsTitle =
            document.createElement("div");

        stepsTitle.classList.add(
            "steps-title"
        );

        stepsTitle.textContent =
            "Steps:";


        content.appendChild(
            stepsTitle
        );


        const stepsList =
            document.createElement("ol");

        stepsList.classList.add(
            "steps-list"
        );


        steps.forEach(function (step) {

            const stepItem =
                document.createElement("li");

            stepItem.textContent = step;

            stepsList.appendChild(
                stepItem
            );

        });


        content.appendChild(
            stepsList
        );
    }


    messageDiv.appendChild(
        avatar
    );

    messageDiv.appendChild(
        content
    );


    chatMessages.appendChild(
        messageDiv
    );


    // ======================================
    // SAVE MESSAGE
    // ======================================

    if (save) {

        saveChatMessage(

            message,
            sender,
            steps

        );

    }


    // ======================================
    // SCROLL
    // ======================================

    requestAnimationFrame(() => {

        chatMessages.scrollTo({

            top:
                chatMessages.scrollHeight,

            behavior:
                "smooth"

        });

    });
}


// ==========================================
// SAVE CHAT MESSAGE
// ==========================================

function saveChatMessage(
    message,
    sender,
    steps = []
) {

    let history =
        getChatHistory();


    history.push({

        message: message,

        sender: sender,

        steps: steps,

        timestamp: Date.now()

    });


    localStorage.setItem(

        CHAT_STORAGE_KEY,

        JSON.stringify(history)

    );
}


// ==========================================
// GET CHAT HISTORY
// ==========================================

function getChatHistory() {

    const storedData =
        localStorage.getItem(
            CHAT_STORAGE_KEY
        );


    if (!storedData) {

        return [];

    }


    try {

        const history =
            JSON.parse(storedData);


        const now =
            Date.now();


        const validHistory =
            history.filter(
                function (item) {

                    return (

                        now -
                        item.timestamp

                    ) < CHAT_EXPIRY_TIME;

                }
            );


        localStorage.setItem(

            CHAT_STORAGE_KEY,

            JSON.stringify(validHistory)

        );


        return validHistory;


    } catch (error) {

        console.error(
            "Invalid chat history:",
            error
        );


        localStorage.removeItem(
            CHAT_STORAGE_KEY
        );


        return [];

    }
}


// ==========================================
// LOAD CHAT HISTORY
// ==========================================

function loadChatHistory() {

    const history =
        getChatHistory();


    history.forEach(
        function (item) {

            addMessage(

                item.message,

                item.sender,

                item.steps,

                false

            );

        }
    );


    if (history.length > 0) {

        requestAnimationFrame(() => {

            chatMessages.scrollTop =
                chatMessages.scrollHeight;

        });

    }
}


// ==========================================
// GET CONVERSATION HISTORY
// ==========================================

function getConversationHistory() {

    const history =
        getChatHistory();


    return history.map(
        function (item) {

            return {

                role:
                    item.sender === "user"
                        ? "user"
                        : "assistant",

                content:
                    item.message

            };

        }
    );
}


// ==========================================
// THEME TOGGLE LOGIC
// ==========================================

const themeToggle = document.getElementById("themeToggle");
const THEME_STORAGE_KEY = "erp_chat_theme";

// Load theme on startup
const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || "light";
if (savedTheme === "dark") {
    document.body.setAttribute("data-theme", "dark");
    if(themeToggle) themeToggle.textContent = "☀️";
}

if(themeToggle) {
    themeToggle.addEventListener("click", () => {
        const isDark = document.body.getAttribute("data-theme") === "dark";
        if (isDark) {
            document.body.removeAttribute("data-theme");
            themeToggle.textContent = "🌙";
            localStorage.setItem(THEME_STORAGE_KEY, "light");
        } else {
            document.body.setAttribute("data-theme", "dark");
            themeToggle.textContent = "☀️";
            localStorage.setItem(THEME_STORAGE_KEY, "dark");
        }
    });
}
