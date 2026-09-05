const API_URL = "/query";
const LOGO_URL = "/static/images/readflix-logo.png";

const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const sendIcon = document.getElementById("sendIcon");
const sendLoader = document.getElementById("sendLoader");
const typingIndicator = document.getElementById("typingIndicator");
const newChatBtn = document.getElementById("newChatBtn");

let activeRequestController = null;
let activeRequestId = 0;

let threadId = sessionStorage.getItem(
    "readflix_thread_id"
);

if (!threadId) {
    threadId = crypto.randomUUID();

    sessionStorage.setItem(
        "readflix_thread_id",
        threadId
    );
}

/* =========================================================
   SEND MESSAGE
   ========================================================= */

async function sendMessage() {
    const question =
        messageInput.value.trim();

    if (!question || sendBtn.disabled) {
        return;
    }

    const requestThreadId = threadId;

    const requestId =
        ++activeRequestId;

    const controller =
        new AbortController();

    activeRequestController =
        controller;

    const currentEmptyState =
        document.getElementById(
            "emptyState"
        );

    if (currentEmptyState) {
        currentEmptyState.remove();
    }

    addMessage(
        "user",
        question
    );

    messageInput.value = "";

    autoResizeTextarea();

    setLoading(true);

    try {
        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    q: question,
                    thread_id:
                        requestThreadId,
                }),

                signal:
                    controller.signal,
            }
        );

        let data = {};

        try {
            data = await response.json();
        } catch {
            data = {};
        }

        if (response.status === 429) {
            throw new Error(
                "RATE_LIMIT"
            );
        }

        if (!response.ok) {
            throw new Error(
                data.detail ||
                `HTTP ${response.status}`
            );
        }

        /*
         * Ignore the response if the user
         * already started a new conversation.
         */
        if (
            requestId !==
            activeRequestId
        ) {
            return;
        }

        const answer =
            data.answer ||
            "I couldn't generate an answer.";

        addMessage(
            "assistant",
            answer
        );

    } catch (error) {

        if (
            error.name ===
            "AbortError"
        ) {
            return;
        }

        /*
         * Ignore errors belonging to
         * an old conversation.
         */
        if (
            requestId !==
            activeRequestId
        ) {
            return;
        }

        console.error(
            "Request failed:",
            error
        );

        const message =
            error.message ===
            "RATE_LIMIT"
                ? "You're sending messages too quickly. Please try again in a moment."
                : "I can't answer right now. Please try again.";

        addMessage(
            "assistant",
            message
        );

    } finally {

        /*
         * Only the currently active request
         * is allowed to change loading state.
         */
        if (
            requestId ===
            activeRequestId
        ) {
            activeRequestController =
                null;

            setLoading(false);
        }
    }
}

/* =========================================================
   ADD MESSAGE
   ========================================================= */

function addMessage(
    role,
    content
) {
    const message =
        document.createElement("div");

    message.className =
        `message ${role}`;

    const avatar =
        document.createElement("div");

    avatar.className =
        `message-avatar ${
            role === "user"
                ? "user-avatar"
                : "assistant-avatar"
        }`;

    if (role === "user") {

        avatar.textContent =
            "You";

    } else {

        const logo =
            document.createElement("img");

        logo.src = LOGO_URL;

        logo.alt =
            "READFLIX Assistant";

        logo.className =
            "message-avatar-image";

        avatar.appendChild(
            logo
        );
    }

    const wrapper =
        document.createElement("div");

    wrapper.className =
        "message-content-wrapper";

    const contentElement =
        document.createElement("div");

    contentElement.className =
        "message-content";

    if (role === "assistant") {

        if (
            typeof marked !==
            "undefined"
        ) {

            const rendered =
                marked.parse(
                    content
                );

            if (
                typeof DOMPurify !==
                "undefined"
            ) {

                contentElement.innerHTML =
                    DOMPurify.sanitize(
                        rendered
                    );

            } else {

                contentElement.textContent =
                    content;
            }

        } else {

            contentElement.textContent =
                content;
        }

    } else {

        contentElement.textContent =
            content;
    }

    wrapper.appendChild(
        contentElement
    );

    if (
        role === "assistant"
    ) {
        wrapper.appendChild(
            createMessageActions(
                content
            )
        );
    }

    message.appendChild(
        avatar
    );

    message.appendChild(
        wrapper
    );

    chatMessages.appendChild(
        message
    );

    scrollToBottom();
}

/* =========================================================
   MESSAGE ACTIONS
   ========================================================= */

