// Μικρά, καθαρά presentational components για το admin panel.
// Δεν χρησιμοποιούν hooks -> μένουν server components.

import Link from "next/link";

export function PageHeading({
  title,
  subtitle,
  count,
}: {
  title: string;
  subtitle?: string;
  count?: number;
}) {
  return (
    <header className="mb-6 flex items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle && (
          <p className="mt-1 text-sm text-foreground/60">{subtitle}</p>
        )}
      </div>
      {count != null && (
        <span className="shrink-0 rounded-full bg-foreground/10 px-3 py-1 text-sm text-foreground/70">
          {count} σύνολο
        </span>
      )}
    </header>
  );
}

export function Table({
  headers,
  children,
}: {
  headers: string[];
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-foreground/10">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-foreground/10 bg-foreground/[0.03] text-left text-foreground/60">
            {headers.map((h) => (
              <th key={h} className="whitespace-nowrap px-4 py-3 font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

export function Td({
  children,
  mono,
}: {
  children: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <td
      className={`border-b border-foreground/5 px-4 py-3 align-middle ${
        mono ? "font-mono text-xs text-foreground/70" : ""
      }`}
    >
      {children}
    </td>
  );
}

export function StatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${
        active
          ? "bg-green-500/15 text-green-600 dark:text-green-400"
          : "bg-foreground/10 text-foreground/50"
      }`}
    >
      {active ? "Ενεργή" : "Ανενεργή"}
    </span>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <p className="rounded-2xl border border-dashed border-foreground/15 px-4 py-10 text-center text-foreground/50">
      {message}
    </p>
  );
}

export function ErrorState({ message }: { message: string }) {
  const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return (
    <div className="rounded-2xl border border-red-500/30 bg-red-500/5 px-4 py-6 text-sm text-red-600 dark:text-red-400">
      <p className="font-medium">Σφάλμα φόρτωσης</p>
      <p className="mt-1 text-foreground/60">{message}</p>
      <p className="mt-2 text-foreground/50">
        Βεβαιώσου ότι τρέχει το backend στο <code>{api}</code>.
      </p>
    </div>
  );
}

export function StatCard({
  label,
  value,
  href,
}: {
  label: string;
  value: React.ReactNode;
  href: string;
}) {
  return (
    <Link
      href={href}
      className="rounded-2xl border border-foreground/10 p-5 transition-colors hover:bg-foreground/[0.03]"
    >
      <div className="text-sm text-foreground/60">{label}</div>
      <div className="mt-2 text-3xl font-semibold tabular-nums">{value}</div>
    </Link>
  );
}
