function toggleChat() {
  const chatbox = document.getElementById("chatbox");
  const messages = document.getElementById("messages");

  if (chatbox.style.display === "block" || chatbox.style.display === "flex") {
    chatbox.style.display = "none";
    chatbox.classList.remove("maximized"); // Kapattığında büyütme modunu iptal et
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
  messages.innerHTML += `<div class="chat-message user">${msg}</div>`;
  input.value = "";

  const typingDiv = document.createElement("div");
  typingDiv.classList.add("chat-message", "bot");
  typingDiv.innerHTML = `<span class="typing-dots">Yazıyor<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></span>`;
  messages.appendChild(typingDiv);
  messages.scrollTop = messages.scrollHeight;

  fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question: msg }),
  })
    .then((res) => res.json())
    .then((data) => {
      typingDiv.innerHTML = "";
      let i = 0;
      const text = data.answer;
      const typingInterval = setInterval(() => {
        if (i < text.length) {
          typingDiv.innerHTML += text.charAt(i);
          i++;
          messages.scrollTop = messages.scrollHeight;
        } else {
          clearInterval(typingInterval);
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
      }
    }, 30);
  }, 700);
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
  if (chatbox) {
    chatbox.style.display = "none";
  }
  if (bubble) {
    bubble.classList.add("show-bubble");
    setTimeout(() => {
      bubble.classList.remove("show-bubble");
    }, 6000);
  }
});

setInterval(() => {
  if (bubble) {
    bubble.classList.add("show-bubble");
    setTimeout(() => {
      bubble.classList.remove("show-bubble");
    }, 6000);
  }
}, 12000);

const toggleButton = document.querySelector(".chatbot-toggle");
toggleButton.addEventListener("mouseenter", () => {
  if (bubble) {
    bubble.classList.add("show-bubble");
    setTimeout(() => {
      bubble.classList.remove("show-bubble");
    }, 6000);
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

  if (chatbox.classList.contains("maximized")) {
    icon.textContent = "❐";
  } else {
    icon.textContent = "🗖";
  }
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
