/*
* Title: Global variable
* Description: 
* Use: 
* 
*/
let isStreaming = false;
let chatHistory = [];
let isAutoScroll = true; // Now indicates if auto-scrolling is enable
let conversationId =  getConversationId_fromURL();

// let isExistedId = await conversationExists(convoId);

// console.log("ConversatonId:", conversationId); // Logs: Chat Status: new_chat

/*
* Title: Global Element(Div)
* Description: get, create, append Element
* Use: 
* 
*/
const elements = {
    chataddNewChatFromLayout: document.getElementById("chataddNewChatFromLayout"),
    chatContainer: document.getElementById("chatContainer"),
    chatMessage: document.getElementById("chatMessage"),
    showMessage: document.getElementById("showMessage"),
    userPrompt: document.getElementById("userPrompt"),
    toggleButton: document.getElementById("toggleButton"),
    chatInput: document.getElementById("chatInput"),
    scrollToBottomBtn: document.getElementById("scrollToBottomBtn"), // New element
};  

let startButtonSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 19V5" />
        <polyline points="5 12 12 5 19 12" />
    </svg>`;
let stopButtonSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="2" y="2" width="20" height="20" rx="2" ry="2" stroke="currentColor" stroke-width="2" fill="none" />
    </svg>`;

// Create Message Element for role=user
function createUserMessage(userPrompt) {
    const userDiv = document.createElement("div");
    userDiv.className = "user";
    userDiv.innerHTML = `<div class="role_box">${userPrompt}</div>`;
    return userDiv;
}

// Create Message Element for role=model
function createModelMessage() {
    const modelDiv = document.createElement("div");
    modelDiv.className = "model";
    modelDiv.style.minHeight = "calc(100vh - 330px)";
    modelDiv.innerHTML = `<div class="role_box">
        <div class="loading-text">
            <span>L</span><span>o</span><span>a</span><span>d</span><span>i</span><span>n</span><span>g</span>
            <span>.</span><span>.</span><span>.</span>
        </div>
    </div>`;
    return modelDiv;
}

function incrementUserMessageLimitOnHeader() {
    let span = document.getElementById("userMessageLimit");
    let currentValue = parseInt(span.innerText);
    span.innerText = currentValue + 1;
}


/*
* Markdown IT
* Description: 
* Use: use in steamResponse
* 
*/
const md = window.markdownit({
    html: true,
    breaks: true,
    highlight: function (str, lang) {
        if (lang && window.hljs?.getLanguage(lang)) {
            // If a valid language is detected, format as highlighted code
            return `<pre><code class="hljs">${window.hljs.highlight(str, { language: lang }).value}</code></pre>`;
        }
        // Return null to bypass default code block rendering
        return null;
    }
});

// LIST
// Override the default code_block and fence rendering
md.renderer.rules.code_block = function (tokens, idx, options, env, self) {
    const token = tokens[idx];
    const content = token.content;
    // Use md.render() for block-level content, wrapped once
    return `<div class="markdown-content">${md.render(content)}</div>`;
};

md.renderer.rules.fence = function (tokens, idx, options, env, self) {
    const token = tokens[idx];
    const content = token.content;
    const lang = token.info.trim();
    
    if (lang && window.hljs?.getLanguage(lang)) {
        return `<pre><code class="hljs language-${lang}">${window.hljs.highlight(content, { language: lang }).value}</code></pre>`;
    }
    // Use md.render() for block-level content, wrapped once
    return `<div class="markdown-content">${md.render(content)}</div>`;
};

// Customize list rendering for different levels
md.renderer.rules.list_item_open = function (tokens, idx, options, env, self) {
    const token = tokens[idx];
    const level = env.listLevel || 0; // Track nesting level
    let className = 'markdown-list'; // Default for level 0
    if (level === 1) className = 'nested-list-level1';
    else if (level > 1) className = 'nested-list-level2';
    return `<li class="${className}">`;
};

// TABLE
// Add this after the existing renderer rules
md.renderer.rules.table_open = function (tokens, idx, options, env, self) {
    return '<table class="markdown-table">';
};

