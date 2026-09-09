import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Meal Planner",
  description: "Manage healthy recipes and ingredients",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
