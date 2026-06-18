"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

// Δείχνει μήνυμα όταν το Stripe γυρίσει πίσω με ?checkout=success|cancel
export default function CheckoutBanner() {
  const params = useSearchParams();
  const router = useRouter();
  const status = params.get("checkout");
  const [dismissed, setDismissed] = useState(false);

  const visible =
    !dismissed && (status === "success" || status === "cancel");
  if (!visible) return null;

  const success = status === "success";

  function dismiss() {
    setDismissed(true);
    // Καθαρίζουμε το query param από το URL
    router.replace("/");
  }

  return (
    <div
      role="status"
      className={`mb-6 flex items-center justify-between gap-4 rounded-xl border px-4 py-3 text-sm ${
        success
          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
          : "border-foreground/15 bg-foreground/5 text-foreground/70"
      }`}
    >
      <span>
        {success
          ? "Η πληρωμή ολοκληρώθηκε! Η ταινία προστέθηκε στη βιβλιοθήκη σου."
          : "Η πληρωμή ακυρώθηκε."}
      </span>
      <button
        type="button"
        onClick={dismiss}
        aria-label="Κλείσιμο"
        className="shrink-0 rounded-full p-1 text-current/70 transition-colors hover:bg-foreground/10"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          className="h-4 w-4"
          aria-hidden="true"
        >
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