md.renderer.rules.table_close = function (tokens, idx, options, env, self) {
    return '</table>';
};

md.renderer.rules.th_open = function (tokens, idx, options, env, self) {
    return '<th class="markdown-th">';
};

md.renderer.rules.td_open = function (tokens, idx, options, env, self) {
    return '<td class="markdown-td">';
};

function formatCodeBlock(code, lang) {
    if (!code.trim()) return '';
    
    if (lang && window.hljs?.getLanguage(lang)) {
        return `<pre><code class="hljs language-${lang}">${window.hljs.highlight(code.trim(), { language: lang }).value}</code></pre>`;
    }
    
    // Wrap markdown-rendered content in a div with margin-left
    return `<div class="markdown-content">${md.render(code.trim())}</div>`;
}

function formatChunk(text, codeBuffer, inCodeBlock, lang) {
    if (inCodeBlock) {
        return formatCodeBlock(codeBuffer, lang);
    }
    return text.trim() ? md.render(text.trim()) : '';
}

/*
* Title: Function for Gemini API
* Description: fetch data from api (AI) by stream(chunk)
* Fuction: toggleChat, streamResponse=>(readStream), stopStream, handleStreamError, resetChatState
* Use globle variable: isStreaming,
* 
*/
function streamResponse(userPrompt, modelContent) {
    const api = globalModelApi();
    modelApiName = api.getActiveModel().modelValue;
    console.log(modelApiName);

    fetch("/api/ai/get_stream", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ userPrompt, modelApiName }), 
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let renderedContent = '';
        let codeBlockBuffer = '';
        let tableBuffer = '';
        let isInCodeBlock = false;
        let isInTable = false;
        let codeBlockLang = '';
        let fullResponseText = ''; // To store complete response text

        function renderPartialTable(tableContent) {
            // Split table into lines and ensure we have at least header and separator
            const lines = tableContent.trim().split('\n');
            if (lines.length < 2 || !lines[1].includes('---')) {
                return tableContent; // Not enough for a valid table yet
            }
            return md.render(tableContent);
        }

        async function readStream() {
            reader.read().then(async ({ done, value }) => {
                if (done) {
                    if (buffer || codeBlockBuffer || tableBuffer) {
                        if (isInTable) {
                            renderedContent += renderPartialTable(tableBuffer);
                        } else if (isInCodeBlock) {
                            renderedContent += formatCodeBlock(codeBlockBuffer, codeBlockLang);
                        } else {
                            renderedContent += md.render(buffer);
                        }
                        modelContent.innerHTML = renderedContent;
                    }
                    const modelMessage = { role: "model", content: renderedContent };
                    setChatHistory([modelMessage]);

                    // Save to database when stream is complete
                    sendMessageDB(senderRole="model", renderedContent, fullResponseText);

                    // Place updateConversationTitle here
                    if (elements.showMessage.children.length === 2) {

                        // Check if first child has class "user"
                        // const firstChild = elements.showMessage.children[0];
                        // if (firstChild.classList.contains("user")) {
                            const conversationId = getConversationId_fromURL();
                            // const newPrompt = firstChild.textContent.trim(); // Get text from user div instead of userPrompt input
                            await updateConversationTitle(conversationId, userPrompt);
                        
                        // }
                    }

                    resetChatState();
                    scrollToBottomByStream();
                    return;
                }


                const chunk = decoder.decode(value, { stream: true });
                fullResponseText += chunk; // Accumulate full response text

                buffer += chunk;
                const lines = buffer.split('\n');
                buffer = lines.pop();

                lines.forEach(line => {
                    // Handle code blocks
                    if (line.trim().startsWith('```')) {
                        if (isInCodeBlock) {
                            // End of code block
                            renderedContent += formatCodeBlock(codeBlockBuffer, codeBlockLang);
                            codeBlockBuffer = '';
                            isInCodeBlock = false;
                            codeBlockLang = '';
                        } else {
                            // Start of code block
                            if (tableBuffer) {
                                renderedContent += renderPartialTable(tableBuffer);
                                tableBuffer = '';
                                isInTable = false;
                            } else if (buffer.trim()) {
                                renderedContent += md.render(buffer.trim());
                            }
                            isInCodeBlock = true;
                            codeBlockLang = line.replace('```', '').trim();
                            codeBlockBuffer = '';
                        }
                    }
                    // Handle tables
                    else if (!isInCodeBlock && (line.includes('|') || line.includes('---'))) {
                        if (!isInTable && line.includes('|')) {
                            isInTable = true;
                        }
                        if (isInTable) {
                            tableBuffer += line + '\n';
                            // Render partial table if we have header and separator
                            if (tableBuffer.includes('---')) {
                                modelContent.innerHTML = renderedContent + renderPartialTable(tableBuffer);
                            }
                        }
                    }
                    else if (isInCodeBlock) {
                        codeBlockBuffer += line + '\n';
                    }
                    else {
                        if (tableBuffer) {
                            renderedContent += renderPartialTable(tableBuffer);
                            tableBuffer = '';
                            isInTable = false;
                        }
                        renderedContent += md.render(line);
                        modelContent.innerHTML = renderedContent;
                    }
                    scrollToBottomByStream();
                });

                // Update display with current content
                if (isInTable && tableBuffer.includes('---')) {
                    modelContent.innerHTML = renderedContent + renderPartialTable(tableBuffer);
                } else if (!isInCodeBlock && !isInTable) {
                    modelContent.innerHTML = renderedContent;
                }

                readStream();
            }).catch(err => handleStreamError(err, modelContent));
        }
        readStream();
    })
    .catch(err => handleStreamError(err, modelContent));
}