function createMessageActions(
    content
) {
    const actions =
        document.createElement("div");

    actions.className =
        "message-actions";

    const copyBtn =
        document.createElement(
            "button"
        );

    copyBtn.className =
        "action-btn";

    copyBtn.type = "button";

    copyBtn.textContent =
        "Copy";

    copyBtn.addEventListener(
        "click",
        async () => {
            try {

                await navigator.clipboard.writeText(
                    content
                );

                copyBtn.textContent =
                    "Copied";

                setTimeout(() => {
                    copyBtn.textContent =
                        "Copy";
                }, 1500);

            } catch (error) {

                console.error(
                    "Copy failed:",
                    error
                );
            }
        }
    );

    actions.appendChild(
        copyBtn
    );

    return actions;
}

/* =========================================================
   LOADING
   ========================================================= */

function setLoading(
    loading
) {
    sendBtn.disabled =
        loading;

    typingIndicator.classList.toggle(
        "hidden",
        !loading
    );

    sendIcon.classList.toggle(
        "hidden",
        loading
    );

    sendLoader.classList.toggle(
        "hidden",
        !loading
    );

    if (loading) {
        scrollToBottom();
    }
}

/* =========================================================
   SCROLL
   ========================================================= */

function scrollToBottom() {
    if (!chatMessages) {
        return;
    }

    requestAnimationFrame(() => {

        chatMessages.scrollTop =
            chatMessages.scrollHeight;

    });
}

/* =========================================================
   TEXTAREA
   ========================================================= */

function autoResizeTextarea() {

    messageInput.style.height =
        "auto";

    const maxHeight =
        window.innerWidth <= 760
            ? 120
            : 140;

    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            maxHeight
        ) + "px";
}

function resetInput() {

    messageInput.value = "";

    autoResizeTextarea();

    messageInput.focus();
}

/* =========================================================
   KEYBOARD
   ========================================================= */

messageInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);

messageInput.addEventListener(
    "input",
    autoResizeTextarea
);

/* =========================================================
   SEND BUTTON
   ========================================================= */

sendBtn.addEventListener(
    "click",
    sendMessage
);

/* =========================================================
   QUICK PROMPTS
   ========================================================= */

function bindQuickPrompts() {

    document
        .querySelectorAll(
            ".quick-prompts button"
        )
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    messageInput.value =
                        button.dataset.prompt;

                    autoResizeTextarea();

                    messageInput.focus();
                }
            );
        });
}

bindQuickPrompts();

/* =========================================================
   NEW CHAT
   ========================================================= */

newChatBtn.addEventListener(
    "click",
    async () => {

        /*
         * Save the old thread before creating a new one.
         */
        const oldThreadId = threadId;

        /*
         * Invalidate every previous request.
         */
        activeRequestId++;

        /*
         * Cancel the currently running request.
         */
        if (activeRequestController) {
            activeRequestController.abort();
            activeRequestController = null;
        }

        /*
         * Delete old thread from backend memory.
         */
        try {
            await fetch(
                `${API_URL.replace("/query", "")}/thread/${encodeURIComponent(oldThreadId)}`,
                {
                    method: "DELETE",
                }
            );
        } catch (error) {
            console.error(
                "Thread deletion failed:",
                error
            );
        }

        /*
         * Generate a completely new thread.
         */
        threadId = crypto.randomUUID();

        sessionStorage.setItem(
            "readflix_thread_id",
            threadId
        );

        /*
         * Reset UI.
         */
        chatMessages.innerHTML = `
            <div
                id="emptyState"
                class="empty-state"
            >
                <div class="empty-icon">
                    <img
                        src="${LOGO_URL}"
                        alt=""
                    >
                </div>

                <h2>
                    How can I help you?
                </h2>

                <p>
                    Ask me anything about
                    READFLIX Library.
                </p>

                <div class="quick-prompts">

                    <button
                        type="button"
                        data-prompt="How many seats are available in the library?"
                    >
                        How many seats are available?
                    </button>

                    <button
                        type="button"
                        data-prompt="What are the library opening hours?"
                    >
                        What are the opening hours?
                    </button>

                    <button
                        type="button"
                        data-prompt="Can I borrow books from the library?"
                    >
                        Can I borrow books?
                    </button>

                    <button
                        type="button"
                        data-prompt="Is Wi-Fi available in the library?"
                    >
                        Is Wi-Fi available?
                    </button>

                </div>
            </div>
        `;

        bindQuickPrompts();

        setLoading(false);
        resetInput();
        chatMessages.scrollTop = 0;
    }
);


window.addEventListener(
    "resize",
    autoResizeTextarea
);

window.addEventListener(
    "orientationchange",
    () => {

        setTimeout(
            autoResizeTextarea,
            100
        );

    }
);
window.addEventListener("pagehide", () => {
    if (!threadId) {
        return;
    }

    fetch(
        `${API_URL.replace("/query", "")}/thread/${encodeURIComponent(threadId)}`,
        {
            method: "DELETE",
            keepalive: true,
        }
    ).catch(() => {});

    sessionStorage.removeItem("readflix_thread_id");
});

/* =========================================================
   INITIALIZE
   ========================================================= */

autoResizeTextarea();