"use client";

import { useState } from "react";
import Image from "next/image";

import { mediaUrl, formatDate, type Movie } from "../lib/movies";
import MovieModal from "./MovieModal";

function MoviePoster({ movie }: { movie: Movie }) {
  const src = mediaUrl(movie.thumbnail_url);

  if (!src) {
    return (
      <div className="flex aspect-[2/3] w-full items-center justify-center rounded-xl bg-foreground/10 text-4xl font-semibold text-foreground/30">
        {movie.title.charAt(0).toUpperCase()}
      </div>
    );
  }

  return (
    <div className="relative aspect-[2/3] w-full overflow-hidden rounded-xl bg-foreground/10">
      {/* unoptimized: το backend σερβίρει ήδη έτοιμα WEBP thumbnails (max 400px) */}
      <Image
        src={src}
        alt={`Αφίσα: ${movie.title}`}
        fill
        unoptimized
        className="object-cover"
      />
    </div>
  );
}

function MovieCard({
  movie,
  onSelect,
}: {
  movie: Movie;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className="flex flex-col justify-between gap-4 rounded-2xl border border-foreground/10 bg-foreground/[0.03] p-5 text-left transition-colors hover:border-foreground/25 focus:outline-none focus-visible:ring-2 focus-visible:ring-foreground/40"
    >
      <MoviePoster movie={movie} />
      <h3 className="text-lg font-semibold leading-snug">{movie.title}</h3>
      <div className="flex items-center justify-between text-sm text-foreground/60">
        <span>{formatDate(movie.release_date)}</span>
        <span className="inline-flex items-center gap-1 rounded-full bg-foreground/10 px-2.5 py-1 font-medium text-foreground/80">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            className="h-4 w-4 text-amber-500"
            aria-hidden="true"
          >
            <path d="m12 17.27 6.18 3.73-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
          </svg>
          {movie.rating}
        </span>
      </div>
    </button>
  );
}

export default function MovieGallery({ movies }: { movies: Movie[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            movie={movie}
            onSelect={() => setSelectedId(movie.id)}
          />
        ))}
      </div>

      <MovieModal movieId={selectedId} onClose={() => setSelectedId(null)} />
    </>
  );
}
