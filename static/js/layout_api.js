/* 
 * For: Show data when user Login
 * Function: fetchAuthData,
 *
 */
    // Fetch logo_html from Flask API

// function getLogoAndCssFromSystemSettings() {
//     fetch("/admin/api/system_settings/get_logoAndCSS")
//         .then(response => response.json())
//         .then(data => {
//             if (data.logo_html) {
//                 document.querySelectorAll(".appLogo").forEach(element => {
//                     element.innerHTML = data.logo_html;
//                 });
//             }
//             if (data.custom_css) {
//                 const styleElement = document.createElement("style");
//                 styleElement.textContent = data.custom_css;
//                 document.head.appendChild(styleElement);
//             }
//         })
//         .catch(error => console.error("Error fetching settings:", error));
// }

// document.addEventListener("DOMContentLoaded", getLogoAndCssFromSystemSettings);
 
      
    
/* 
 * For: Show data when user Login
 * Function: fetchAuthData,
 *
 */

// USER DATA
function fetchAuthData() {
    fetch('/api/auth', {
        method: 'GET',
        credentials: 'include'  // Include cookies for session authentication
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // console.log("Auth data:", data);
        if (data.status === 'success') {
            displayUserData(data.user);
        } else {
            displayError(data.message || 'Failed to load user data');
        }
    })
    .catch(error => {
        // console.error('Error fetching user data:', error);
        displayError('Error loading user data. Please try again.');
    });
}

