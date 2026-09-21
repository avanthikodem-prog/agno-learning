import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "../App.css";
import { sendChatMessage } from "../services/api";

function Chat() {
  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      sender: "assistant",
      text: "Hello! 👋 How can I help you with your farming question today?",
    },
  ]);

  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    const userMessage = {
      sender: "user",
      text: trimmedMessage,
    };

    setMessages((previousMessages) => [
      ...previousMessages,
      userMessage,
    ]);

    setMessage("");
    setLoading(true);

    // Create an empty assistant message.
    // Streaming chunks will appear inside this message.
    setMessages((previousMessages) => [
      ...previousMessages,
      {
        sender: "assistant",
        text: "",
      },
    ]);

    try {
      let streamedResponse = "";

      const response = await sendChatMessage(
        trimmedMessage,
        sessionId,
        (chunk) => {
          streamedResponse += chunk;

          setMessages((previousMessages) => {
            const updatedMessages = [...previousMessages];

            const lastMessageIndex =
              updatedMessages.length - 1;

            updatedMessages[lastMessageIndex] = {
              sender: "assistant",
              text: streamedResponse,
            };

            return updatedMessages;
          });
        }
      );

      // Fallback if no streaming content was received.
      if (!streamedResponse && response.content) {
        setMessages((previousMessages) => {
          const updatedMessages = [...previousMessages];

          const lastMessageIndex =
            updatedMessages.length - 1;

          updatedMessages[lastMessageIndex] = {
            sender: "assistant",
            text: response.content,
          };

          return updatedMessages;
        });
      }

      // Save the session ID.
      if (response.session_id) {
        setSessionId(response.session_id);
      }
    } catch (error) {
      console.error("Chat request failed:", error);

      setMessages((previousMessages) => {
        const updatedMessages = [...previousMessages];

        const lastMessageIndex =
          updatedMessages.length - 1;

        updatedMessages[lastMessageIndex] = {
          sender: "assistant",
          text:
            "Sorry, I could not connect to the AI assistant. Please check that the AgentOS backend is running.",
        };

        return updatedMessages;
      });
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    if (loading) {
      return;
    }

    setMessages([
      {
        sender: "assistant",
        text: "Hello! 👋 How can I help you with your farming question today?",
      },
    ]);

    setMessage("");
    setSessionId(null);
  };

  return (
    <div className="chat-page">
      <header className="header">
        <div>
          <h1>🌾 GramSwaram Farmer</h1>
          <p>AI Farmer Assistant</p>
        </div>

        <button
          className="new-chat-button"
          onClick={handleNewChat}
          disabled={loading}
        >
          🆕 New Chat
        </button>
      </header>

      <main className="chat-container">
        <section className="chat-card">
          <div className="chat-header">
            <div>
              <h2>💬 AI Farmer Assistant</h2>

              <p>
                Ask questions about farming, crops, and agriculture.
              </p>
            </div>
          </div>

          <div className="messages">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`message ${
                  item.sender === "user"
                    ? "user-message"
                    : "assistant-message"
                }`}
              >
                <strong>
                  {item.sender === "user"
                    ? "You"
                    : "AI Assistant"}
                </strong>

                <div className="message-content">
                  <ReactMarkdown>
                    {item.text}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSend();
                }
              }}
              placeholder="Type your farming question..."
              disabled={loading}
            />

            <button
              className="send-button"
              onClick={handleSend}
              disabled={loading}
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default Chat;