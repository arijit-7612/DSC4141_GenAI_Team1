import type { Metadata } from "next";
import "./globals.css";
import "./auth.css";
import { SiteHeader } from "../components/SiteHeader";
import { AuthGate } from "../components/AuthGate";

export const metadata: Metadata = {
  title: "Smart Bite | Meal planning made simple",
  description: "Plan healthy meals and keep your kitchen organized.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AuthGate><SiteHeader /><main>{children}</main></AuthGate>
      </body>
    </html>
  );
}
