let sessionId = null;
let currentFeedbackId = null;

function toggleChat() {
  const chatbox = document.getElementById("chatbox");
  const messages = document.getElementById("messages");

  if (chatbox.style.display === "block" || chatbox.style.display === "flex") {
    chatbox.style.display = "none";
    chatbox.classList.remove("maximized");
  } else {
    chatbox.style.display = "flex";

    if (!messages.innerHTML.includes("Piri Reis ChatBot")) {
      showTypingEffect(
        "Merhaba, ben Piri Reis ChatBot! Size nasıl yardımcı olabilirim? ⚓"
      );
    }
  }
}

function sendMessage() {
  const input = document.getElementById("user-input");
  const msg = input.value.trim();
  if (!msg) return;

  const messages = document.getElementById("messages");

  const userMessage = document.createElement("div");
  userMessage.classList.add("chat-message", "user");
  userMessage.textContent = msg;
  messages.appendChild(userMessage);
  input.value = "";

  const typingDiv = document.createElement("div");
  typingDiv.classList.add("chat-message", "bot");
  typingDiv.innerHTML = `<span class="typing-dots">Yazıyor<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span>`;
  messages.appendChild(typingDiv);
  messages.scrollTop = messages.scrollHeight;

  fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: msg }),
  })
    .then((res) => res.json())
    .then((data) => {
      typingDiv.innerHTML = "";
      let i = 0;
      const text = data.answer;

      if (!sessionId && data.conversation_id) {
        sessionId = data.conversation_id;
      }

      // Debug için console log ekleyelim
      console.log("Received data:", data);
      console.log("Feedback ID:", data.feedback_id);

      const typingInterval = setInterval(() => {
        if (i < text.length) {
          typingDiv.innerHTML += text.charAt(i);
          i++;
          messages.scrollTop = messages.scrollHeight;
        } else {
          clearInterval(typingInterval);
          // feedback_id'yi butonlara ekle
          addFeedbackButtons(typingDiv, data.feedback_id);
        }
      }, 30);
    })
    .catch((err) => {
      typingDiv.innerHTML = "Bir hata oluştu. Lütfen tekrar deneyin.";
      console.error("Hata:", err);
    });
}

function showTypingEffect(text) {
  const messages = document.getElementById("messages");

  const typingDiv = document.createElement("div");
  typingDiv.classList.add("chat-message", "bot");
  typingDiv.innerHTML = `<span class="typing-dots">Yazıyor<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span>`;
  messages.appendChild(typingDiv);
  messages.scrollTop = messages.scrollHeight;

  setTimeout(() => {
    typingDiv.innerHTML = "";
    let i = 0;
    const typingInterval = setInterval(() => {
      if (i < text.length) {
        typingDiv.innerHTML += text.charAt(i);
        i++;
        messages.scrollTop = messages.scrollHeight;
      } else {
        clearInterval(typingInterval);
        // Hoş geldin mesajında feedback_id yok, null geçiyoruz
        addFeedbackButtons(typingDiv, null);
      }
    }, 30);
  }, 700);
}

function addFeedbackButtons(elem, feedbackId) {
  console.log("Adding feedback buttons with ID:", feedbackId);
  
  const feedbackHTML = `
    <div class="feedback" data-feedback-id="${feedbackId || ''}">
      <button class="feedback-btn like-btn" aria-label="Beğendim" data-tooltip="Yanıtı beğendim">
        <i class="fa-regular fa-thumbs-up"></i>
      </button>
      <button class="feedback-btn dislike-btn" aria-label="Beğenmedim" data-tooltip="Yanıtı beğenmedim">
        <i class="fa-regular fa-thumbs-down"></i>
      </button>
    </div>
  `;

  elem.insertAdjacentHTML("beforeend", feedbackHTML);

  const feedbackContainer = elem.querySelector(".feedback");
  const likeBtn = elem.querySelector(".like-btn");
  const dislikeBtn = elem.querySelector(".dislike-btn");

  // Hoş geldin mesajı için butonları devre dışı bırak
  if (!feedbackId || feedbackId === null || feedbackId === 'null') {
    likeBtn.style.opacity = "0.5";
    dislikeBtn.style.opacity = "0.5";
    likeBtn.disabled = true;
    dislikeBtn.disabled = true;
    likeBtn.title = "Hoş geldin mesajı için feedback verilmez";
    dislikeBtn.title = "Hoş geldin mesajı için feedback verilmez";
    return;
  }

  likeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    console.log("Like button clicked for feedback ID:", feedbackId);
    sendFeedback(feedbackId, "like");
    
    // Buton durumlarını güncelle
    likeBtn.innerHTML = '<i class="fa-solid fa-thumbs-up"></i>';
    likeBtn.style.color = "#28a745";
    likeBtn.disabled = true;
    
    // Dislike butonunu resetle
    dislikeBtn.innerHTML = '<i class="fa-regular fa-thumbs-down"></i>';
    dislikeBtn.style.color = "";
    dislikeBtn.disabled = false;
    dislikeBtn.style.opacity = "1";
  });

  dislikeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    console.log("Dislike button clicked for feedback ID:", feedbackId);
    sendFeedback(feedbackId, "dislike");
    
    // Buton durumlarını güncelle
    dislikeBtn.innerHTML = '<i class="fa-solid fa-thumbs-down"></i>';
    dislikeBtn.style.color = "#dc3545";
    dislikeBtn.disabled = true;
    
    // Like butonunu resetle
    likeBtn.innerHTML = '<i class="fa-regular fa-thumbs-up"></i>';
    likeBtn.style.color = "";
    likeBtn.disabled = false;
    likeBtn.style.opacity = "1";
  });
}

