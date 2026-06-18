"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { useAuth } from "@clerk/nextjs";

import {
  getMovie,
  createCheckout,
  mediaUrl,
  formatDate,
  formatRuntime,
  formatPrice,
  type MovieDetail,
  type CheckoutKind,
} from "../lib/movies";

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-foreground/10 px-3 py-1 text-sm font-medium text-foreground/80">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        className="h-4 w-4 text-amber-500"
        aria-hidden="true"
      >
        <path d="m12 17.27 6.18 3.73-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
      </svg>
      {rating}
    </span>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs uppercase tracking-wide text-foreground/40">
        {label}
      </span>
      <span className="text-sm font-medium text-foreground/90">{value}</span>
    </div>
  );
}

function ModalBody({ movie }: { movie: MovieDetail }) {
  const poster = mediaUrl(movie.poster_url) ?? mediaUrl(movie.thumbnail_url);

  const { getToken, isSignedIn } = useAuth();
  const [pending, setPending] = useState<CheckoutKind | null>(null);
  const [checkoutError, setCheckoutError] = useState<string | null>(null);

  async function handleCheckout(kind: CheckoutKind) {
    setCheckoutError(null);

    if (!isSignedIn) {
      setCheckoutError("Πρέπει να συνδεθείς πρώτα.");
      return;
    }

    setPending(kind);
    try {
      const token = await getToken();
      if (!token) throw new Error("Λείπει το token σύνδεσης.");
      // Ανακατεύθυνση στη σελίδα πληρωμής του Stripe
      window.location.href = await createCheckout(movie.id, kind, token);
    } catch (err: unknown) {
      setCheckoutError(
        err instanceof Error ? err.message : "Κάτι πήγε στραβά.",
      );
      setPending(null);
    }
  }

  return (
    <div className="grid gap-8 sm:grid-cols-[260px_1fr]">
      <div className="relative mx-auto aspect-[2/3] w-48 overflow-hidden rounded-xl bg-foreground/10 sm:mx-0 sm:w-full">
        {poster ? (
          <Image
            src={poster}
            alt={`Αφίσα: ${movie.title}`}
            fill
            unoptimized
            className="object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-5xl font-semibold text-foreground/30">
            {movie.title.charAt(0).toUpperCase()}
          </div>
        )}
      </div>

      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-3">
          <h2 className="text-3xl font-semibold leading-tight">{movie.title}</h2>
          <div className="flex flex-wrap items-center gap-2">
            <StarRating rating={movie.rating} />
            {movie.genre && (
              <span className="rounded-full bg-foreground/10 px-3 py-1 text-sm text-foreground/70">
                {movie.genre}
              </span>
            )}
          </div>
        </div>

        {movie.description && (
          <p className="text-sm leading-relaxed text-foreground/70">
            {movie.description}
          </p>
        )}

        <div className="grid grid-cols-2 gap-4">
          <InfoRow label="Κυκλοφορία" value={formatDate(movie.release_date)} />
          <InfoRow label="Διάρκεια" value={formatRuntime(movie.duration)} />
        </div>

        <div className="mt-auto flex flex-col gap-3 pt-2">
          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={() => handleCheckout("rental")}
              disabled={pending !== null}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-foreground/20 bg-foreground/5 px-5 py-3 text-sm font-semibold transition-colors hover:bg-foreground/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-foreground/40 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {pending === "rental" ? (
                "Ανακατεύθυνση…"
              ) : (
                <>
                  Ενοικίαση
                  <span className="text-foreground/60">
                    {formatPrice(movie.rental_price)}
                  </span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={() => handleCheckout("purchase")}
              disabled={pending !== null}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-foreground px-5 py-3 text-sm font-semibold text-background transition-opacity hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-foreground/40 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {pending === "purchase" ? (
                "Ανακατεύθυνση…"
              ) : (
                <>
                  Αγορά
                  <span className="opacity-70">
                    {formatPrice(movie.purchase_price)}
                  </span>
                </>
              )}
            </button>
          </div>
          {checkoutError && (
            <p className="text-sm text-red-500">{checkoutError}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function MovieModal({
  movieId,
  onClose,
}: {
  movieId: string | null;
  onClose: () => void;
}) {
  // Το αποτέλεσμα κρατά και το id στο οποίο ανήκει· έτσι το "loading"
  // προκύπτει derived (state.id !== movieId) χωρίς σύγχρονο setState στο effect.
  const [state, setState] = useState<{
    id: string;
    movie: MovieDetail | null;
    error: string | null;
  } | null>(null);

  // Φόρτωση λεπτομερειών κάθε φορά που αλλάζει το επιλεγμένο id
  useEffect(() => {
    if (!movieId) return;

    let active = true;

    getMovie(movieId)
      .then((data) => {
        if (active) setState({ id: movieId, movie: data, error: null });
      })
      .catch((err: unknown) => {
        if (active) {
          setState({
            id: movieId,
            movie: null,
            error: err instanceof Error ? err.message : "Κάτι πήγε στραβά.",
          });
        }
      });

    return () => {
      active = false;
    };
  }, [movieId]);

  const ready = state?.id === movieId;
  const loading = !ready;
  const movie = ready ? state?.movie ?? null : null;
  const error = ready ? state?.error ?? null : null;

  // Κλείσιμο με Escape + κλείδωμα του scroll όσο είναι ανοιχτό
  useEffect(() => {
    if (!movieId) return;

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }

    document.addEventListener("keydown", onKeyDown);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = prevOverflow;
    };
  }, [movieId, onClose]);

  if (!movieId) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6"
      role="dialog"
      aria-modal="true"
      aria-label="Λεπτομέρειες ταινίας"
    >
      {/* Backdrop — κλικ έξω για κλείσιμο */}
      <button
        type="button"
        aria-label="Κλείσιμο"
        onClick={onClose}
        className="absolute inset-0 h-full w-full cursor-default bg-black/70 backdrop-blur-sm"
      />

      <div className="relative z-10 max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-2xl border border-foreground/10 bg-background p-6 shadow-2xl sm:p-10">
        <button
          type="button"
          onClick={onClose}
          aria-label="Κλείσιμο"
          className="absolute right-4 top-4 flex h-8 w-8 items-center justify-center rounded-full bg-foreground/10 text-foreground/70 transition-colors hover:bg-foreground/20 hover:text-foreground"
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

        {loading && (
          <div className="flex min-h-48 items-center justify-center text-foreground/50">
            Φόρτωση…
          </div>
        )}

        {error && !loading && (
          <div className="flex min-h-48 flex-col items-center justify-center gap-2 text-center">
            <p className="text-foreground/70">{error}</p>
            <button
              type="button"
              onClick={onClose}
              className="rounded-full bg-foreground/10 px-4 py-2 text-sm font-medium hover:bg-foreground/20"
            >
              Κλείσιμο
            </button>
          </div>
        )}

        {movie && !loading && <ModalBody movie={movie} />}
      </div>
    </div>
  );
}
