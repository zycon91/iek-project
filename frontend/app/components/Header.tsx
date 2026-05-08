"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Show, UserButton } from "@clerk/nextjs";

const tabs = [
  { href: "/", label: "Αρχική" },
  { href: "/movies", label: "Ταινίες" },
  { href: "/series", label: "Σειρές" },
];

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between gap-4 border-b border-foreground/10 bg-background/80 px-6 py-3 backdrop-blur">
      <nav className="flex items-center gap-1">
        {tabs.map((tab) => {
          const active =
            tab.href === "/" ? pathname === "/" : pathname.startsWith(tab.href);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={`rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                active
                  ? "bg-foreground text-background"
                  : "hover:bg-foreground/10"
              }`}
            >
              {tab.label}
            </Link>
          );
        })}
      </nav>

      <div className="flex items-center">
        <Show when="signed-in">
          <UserButton />
        </Show>
        <Show when="signed-out">
          <Link
            href="/sign-in"
            aria-label="Λογαριασμός"
            title="Λογαριασμός"
            className="flex h-10 w-10 items-center justify-center rounded-full bg-foreground text-background transition-opacity hover:opacity-90"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-3.33 0-10 1.67-10 5v3h20v-3c0-3.33-6.67-5-10-5Z" />
            </svg>
          </Link>
        </Show>
      </div>
    </header>
  );
}