function displayUserData(user) {
    const userInfoDiv = document.getElementById('userInfo');
    const roleAllowedDiv = document.getElementById('roleAllowed');
    const userLimitDiv = document.getElementById('userLimit');
    // 
    const currentUserName = document.getElementById('currentUserName');
    
    // Clear initial loading message
    userInfoDiv.innerHTML = '';
    roleAllowedDiv.innerHTML = '';
    userLimitDiv.innerHTML ='';
    currentUserName.innerHTML ='';

    // Display data
    userLimitDiv.innerHTML = `
    <span id="userMessageLimit">${user.message_limit}</span>
    /${user.max_messages_today}
     <span style="font-size: 0.8em;">Credits</span>`;

    currentUserName.innerHTML = `<h5>${user.displayName}</h5>`;
    
    // Handle picture display
    if (user.picture && user.picture !== 'none' && user.picture !== '') {
        // console.log("User picture:", user.picture)
        // Create img element dynamically
        const userPictureImg = document.createElement('img');
        userPictureImg.src = user.picture;
        userPictureImg.alt = 'Profile';
        userPictureImg.style.width="100%";
        userInfoDiv.appendChild(userPictureImg);
    } else {
        // Show first 2 letters of username if no picture
        const initials = user.username.substring(0, 2).toUpperCase();
        userInfoDiv.innerHTML = `<span class="no-picture">${initials}</span>`;
    }

    if (user.role === 1 || user.role === 2) {

        // Add the element after roleAllowedDiv
        const adminLink = document.createElement('a');
        adminLink.href = "/admin/system_settings";
        adminLink.className = "dropdown-menu-profile";
        adminLink.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-gear me-2" viewBox="0 0 16 16">
                <path d="M11 5a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM8 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm.256 7a4.474 4.474 0 0 1-.229-1.004H3c.001-.246.154-.986.832-1.664C4.484 10.68 5.711 10 8 10c.26 0 .507.009.74.025.226-.341.496-.65.804-.918C9.077 9.038 8.564 9 8 9c-5 0-6 3-6 4s1 1 1 1h5.256Z"/>
                <path d="M12.5 16a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm-.646-4.854.646.647.646-.647a.5.5 0 0 1 .708.708l-.647.646.647.646a.5.5 0 0 1-.708.708l-.646-.647-.646.647a.5.5 0 0 1-.708-.708l.647-.646-.647-.646a.5.5 0 0 1 .708-.708Z"/>
            </svg>
            Admin
        `;
        roleAllowedDiv.after(adminLink);
    } 
}

function displayError(message) {
    const userInfoDiv = document.getElementById('user-info');
    userInfoDiv.innerHTML = `<p class="error">${message}</p>`;
}


// Call the function when the page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchAuthData();
    // fetchUserConversations();
});


// Assuming you have a frontend script file
document.addEventListener('DOMContentLoaded', () => {
    const sideBarScroll = document.getElementById('sideBarScroll')
    const chatHistory = document.getElementById('chatHistory');
    let page = 1; // Track pagination
    let isLoading = false; // Prevent multiple simultaneous requests
    let hasMore = true; // Track if there's more data to load

    // Create loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = `
        <div class="spinner"></div>
        <span>Loading...</span>
    `;
    loadingIndicator.style.display = 'none'; // Hidden by default
    chatHistory.insertAdjacentElement('afterend',loadingIndicator);

    // Function to fetch conversations
    async function fetchConversations() {
        if (isLoading || !hasMore) return;

        isLoading = true;
        loadingIndicator.style.display = 'flex'; // Show loading indicator
        try {
            const response = await fetch(`/api/conversations/pagination?page=${page}`, {
                headers: {
                    'Content-Type': 'application/json',
                    // Include any authentication headers if needed
                }
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                // console.log("Conversation",data.conversations);
                // Append conversations to the div
                displayConversations(data.conversations);

                // Check if there's more data
                hasMore = data.conversations.length > 0;
                page++;
            }
        } catch (error) {
            console.error('Error fetching conversations:', error);
        } finally {
            isLoading = false;
            loadingIndicator.style.display = 'none'; // Hide loading indicator
        }
    }

    // dispaly conversations
    function displayConversations(conversations) {
        const chatHistory = document.getElementById('chatHistory');
        
        if (conversations.length === 0) {
            // convoElement.innerHTML = '<p>No conversations found.</p>';
            return;
        }
        // Funtion to show normall content
        // conversations.forEach(convo => {
        //     const convoElement = document.createElement('div');
        //     convoElement.className = 'conversation-item';
        //     convoElement.innerHTML = `
        //         <a href="/chat/${convo.id}">${convo.title}</a>
        //     `;
        //     // <p>Created: ${new Date(convo.created_at).toLocaleString()}</p>
        //     // <p>Last Updated: ${new Date(convo.updated_at).toLocaleString()}</p>
        //     // <a href="{{ url_for('gemini_routes.user_new_chat', conversation_id=${convo.id}) }}"">${convo.title}</a>
        //     chatHistory.appendChild(convoElement);
        // });

        // Helper function to get relative time
        function getTimeDifference(date) {
            const now = new Date();
            const chatDate = new Date(date);
            const diffMs = now - chatDate;
            const diffSec = Math.floor(diffMs / 1000);
            const diffMin = Math.floor(diffSec / 60);
            const diffHr = Math.floor(diffMin / 60);
            const diffDays = Math.floor(diffHr / 24);

            if (diffMin < 60) return `${diffMin}m ago`;
            if (diffHr < 24) return `${diffHr}h ago`;
            if (diffDays === 1) return 'Yesterday';
            return `${diffDays}d ago`;
        }

        // Group conversations by time period
        function groupConversations() {
            const now = new Date();
            const today = [];
            const yesterday = [];
            const last7Days = [];
            const lastMonth = [];
            const oldChats = [];

            conversations.forEach(convo => {
                const chatDate = new Date(convo.created_at);
                const diffMs = now - chatDate;
                const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

                const chatItem = {
                    id: convo.id,
                    title: convo.title,
                    time: getTimeDifference(convo.created_at)
                };

                if (diffDays === 0) {
                    today.push(chatItem);
                } else if (diffDays === 1) {
                    yesterday.push(chatItem);
                } else if (diffDays <= 7) {
                    last7Days.push(chatItem);
                } else if (diffDays <= 30) {
                    lastMonth.push(chatItem);
                } else {
                    oldChats.push(chatItem); 
                }
            });

            return { today, yesterday, last7Days, lastMonth, oldChats };
        }

        // Render grouped conversations
        const groupedChats = groupConversations();
        const sections = [
            { title: 'Today', chats: groupedChats.today },
            { title: 'Yesterday', chats: groupedChats.yesterday },
            { title: 'Last 7 Days', chats: groupedChats.last7Days },
            { title: 'Last Month', chats: groupedChats.lastMonth },
            { title: 'Old Chats', chats: groupedChats.oldChats }
        ];

        chatHistory.innerHTML = ''; // Clear existing content

        sections.forEach(section => {
            if (section.chats.length > 0) {
                // Create section header
                const sectionElement = document.createElement('div');
                sectionElement.className = 'conversation-section';
                
                const heading = document.createElement('div');
                heading.classList.add('mb-1', 'mt-4')
                heading.textContent = section.title;
                sectionElement.appendChild(heading);

                // Add conversation items
                section.chats.forEach(convo => {
                    const convoElement = document.createElement('div');
                    convoElement.className = 'conversation-item';
                    // convoElement.innerHTML = `
                    //     <a href="/chat/${convo.id}">${convo.title}</a>
                    //     <span style="color: #666; margin-left: 10px;">(${convo.time})</span>
                    // `;
                    convoElement.innerHTML = `
                        <a href="/chat/${convo.id}">${convo.title}</a>
                    `;
                    sectionElement.appendChild(convoElement);
                });

                chatHistory.appendChild(sectionElement);
            }
        });
    }

    // Scroll event listener
    sideBarScroll.addEventListener('scroll', () => {
        // Check if user has scrolled to the bottom
        const { scrollTop, scrollHeight, clientHeight } = sideBarScroll;
        
        if (scrollTop + clientHeight >= scrollHeight - 50) { // 50px threshold
            fetchConversations();
        }
    });

    // Initial load
    fetchConversations();
});

