import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Meal Planner",
  description: "Manage healthy recipes and ingredients",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <Link href="/recipes" className="brand">Meal Planner</Link>
          <Link href="/recipes/new" className="button">Add recipe</Link>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
