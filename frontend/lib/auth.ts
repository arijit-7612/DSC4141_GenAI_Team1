const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const KEY = "smart-bite-access-token";

type AuthResponse = { access_token: string };

async function post(path: string, body: Record<string, string>): Promise<AuthResponse> {
  const response = await fetch(`${API_URL}${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new Error(data?.detail ?? "Something went wrong. Please try again.");
  return data;
}

export const auth = {
  token: () => typeof window === "undefined" ? null : localStorage.getItem(KEY),
  save: (token: string) => localStorage.setItem(KEY, token),
  clear: () => localStorage.removeItem(KEY),
  login: (email: string, password: string) => post("/auth/login", { email, password }),
  register: (email: string, password: string) => post("/auth/register", { email, password }),
};