function handleStreamError(err, modelContent) {
    console.error("Stream error:", err);
    modelContent.innerHTML += "<p style='color: red;'>Error: Stream interrupted.</p>";
    resetChatState();
}

function resetChatState() {
    isStreaming = false;
    // elements.toggleButton.textContent = "Start Chat";
    elements.toggleButton.innerHTML = startButtonSvg;
    elements.userPrompt.disabled = false;
    elements.toggleButton.disabled = !elements.userPrompt.value.trim() && !isStreaming; // Disable if empty and not streaming
}

/*
* Title: Controll Function for Backend
* Description: 
* Use: 
* 
*/
async function toggleChat() {
    if (!isStreaming) {
        const userPrompt = elements.userPrompt.value.trim();
        if (!userPrompt) {
            alert("Please type a message to start the chat.");
            return;
        }

        if (elements.chatContainer && elements.chatContainer.classList.contains('justify-content-center')) {
            // Add the 'flex-grow-1' class
            elements.chatContainer.classList.add('justify-content-between');
            elements.chatContainer.classList.remove('justify-content-center');
            elements.chatMessage.classList.add('flex-grow-1');
        }

        // check user send limit for today
        canSend = await checkMessageLimit();
        if (!canSend) {
            console.log("checkMessageLimit():", "You reach 10 messages!")
            // Create the alert addNewChatFromLayout
            let alertDiv = document.createElement("div");
            alertDiv.className = "alert alert-warning d-flex align-items-center justify-content-between";
            alertDiv.setAttribute("role", "alert");
            alertDiv.innerHTML=`
                <div>
                    <strong>Oops!</strong> You've reached your daily message limit for today.
                </div>
                <button type="button" class="btn btn-primary btn-sm">
                    Upgrade Now
                </button>`;
            elements.showMessage.appendChild(alertDiv);
            elements.userPrompt.disabled = true;
            scrollToBottomManually()
            return
        } 
        incrementUserMessageLimitOnHeader()

        const userMessage = { role: "user", content: userPrompt };
        // chat_history.push(userMessage);
        setChatHistory([userMessage])
        sendMessageDB(senderRole="user", userPrompt, userPrompt);

        isStreaming = true;
        // elements.toggleButton.textContent = "Stop Chat";
        elements.toggleButton.innerHTML = stopButtonSvg;
        elements.userPrompt.disabled = true;

        // Create message elements
        const userDiv = createUserMessage(userPrompt);
        const modelDiv = createModelMessage();
        // Append html inside modelDiv
        const modelContent = modelDiv.querySelector(".role_box");

        // Check if there are any existing children (remove min-height from the last modelDev)
        if (elements.showMessage.children.length > 0) {
            // Find the last child1 and remove its min-height
            let existingModelDiv = elements.showMessage.querySelector('.model:last-of-type');
            if (existingModelDiv) {
                existingModelDiv.style.minHeight = '';
            }
        }

        // Append both children
        elements.showMessage.appendChild(userDiv);
        elements.showMessage.appendChild(modelDiv);
        

        scrollToBottomManually();
        streamResponse(userPrompt, modelContent);

        // Clear the textarea after starting the stream
        elements.userPrompt.value = "";  // Add this line
        adjustUserPromptHeight();  // Adjust the height after clearing to reset textarea size

    } else {
        stopStream();
        isStreaming = false;
    }
}

