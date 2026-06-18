"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { href: "/admin", label: "Πίνακας", exact: true },
  { href: "/admin/movies", label: "Ταινίες" },
  { href: "/admin/rentals", label: "Ενοικιάσεις" },
  { href: "/admin/purchases", label: "Αγορές" },
  { href: "/admin/users", label: "Χρήστες" },
  { href: "/admin/subscriptions", label: "Συνδρομές" },
];

export default function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-56 shrink-0 flex-col gap-1 border-r border-foreground/10 bg-foreground/[0.02] p-4">
      <div className="mb-4 px-3 text-lg font-semibold tracking-tight">
        🎬 Admin
      </div>
      <nav className="flex flex-col gap-1">
        {items.map((it) => {
          const active = it.exact
            ? pathname === it.href
            : pathname.startsWith(it.href);
          return (
            <Link
              key={it.href}
              href={it.href}
              className={`rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-foreground text-background"
                  : "text-foreground/75 hover:bg-foreground/10"
              }`}
            >
              {it.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
