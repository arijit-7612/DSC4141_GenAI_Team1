"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { auth } from "../lib/auth";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname(); const router = useRouter(); const [ready, setReady] = useState(false);
  const publicPage = pathname === "/login" || pathname === "/register";
  useEffect(() => { if (!publicPage && !auth.token()) router.replace("/login"); if (publicPage && auth.token()) router.replace("/"); setReady(true); }, [pathname, publicPage, router]);
  return ready && (publicPage || auth.token()) ? <>{children}</> : null;
}