function stopStream() {
    fetch("/api/ai/stop_stream", { method: "POST" })
        .then(res => res.json())
        .then(data => console.log("Stop response:", data))
        .catch(err => console.error("Stop error:", err));
    resetChatState();
}

async function setChatHistory(newMessages) {
    try {
        const response = await fetch("/set_chat_history", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_history: newMessages })
        });
        const data = await response.json();
        console.log('setChatHistory:', data);
        // renderMessages(data)
    } catch (error) {
        console.error('Error setting chat history:', error);
    }
}

// function clearChat() {
//     fetch("/clear_history", { method: "POST" })
//         .then(response => response.json())
//         .catch(err => console.error("Clear error:", err))
//         .then(() => elements.showMessage.innerHTML = "");
// }

/*
* Title: Function for set global variable
* Description: 
* Set variable: conversationId,
* 
*/

// Get conversationId from URL instead of generating randomly
function getConversationId_fromURL() {
    const url = window.location.href;
    const urlObj = new URL(url);
    const pathSegments = urlObj.pathname.split('/');

    // Check if the URL matches the expected pattern: /chat/{id}
    if (pathSegments.length >= 3 && pathSegments[1] === 'chat') {
        
        convoId = pathSegments[2];
        return convoId; // Return the ID part
    }

    // Return empty string or null if pattern doesn't match
    return '';
}

/*
* Title: Database
* Description: 
* Use global variable: conversationId,
* Body: JSON.stringify({})
*/

// Function to render chat history to the UI
function renderMessages(myMessages) {
    // addNewChatFromLayout.innerHTML = ''; 
    myMessages.forEach(message => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 
            message.sender === 'user' ? 'user' : 'model');
        
        messageElement.innerHTML = `
            <div class="role_box">
                ${message.sender === 'user' ? message.message_text : message.message_html}
            </div>`;
        
        // elements.showMessage.appendChild(messageElement);
        // Prepend the message (add it before the first child)
        elements.showMessage.insertBefore(messageElement, elements.showMessage.firstChild);
    });
    
}

