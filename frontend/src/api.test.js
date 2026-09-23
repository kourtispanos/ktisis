import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { api, getToken, setToken, setUnauthorizedHandler } from "./api.js";

function mockFetch(status, body) {
  global.fetch = vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    json: () => Promise.resolve(body),
  });
}

beforeEach(() => {
  sessionStorage.clear();
  setUnauthorizedHandler(() => {});
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("token", () => {
  test("αποθηκεύεται και διαβάζεται", () => {
    setToken("abc123");
    expect(getToken()).toBe("abc123");
  });

  test("null σβήνει το token", () => {
    setToken("abc123");
    setToken(null);
    expect(getToken()).toBeNull();
  });
});

describe("api requests", () => {
  test("στέλνει το token ως Authorization header όταν υπάρχει", async () => {
    setToken("my-token");
    mockFetch(200, { ok: true });
    await api.get("/clients");
    const [, options] = global.fetch.mock.calls[0];
    expect(options.headers.Authorization).toBe("Bearer my-token");
  });

  test("δεν στέλνει Authorization όταν δεν υπάρχει token", async () => {
    mockFetch(200, { ok: true });
    await api.get("/auth/me");
    const [, options] = global.fetch.mock.calls[0];
    expect(options.headers.Authorization).toBeUndefined();
  });

  test("post στέλνει JSON body με Content-Type", async () => {
    mockFetch(201, { ok: true });
    await api.post("/clients", { name: "Γιάννης" });
    const [, options] = global.fetch.mock.calls[0];
    expect(options.headers["Content-Type"]).toBe("application/json");
    expect(options.body).toBe(JSON.stringify({ name: "Γιάννης" }));
  });

  test("401 σε προστατευμένη διαδρομή σβήνει το token και ειδοποιεί", async () => {
    setToken("my-token");
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);
    mockFetch(401, { detail: "Δεν είσαι συνδεδεμένος" });

    await expect(api.get("/clients")).rejects.toThrow("Η σύνδεσή σου έληξε");
    expect(getToken()).toBeNull();
    expect(onUnauthorized).toHaveBeenCalledOnce();
  });

  test("401 στο login ΔΕΝ ενεργοποιεί το unauthorized handler (είναι αναμενόμενο λάθος)", async () => {
    const onUnauthorized = vi.fn();
    setUnauthorizedHandler(onUnauthorized);
    mockFetch(401, { detail: "Λάθος όνομα χρήστη ή κωδικός" });

    await expect(api.post("/auth/login", { username: "x", password: "y" }))
      .rejects.toThrow("Λάθος όνομα χρήστη ή κωδικός");
    expect(onUnauthorized).not.toHaveBeenCalled();
  });

  test("άλλα σφάλματα δείχνουν το detail του server", async () => {
    mockFetch(409, { detail: "Αυτό το όνομα χρήστη υπάρχει ήδη" });
    await expect(api.post("/auth/signup", { username: "x", password: "y" }))
      .rejects.toThrow("Αυτό το όνομα χρήστη υπάρχει ήδη");
  });

  test("σφάλμα χωρίς έγκυρο JSON σώμα δείχνει γενικό μήνυμα", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 500,
      ok: false,
      json: () => Promise.reject(new Error("not json")),
    });
    await expect(api.get("/clients")).rejects.toThrow("Σφάλμα 500");
  });
});
