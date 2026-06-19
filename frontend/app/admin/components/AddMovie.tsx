"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@clerk/nextjs";
import {
  searchTmdb,
  createMovieFromTmdb,
  type TmdbSearchResult,
} from "../../lib/movies";

export default function AddMovie() {
  const router = useRouter();
  const { getToken } = useAuth();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<TmdbSearchResult[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [addingId, setAddingId] = useState<number | null>(null);
  const [addedIds, setAddedIds] = useState<number[]>([]);

  async function onSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResults([]);
    try {
      const token = await getToken();
      if (!token) throw new Error("Δεν βρέθηκε token — κάνε ξανά login.");
      const res = await searchTmdb(query.trim(), token);
      setResults(res);
      setSearched(true);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function onAdd(r: TmdbSearchResult) {
    setAddingId(r.tmdb_id);
    setError(null);
    try {
      const token = await getToken();
      if (!token) throw new Error("Δεν βρέθηκε token — κάνε ξανά login.");
      await createMovieFromTmdb(r.tmdb_id, token);
      setAddedIds((ids) => [...ids, r.tmdb_id]);
      router.refresh(); // ανανεώνει τον πίνακα (server component)
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setAddingId(null);
    }
  }

  return (
    <div className="mb-6">
      {!open ? (
        <button
          onClick={() => setOpen(true)}
          className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90"
        >
          + Προσθήκη ταινίας
        </button>
      ) : (
        <div className="rounded-2xl border border-foreground/10 bg-foreground/[0.02] p-4">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-sm font-medium">Προσθήκη ταινίας από TMDB</span>
            <button
              onClick={() => setOpen(false)}
              className="text-sm text-foreground/50 hover:text-foreground"
            >
              ✕ Κλείσιμο
            </button>
          </div>

          <form onSubmit={onSearch} className="flex gap-2">
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Όνομα ταινίας (π.χ. Inception)…"
              className="flex-1 rounded-lg border border-foreground/15 bg-transparent px-3 py-2 text-sm outline-none transition-colors focus:border-foreground/40"
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {loading ? "Αναζήτηση…" : "Αναζήτηση"}
            </button>
          </form>

          {error && (
            <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>
          )}

          {searched && !loading && results.length === 0 && !error && (
            <p className="mt-3 text-sm text-foreground/50">
              Δεν βρέθηκαν αποτελέσματα.
            </p>
          )}

          {results.length > 0 && (
            <ul className="mt-3 divide-y divide-foreground/5">
              {results.slice(0, 8).map((r) => {
                const added = addedIds.includes(r.tmdb_id);
                const year = r.release_date ? r.release_date.slice(0, 4) : "—";
                return (
                  <li
                    key={r.tmdb_id}
                    className="flex items-center justify-between gap-4 py-2"
                  >
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium">
                        {r.title}{" "}
                        <span className="text-foreground/50">({year})</span>
                      </div>
                      <div className="text-xs text-foreground/50">
                        ⭐ {r.rating.toFixed(1)} · TMDB #{r.tmdb_id}
                      </div>
                    </div>
                    {added ? (
                      <span className="shrink-0 text-xs font-medium text-green-600 dark:text-green-400">
                        ✓ Προστέθηκε
                      </span>
                    ) : (
                      <button
                        onClick={() => onAdd(r)}
                        disabled={addingId === r.tmdb_id}
                        className="shrink-0 rounded-md border border-foreground/15 px-3 py-1 text-xs font-medium transition-colors hover:bg-foreground/10 disabled:opacity-50"
                      >
                        {addingId === r.tmdb_id ? "Προσθήκη…" : "Προσθήκη"}
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
