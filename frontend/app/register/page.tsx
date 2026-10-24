"use client";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "../../lib/auth";

export default function RegisterPage() {
  const router = useRouter(); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) { event.preventDefault(); if (!email.trim() || !password) return setError("Email and password are required."); if (password.length < 8) return setError("Password must be at least 8 characters."); setLoading(true); setError(""); try { const data = await auth.register(email, password); auth.save(data.access_token); router.replace("/"); } catch (e) { setError(e instanceof Error ? e.message : "Unable to create account."); } finally { setLoading(false); } }
  return <section className="auth-page"><div className="auth-card"><h1>Create account</h1><form onSubmit={submit}><label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label><label>Password<input type="password" minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} required /></label>{error && <p role="alert">{error}</p>}<button type="submit" disabled={loading}>{loading ? "Creating…" : "Create account"}</button></form><Link href="/login">Back to sign in</Link></div></section>;
}
