const TOKEN_KEY = "ktisis_token";

let onUnauthorized = () => {};

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

export const getToken = () => sessionStorage.getItem(TOKEN_KEY);

export function setToken(token) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token);
  else sessionStorage.removeItem(TOKEN_KEY);
}

async function request(method, path, body) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const response = await fetch(`/api${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (response.status === 401 && !path.startsWith("/auth/")) {
    setToken(null);
    onUnauthorized();
    throw new Error("Η σύνδεσή σου έληξε. Συνδέσου ξανά.");
  }

  if (!response.ok) {
    let message = `Σφάλμα ${response.status}`;
    try {
      const data = await response.json();
      if (typeof data.detail === "string") message = data.detail;
      else if (Array.isArray(data.detail)) message = "Έλεγξε τα στοιχεία που συμπλήρωσες.";
    } catch {
      // η απάντηση δεν ήταν JSON - κρατάμε το γενικό μήνυμα
    }
    throw new Error(message);
  }
  return response.json();
}

export const api = {
  get: (path) => request("GET", path),
  post: (path, body) => request("POST", path, body),
  put: (path, body) => request("PUT", path, body),
  delete: (path) => request("DELETE", path),
};