async function conversationExists(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}/exists`);

        const data = await response.json();
        return data.exists; // Return the boolean value

    } catch (error) {
        console.error("Network error or other issue:", error);
        return false; // Assume it doesn't exist on network errors (or handle differently)
    }
}

// Function to check message limit
async function checkMessageLimit() {
    try {
        // Make POST request to the API endpoint
        const response = await fetch('/api/user_message_limit/check_limit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Add any authentication headers if required
                // 'Authorization': `Bearer ${yourToken}`
            },
            credentials: 'include' // Include cookies/session data
        });

        // Parse the JSON response
        const data = await response.json();

        // Handle the response
        if (data.status === 'success') {
            console.log(data.message); // "Message sent successfully"
            return true;
        } else {
            console.log(data.message); // "Message limit reached"
            return false;
        }

    } catch (error) {
        console.error('Error checking message limit:', error);
        return false;
    }
}


// Add this script in your HTML file or separate JS file
document.addEventListener('DOMContentLoaded', () => {
    const chatMessage = document.getElementById('chatMessage');
    const showMessage = document.getElementById('showMessage');
    let offset = 0;
    const limit = 10;
    let isLoading = false;
    let hasMore = true;
    // const conversationId = /* your conversation ID here */; // Set this dynamically
    let loadingElement = null;

    // Initial load
    if (!conversationId) {
        elements.chatContainer.classList.remove('justify-content-between');
        elements.chatContainer.classList.add('justify-content-center');
        elements.chatMessage.classList.remove('flex-grow-1');
        return
    }

    elements.chatContainer.classList.add('justify-content-between');
    elements.chatContainer.classList.remove('justify-content-center');

    // Initial load
    getMessageByCoversatonId(conversationId);

    // Scroll event listener
    chatMessage.addEventListener('scroll', () => {
        if (chatMessage.scrollTop === 0 && !isLoading && hasMore) {
            console.log("Top", conversationId)
            getMessageByCoversatonId(conversationId);
        }
    });

    async function  getMessageByCoversatonId(conversationId) {
        if (isLoading || !hasMore) return;

        isLoading = true;
        showLoadingIndicator();
        try {
            const response = await fetch(`/api/messages/get_all/${conversationId}?offset=${offset}&limit=${limit}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const messages = data.messages;
                hasMore = data.has_more;

                // Store current scroll height
                const oldScrollHeight = chatMessage.scrollHeight;

                // Prepend messages (since we're loading older ones)
                // messages.reverse().forEach(message => {
                messages.forEach(message => {
                    const messageElement = createMessageElement(message);
                    showMessage.insertBefore(messageElement, showMessage.firstChild);
                });

                // Maintain scroll position
                const newScrollHeight = chatMessage.scrollHeight;
                chatMessage.scrollTop = newScrollHeight - oldScrollHeight;

                offset += messages.length;
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            // Optional: Show error message to user
            showErrorIndicator();
        } finally {
            isLoading = false;
            hideLoadingIndicator()
        }
    }

    function createMessageElement(message) {
        // const div = document.createElement('div');
        // div.className = 'message'; // Add your own styling class
        // div.innerHTML = `
        //     <div class="sender">${message.sender}</div>
        //     <div class="content">${message.message_html || message.message_text}</div>
        //     <div class="timestamp">${new Date(message.timestamp).toLocaleString()}</div>
        // `;
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 
            message.sender === 'user' ? 'user' : 'model');
        
        messageElement.innerHTML = `
            <div class="role_box">
                ${message.sender === 'user' ? message.message_text : message.message_html}
            </div>`;
        return messageElement;
    }

    function showLoadingIndicator() {
        if (!loadingElement) {
            loadingElement = document.createElement('div');
            loadingElement.className = 'loading-indicator';
            loadingElement.innerHTML = `
                <div class="spinner"></div>
                <span>Loading messages...</span>
            `;
            showMessage.insertBefore(loadingElement, showMessage.firstChild);
        }
    }

    function hideLoadingIndicator() {
        if (loadingElement && loadingElement.parentNode) {
            loadingElement.parentNode.removeChild(loadingElement);
            loadingElement = null;
        }
    }

    function showErrorIndicator() {
        hideLoadingIndicator();
        const errorElement = document.createElement('div');
        errorElement.className = 'error-indicator';
        errorElement.textContent = 'Failed to load messages. Please try again.';
        showMessage.insertBefore(errorElement, showMessage.firstChild);
        // Optional: Remove error message after some time
        setTimeout(() => {
            if (errorElement.parentNode) {
                errorElement.parentNode.removeChild(errorElement);
            }
        }, 3000);
    }
});

// First Create conversation (ID)
async function createConversationDB_id() {
    try {
        const response = await fetch('/api/conversations/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            console.log("Conversation:", data);
            // return data.conversation_id;
            return data.id;
        }
        throw new Error('Failed to create conversation ID');
        
    } catch (error) {
        console.error('Error creating conversation ID:', error);
        return null;
    }
}

