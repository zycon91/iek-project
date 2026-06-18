import { getMovies } from "../lib/movies";
import MovieGallery from "./MovieGallery";

export default async function MovieGrid() {
  const page = await getMovies({ limit: 20, sort_by: "rating", order: "desc" });

  if (page.items.length === 0) {
    return <p className="text-foreground/60">Δεν υπάρχουν ταινίες ακόμη.</p>;
  }

  return <MovieGallery movies={page.items} />;
}