// 
document.querySelectorAll('.conversation-item').forEach(item => {
    item.addEventListener('click', function() {
        // Remove focus class from all items
        document.querySelectorAll('.conversation-item').forEach(el => el.classList.remove('focused'));
        // Add focus class to the clicked item
        this.classList.add('focused');
    });
});





// Fetch data from API when page loads
function fetchMessageLimit() {
    fetch('/api/message_limit')
        .then(response => response.json())
        .then(data => {
            let remainingSeconds = data.remaining_seconds;
            document.getElementById('message_count').textContent = data.message_count;

            function updateCountdown() {
                if (remainingSeconds <= 0) {
                    document.getElementById('countdownMessageLimit').innerHTML = "Message limit has been reset!";
                    setTimeout(() => location.reload(), 1000);
                    return;
                }

                const hours = Math.floor(remainingSeconds / 3600);
                const minutes = Math.floor((remainingSeconds % 3600) / 60);
                const seconds = Math.floor(remainingSeconds % 60);

                document.getElementById('countdownMessageLimit').innerHTML = 
                    `Messages reset in: ${hours}h ${minutes}m ${seconds}s`;

                if (document.getElementById('countdownSend')) {
                    
                    document.getElementById('countdownSend').innerHTML = 
                        `Your message will be reset in: ${hours}h ${minutes}m ${seconds}s`;
                }
                
                remainingSeconds--;
                setTimeout(updateCountdown, 1000);
            }

            if (remainingSeconds > 0) {
                updateCountdown();
            } else {
                // document.getElementById('countdownMessageLimit').innerHTML = "Message limit has been reset!";
                document.getElementById('countdownMessageLimit').innerHTML = "Free to use!";
            }
        })
        .catch(error => {
            console.error('Error fetching message limit:', error);
            document.getElementById('message_count').textContent = 'Error';
            document.getElementById('countdownMessageLimit').innerHTML = 'Error loading countdown';
        });
}

window.addEventListener("load", fetchMessageLimit);