function sendFeedback(feedbackId, feedbackType) {
  console.log("Sending feedback:", { feedbackId, feedbackType });
  
  if (!feedbackId) {
    console.log("Feedback ID bulunamadı");
    showNotification("Feedback ID bulunamadı!", "error");
    return;
  }

  fetch("/feedback", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      feedback_id: feedbackId,
      feedback_type: feedbackType,
    }),
  })
    .then((res) => {
      console.log("Feedback response status:", res.status);
      return res.json();
    })
    .then((data) => {
      console.log("Feedback response data:", data);
      if (data.success) {
        showNotification("Geri bildiriminiz kaydedildi. Teşekkürler!");
      } else {
        console.error("Feedback kaydedilirken hata:", data.error);
        showNotification("Feedback kaydedilirken hata oluştu: " + data.error, "error");
      }
    })
    .catch((err) => {
      console.error("Feedback gönderirken hata:", err);
      showNotification("Feedback gönderirken hata oluştu!", "error");
    });
}

function showNotification(message, type = "success") {
  const notification = document.createElement("div");
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === "error" ? "#dc3545" : "#28a745"};
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    z-index: 10000;
    font-size: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    animation: slideIn 0.3s ease;
  `;
  
  // Animasyon için CSS ekle
  if (!document.getElementById("notification-styles")) {
    const style = document.createElement("style");
    style.id = "notification-styles";
    style.textContent = `
      @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    `;
    document.head.appendChild(style);
  }
  
  document.body.appendChild(notification);
  setTimeout(() => {
    notification.remove();
  }, 3000);
}

document.addEventListener("DOMContentLoaded", function () {
  const userInput = document.getElementById("user-input");
  if (userInput) {
    userInput.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        sendMessage();
      }
    });
  }
});

const bubble = document.querySelector(".chat-bubble");

window.addEventListener("load", () => {
  const chatbox = document.getElementById("chatbox");
  if (chatbox) chatbox.style.display = "none";
  if (bubble) {
    bubble.classList.add("show-bubble");
    setTimeout(() => bubble.classList.remove("show-bubble"), 6000);
  }
});

setInterval(() => {
  if (bubble) {
    bubble.classList.add("show-bubble");
    setTimeout(() => bubble.classList.remove("show-bubble"), 6000);
  }
}, 12000);

const toggleButton = document.querySelector(".chatbot-toggle");
toggleButton.addEventListener("mouseenter", () => {
  if (bubble) {
    bubble.classList.add("show-bubble");
    setTimeout(() => bubble.classList.remove("show-bubble"), 6000);
  }
});

window.addEventListener("click", function (e) {
  const chatbox = document.getElementById("chatbox");
  const toggleBtn = document.querySelector(".chatbot-toggle");
  if (
    chatbox.style.display === "flex" &&
    !chatbox.contains(e.target) &&
    !toggleBtn.contains(e.target)
  ) {
    chatbox.style.display = "none";
    chatbox.classList.remove("maximized");
  }
});

function closeChatbox() {
  const chatbox = document.getElementById("chatbox");
  chatbox.style.display = "none";
  chatbox.classList.remove("maximized");
}

function toggleMaximize() {
  const chatbox = document.getElementById("chatbox");
  const icon = document.getElementById("maximize-icon");

  chatbox.classList.toggle("maximized");

  icon.textContent = chatbox.classList.contains("maximized") ? "❐" : "🗖";
}

let isDragging = false;
let startY = 0;

const resizeHandle = document.getElementById("resize-handle");
const chatbox = document.getElementById("chatbox");

if (resizeHandle) {
  resizeHandle.addEventListener("mousedown", (e) => {
    isDragging = true;
    startY = e.clientY;
  });

  window.addEventListener("mousemove", (e) => {
    if (isDragging) {
      const deltaY = startY - e.clientY;
      if (deltaY > 50) {
        chatbox.classList.add("expanded");
        isDragging = false;
      }
    }
  });

  window.addEventListener("mouseup", () => {
    isDragging = false;
  });
}