async function updateConversationTitle(conversationId, newPrompt) {
    try {
        console.log('Sending request:', { conversationId, newPrompt });
        const response = await fetch('/api/conversations/update_title', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation_id: conversationId, // UUID or DB ID
                userPrompt: newPrompt
            }),
            credentials: 'include' // Add this if using sessions
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("datatsss", data)

        if (data.status === 'success') {
            console.log(`Conversation title set to: ${data.title}`);
            // document.getElementById("titleResult").innerHTML = `<h2>${data.title}</h2>`;
            const addNewChatFromLayout = document.getElementById('addNewChat');
            addNewChatFromLayout.innerHTML = `
                <div class="pb-2">New chat</div>
                <div class="conversation-item">
                    <a href="/chat/${data.id}">${data.title}</a>
                </div>
            `;
            // return {
            //     conversationId: data.id,
            //     title: data.title
            // };
        }

    } catch (error) {
        console.error('Error updating conversation title:', error);
        return null; // Or throw the error if preferred
    }
}

// Save data to database
async function sendMessageDB(senderRole, fullResponseText, renderContent) {

    // If conversationId is empty or not found, create a new one
    if (!conversationId || conversationId === '') {
        conversationId = await createConversationDB_id();
        if (!conversationId) {
            console.error('Failed to create conversation ID');
            return false;
        }
        // Optionally update URL with new conversation ID
        window.history.pushState({}, '', `/chat/${conversationId}`);
    }

    const messageData = {
        conversionID: conversationId,
        sender: senderRole,
        fullResponseText: fullResponseText,
        renderContent: renderContent
    };

    try {
        const response = await fetch('/api/messages/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chat_history: [messageData]
            })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            return true;
        }
        throw new Error('Server error');
    } catch (error) {
        console.error('Error saving message:', error);
        elements.userPrompt.disabled = true;
        return false;
    }
}

/*
* Title: Chat Behavior
* Description: 
* Use: 
* 
*/

// Modified scrollToBottomByStream function
function scrollToBottomByStream() {
    if (isAutoScroll) { 
        elements.chatMessage.scrollTo({
            top: elements.chatMessage.scrollHeight,
            behavior: 'smooth'
        });
    }
}

// Modified scrollToBottomManually function
function scrollToBottomManually() {
    elements.chatMessage.scrollTo({
        top: elements.chatMessage.scrollHeight,
        behavior: 'smooth'
    });
}


function adjustUserPromptHeight() {
    const textarea = elements.userPrompt;
    let maxHeight = 200; // Set any value you want
    textarea.style.height = "25px";
    textarea.style.height = `${Math.min(textarea.scrollHeight + 10, maxHeight)}px`;
}

/*
* Title: DOMContentLoaded
* Description: 
* Use: 
* 
*/

document.addEventListener("DOMContentLoaded", async () => {

    adjustUserPromptHeight();
    
    // if (conversationId) {
    //     getMessageByCoversatonId(conversationId);
    // }

    // Initially disable toggleButton if textarea is empty and not streaming
    elements.toggleButton.disabled = !elements.userPrompt.value.trim() && !isStreaming;

    // Add input event listener to enable/disable toggleButton based on textarea content and streaming state
    elements.userPrompt.addEventListener("input", () => {
        elements.toggleButton.disabled = !elements.userPrompt.value.trim() && !isStreaming; // Only disable if empty and not streaming
        adjustUserPromptHeight();
    });

    elements.userPrompt.addEventListener("input", adjustUserPromptHeight);
    elements.userPrompt.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey && !isStreaming) {
            e.preventDefault();
            toggleChat();
        }
    });
    elements.chatInput.addEventListener("click", () => elements.userPrompt.focus());

    elements.chatMessage.addEventListener("scroll", () => {
        const chat = elements.chatMessage;
        const distanceFromBottom = chat.scrollHeight - chat.scrollTop - chat.clientHeight;

        // is at Bottom from 10px
        if (distanceFromBottom < 10) {
            isAutoScroll = true; // Disable auto-scroll when user scrolls up
        } else {
            isAutoScroll = false;
        }

        // is at Bottom from 200px
        if (distanceFromBottom < 200) {
            elements.scrollToBottomBtn.style.display = "none";
        } else {
            elements.scrollToBottomBtn.style.display = "inline-flex";
        }
    });

});