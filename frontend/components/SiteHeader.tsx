"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/recipes", label: "Recipes" },
  { href: "/weekly-planner", label: "Weekly planner" },
  { href: "/grocery-list", label: "Grocery list" },
];

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link className="brand" href="/" aria-label="Smart Bite home">
          <span className="brand-mark" aria-hidden="true">✦</span>
          <span>Smart Bite</span>
        </Link>
        <nav className="site-nav" aria-label="Primary navigation">
          {links.map((link) => {
            const active = pathname === link.href || (link.href === "/recipes" && pathname.startsWith("/recipes"));
            return <Link key={link.href} href={link.href} className={active ? "active" : ""} aria-current={active ? "page" : undefined}>{link.label}</Link>;
          })}
        </nav>
        <Link href="/recipes/new" className="button header-action">Add recipe</Link>
      </div>
    </header>
  );
}
