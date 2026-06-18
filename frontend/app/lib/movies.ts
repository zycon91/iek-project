const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Αντιστοιχεί στο MovieResponseFrontPage του backend
export type Movie = {
  id: string;
  title: string;
  release_date: string; // ISO date "YYYY-MM-DD"
  rating: number;
  thumbnail_url: string | null;
};

// Αντιστοιχεί στο MovieResponse του backend (πλήρεις λεπτομέρειες μιας ταινίας)
export type MovieDetail = {
  id: string;
  title: string;
  duration: number; // λεπτά
  description: string;
  genre: string;
  release_date: string; // ISO date "YYYY-MM-DD"
  rating: number;
  rental_price: number; // σε λεπτά του ευρώ (π.χ. 399 = 3,99 €)
  purchase_price: number; // σε λεπτά του ευρώ
  poster_url: string | null;
  thumbnail_url: string | null;
};

// Το backend επιστρέφει σχετικά URLs (π.χ. "/static/movies/thumbnails/x.webp")
export function mediaUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  return `${API_URL}${path}`;
}

// --- Κοινοί formatters (καθαρές συναρτήσεις, χρησιμοποιούνται σε κάρτες & modal) ---

export function formatDate(iso: string): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("el-GR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

// 142 -> "2ω 22λ", 95 -> "1ω 35λ", 0/κενό -> "—"
export function formatRuntime(minutes: number): string {
  if (!minutes || minutes <= 0) return "—";
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) return `${mins}λ`;
  return `${hours}ω ${mins}λ`;
}

// 399 -> "3,99 €" (η τιμή φυλάσσεται σε λεπτά του ευρώ)
export function formatPrice(cents: number): string {
  return `${(cents / 100).toLocaleString("el-GR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })} €`;
}

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

// Φέρνει τις πλήρεις λεπτομέρειες μιας ταινίας — GET /movies/{id}
export async function getMovie(id: string): Promise<MovieDetail> {
  const res = await fetch(`${API_URL}/movies/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error(`Αποτυχία φόρτωσης ταινίας (${res.status})`);
  }

  return res.json();
}

export type CheckoutKind = "rental" | "purchase";

// Ζητά από το backend ένα Stripe Checkout session και επιστρέφει το URL πληρωμής.
// Το `token` είναι το Clerk session token (από useAuth().getToken()).
export async function createCheckout(
  movieId: string,
  kind: CheckoutKind,
  token: string,
): Promise<string> {
  const res = await fetch(`${API_URL}/checkout/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ movie_id: movieId, kind }),
  });

  if (!res.ok) {
    throw new Error(`Αποτυχία έναρξης πληρωμής (${res.status})`);
  }

  const data: { checkout_url: string } = await res.json();
  return data.checkout_url;
}
