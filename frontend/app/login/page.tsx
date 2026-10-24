"use client";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter(); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent) { event.preventDefault(); if (!email.trim() || !password) return setError("Email and password are required."); setLoading(true); setError(""); try { const data = await auth.login(email, password); auth.save(data.access_token); router.replace("/"); } catch (e) { setError(e instanceof Error ? e.message : "Unable to sign in."); } finally { setLoading(false); } }
  return <section className="auth-page"><div className="auth-card"><h1>Sign in</h1><form onSubmit={submit}><label>Email<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label><label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required /></label>{error && <p role="alert">{error}</p>}<button type="submit" disabled={loading}>{loading ? "Signing in…" : "Sign in"}</button></form><Link href="/register">Create an account</Link></div></section>;
}
