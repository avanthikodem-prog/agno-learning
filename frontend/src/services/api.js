const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:7777";

export async function sendChatMessage(
  message,
  sessionId = null,
  onChunk = null
) {
  const formData = new FormData();

  formData.append("message", message);
  formData.append("stream", "true");

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

  if (!response.body) {
    throw new Error("Streaming response body is not available.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";
  let fullResponse = "";
  let returnedSessionId = sessionId;

  const processEvent = (eventText) => {
    const lines = eventText.split(/\r?\n/);

    let eventName = "";
    const dataLines = [];

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventName = line.slice(6).trim();
      }

      if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trim());
      }
    }

    if (dataLines.length === 0) {
      return;
    }

    const data = dataLines.join("\n");

    if (!data || data === "[DONE]") {
      return;
    }

    let parsed;

    try {
      parsed = JSON.parse(data);
    } catch {
      return;
    }

    // Capture session ID if AgentOS sends it.
    if (parsed.session_id) {
      returnedSessionId = parsed.session_id;
    }

    if (parsed.session?.session_id) {
      returnedSessionId = parsed.session.session_id;
    }

    // Only use actual content events.
    const isContentEvent =
      eventName === "RunContent" ||
      parsed.event === "RunContent" ||
      parsed.event === "run_content";

    if (!isContentEvent) {
      return;
    }

    const chunk =
      parsed.content ||
      parsed.delta?.content ||
      parsed.message?.content ||
      "";

    if (!chunk) {
      return;
    }

    fullResponse += chunk;

    if (onChunk) {
      onChunk(chunk);
    }
  };

  while (true) {
    const { value, done } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    // SSE events are separated by a blank line.
    const events = buffer.split(/\r?\n\r?\n/);

    // Keep the incomplete event for the next network chunk.
    buffer = events.pop() || "";

    for (const eventText of events) {
      processEvent(eventText);
    }
  }

  // Flush any remaining decoder data.
  buffer += decoder.decode();

  // Process the final event if it does not end with a blank line.
  if (buffer.trim()) {
    processEvent(buffer);
  }

  return {
    content: fullResponse,
    session_id: returnedSessionId,
  };
}