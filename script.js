document.addEventListener("DOMContentLoaded", () => {
let conversations = [];      // Mảng chứa conv cũ
let currentConversation = null;

const sidebar = document.getElementById('sidebar');
const newChatBtn = document.querySelector('.new-chat-btn');
const mainContent = document.getElementById('mainContent');
const contentInner = document.getElementById('contentInner');
const chatInputContainer = document.querySelector(".chat-input-container");
const conversationContainer = document.getElementById("conversationContainer");
const heroSection = document.getElementById("heroSection");
const searchInput = document.querySelector(".search-input");
const searchBtn = document.querySelector(".search-btn");
const chatInput = document.querySelector(".chat-input");
const chatSendBtn = document.querySelector(".chat-send-btn");

const API_URL = "http://localhost:8000/generate_response";

function scrollToBottom() {
    conversationContainer.scrollTop = conversationContainer.scrollHeight;
}
// Toggle sidebar
window.toggleSidebar = function() {
    if (sidebar.classList.contains('open')) {
    sidebar.classList.remove('open');
    mainContent.classList.remove('open');
    contentInner.classList.remove('open');
    if (chatInputContainer) {
        chatInputContainer.classList.remove('open');
        chatInputContainer.classList.add('close');
    }
    sidebar.classList.add('close');
    mainContent.classList.add('close');
    contentInner.classList.add('close');
    } else {
    sidebar.classList.remove('close');
    mainContent.classList.remove('close');
    contentInner.classList.remove('close');
    if (chatInputContainer) {
        chatInputContainer.classList.remove('close');
        chatInputContainer.classList.add('open');
    }
    sidebar.classList.add('open');
    mainContent.classList.add('open');
    contentInner.classList.add('open');
    }
};

// Auto resize textarea
chatInput.addEventListener("input", function() {
    this.style.height = 'auto';
    this.style.height = this.scrollHeight + 'px';
});

// Cập nhật sidebar
function updateSidebar() {
    const chatHistory = document.querySelector(".chat-history");
    chatHistory.innerHTML = "";
    const allConversations = [...conversations];
    if (currentConversation) allConversations.push(currentConversation);

    allConversations.forEach(conv => {
    const item = document.createElement("div");
    item.className = "chat-item";
    item.textContent = conv.title;
    item.addEventListener("click", () => {
        // Chỉ load nếu conv !== currentConversation
        if (conv !== currentConversation) {
        loadConversation(conv);
        }
    });
    chatHistory.appendChild(item);
    });
}

// Tạo cuộc trò chuyện mới
newChatBtn.addEventListener("click", () => {
    if (currentConversation) {
    conversations.push(currentConversation);
    }
    currentConversation = null;
    conversationContainer.innerHTML = "";
    updateSidebar();
    heroSection.style.display = "block";
    conversationContainer.style.display = "none";
    chatInputContainer.style.display = "none";
});

// loadConversation: vẽ các tin đã có trong conv (server-side)
function loadConversation(conv) {
    currentConversation = conv;
    conversationContainer.innerHTML = "";
    // Vẽ lại tin cũ
    conv.messages.forEach(msgObj => {
    addMessage(msgObj.content, msgObj.role, false); 
    });
    heroSection.style.display = "none";
    conversationContainer.style.display = "block";
    chatInputContainer.style.display = "flex";
    scrollToBottom();
}

// addMessage: vẽ 1 tin nhắn
function addMessage(content, sender, save = true) {
    const msg = document.createElement("div");
    msg.className = "message " + (sender === "user" ? "user-message" : "bot-message");
    if (sender === "user") {
    msg.textContent = "Bạn: " + content;
    } else {
    msg.innerHTML = marked.parse(content);
    }
    conversationContainer.appendChild(msg);
    conversationContainer.scrollTop = conversationContainer.scrollHeight;

    // Nếu save = true => push vào conv
    if (save && currentConversation) {
    currentConversation.messages.push({ role: sender, content: content });
    }
    scrollToBottom();
}

// fetchBotResponse: chỉ tin cậy data.chat_history
async function fetchBotResponse(userQuery) {
    // Tạo loading
    const loadingMsg = document.createElement("div");
    loadingMsg.className = "message bot-message loading-blink";
    loadingMsg.textContent = "Extracting Data";
    conversationContainer.appendChild(loadingMsg);
    conversationContainer.scrollTop = conversationContainer.scrollHeight;

    // client: KHÔNG lưu user => server gộp
    // => client HISTORY cũ => do server đã build

    try {
    const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        user_query: userQuery,
        // Gửi chat_history cũ => nếu server cần
        chat_history: currentConversation ? currentConversation.messages : []
        })
    });
    const data = await response.json();
    loadingMsg.classList.remove("loading-blink");
    loadingMsg.remove();

    if (data.chat_history) {
        // CHỈ TIN CẬY SERVER => gán hẳn
        currentConversation.messages = data.chat_history;
        // Xoá khung, vẽ full
        conversationContainer.innerHTML = "";
        loadConversation(currentConversation);
    } else if (data.response) {
        // Nếu server CHỈ trả về 1 tin => ta cần push
        // (Nếu server ko build chat_history, ta vẽ tạm)
        // addMessage(data.response, "bot", false); // tuỳ
        // Ko an toàn => tuỳ logic server
    } else {
        addMessage("Bot: Xin lỗi, không có phản hồi", "bot", false);
    }
    } catch (error) {
    addMessage("Bot: Lỗi kết nối đến server!", "bot", false);
    }
}

// handleHeroQuestion: user gửi tin => KHÔNG lưu cục bộ
function handleHeroQuestion() {
    const question = searchInput.value.trim();
    if (!question) return;

    if (!currentConversation) {
    currentConversation = {
        id: Date.now(),
        title: "Cuộc trò chuyện " + (conversations.length + 1),
        messages: []
    };
    updateSidebar();
    }
    // Ẩn hero, hiển thị
    heroSection.style.display = "none";
    conversationContainer.style.display = "block";
    chatInputContainer.style.display = "flex";

    if (sidebar.classList.contains('open')) {
    chatInputContainer.classList.remove('close');
    chatInputContainer.classList.add('open');
    } else {
    chatInputContainer.classList.remove('open');
    chatInputContainer.classList.add('close');
    }

    // Vẽ user tạm => save=false => ko ghi conv
    addMessage(question, "user", false);

    // Gọi API => server build chat_history
    fetchBotResponse(question);

    // reset
    searchInput.value = "";
}
searchBtn.addEventListener("click", handleHeroQuestion);
// chặn double enter + click
searchInput.addEventListener("keyup", (e) => {
    if (e.key === "Enter") {
    e.preventDefault();
    handleHeroQuestion();
    }
});

// handleChatInput => same logic
function handleChatInput() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Vẽ user tạm => false => server tin cậy
    addMessage(message, "user", false);

    // server build => return chat_history
    fetchBotResponse(message);

    chatInput.value = "";
    chatInput.style.height = "40px";
}
if (chatInput && chatSendBtn) {
    chatSendBtn.addEventListener("click", handleChatInput);
    chatInput.addEventListener("keyup", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        handleChatInput();
    }
    });
}
scrollToBottom();
});