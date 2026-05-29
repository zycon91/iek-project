const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Αντιστοιχεί στο MovieResponseFrontPage του backend
export type Movie = {
  title: string;
  release_date: string; // ISO date "YYYY-MM-DD"
  rating: number;
};

// Αντιστοιχεί στο Page[T] του backend
export type Page<T> = {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
};

export async function getMovies(params?: {
  skip?: number;
  limit?: number;
  genre?: string;
  search?: string;
  sort_by?: "title" | "rating" | "release_date";
  order?: "asc" | "desc";
}): Promise<Page<Movie>> {
  const query = new URLSearchParams();
  if (params?.skip != null) query.set("skip", String(params.skip));
  if (params?.limit != null) query.set("limit", String(params.limit));
  if (params?.genre) query.set("genre", params.genre);
  if (params?.search) query.set("search", params.search);
  if (params?.sort_by) query.set("sort_by", params.sort_by);
  if (params?.order) query.set("order", params.order);

  const qs = query.toString();
  const res = await fetch(`${API_URL}/movies/${qs ? `?${qs}` : ""}`, {
    // Πάντα φρέσκα δεδομένα από το API
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Αποτυχία φόρτωσης ταινιών (${res.status})`);
  }

  return res.json();
}
