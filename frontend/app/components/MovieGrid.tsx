import { getMovies, type Movie } from "../lib/movies";

function formatDate(iso: string): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("el-GR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function MovieCard({ movie }: { movie: Movie }) {
  return (
    <article className="flex flex-col justify-between gap-4 rounded-2xl border border-foreground/10 bg-foreground/[0.03] p-5 transition-colors hover:border-foreground/25">
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
    </article>
  );
}

export default async function MovieGrid() {
  const page = await getMovies({ limit: 20, sort_by: "rating", order: "desc" });

  if (page.items.length === 0) {
    return (
      <p className="text-foreground/60">Δεν υπάρχουν ταινίες ακόμη.</p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {page.items.map((movie, i) => (
        <MovieCard key={`${movie.title}-${i}`} movie={movie} />
      ))}
    </div>
  );
}
