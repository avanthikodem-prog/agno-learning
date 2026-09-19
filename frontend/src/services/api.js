const API_BASE_URL = "http://127.0.0.1:7777";

export async function sendChatMessage(message, sessionId = null) {
  const formData = new FormData();

  formData.append("message", message);
  formData.append("stream", "false");

  if (sessionId) {
    formData.append("session_id", sessionId);
  }

  const response = await fetch(
    `${API_BASE_URL}/agents/agri-assistant/runs`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${import.meta.env.VITE_AGENTOS_KEY}`,
      },
      body: formData,
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `AgentOS request failed: ${response.status} ${errorText}`
    );
  }

  return response.json();
}