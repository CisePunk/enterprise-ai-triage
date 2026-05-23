const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export function fetchHealth() {
  return request("/health");
}

export function fetchDashboard() {
  return request("/dashboard");
}

export function fetchTickets() {
  return request("/tickets");
}

export function submitTicket(ticket) {
  return request("/tickets", {
    method: "POST",
    body: JSON.stringify(ticket),
  });
}
