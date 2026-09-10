import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "../components/SiteHeader";

export const metadata: Metadata = {
  title: "Smart Bite | Meal planning made simple",
  description: "Plan healthy meals and keep your kitchen organized.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <SiteHeader />
        <main>{children}</main>
      </body>
    </html>
  );
}
