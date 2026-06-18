// Data layer για το admin panel.
// Καλεί τα ίδια list endpoints του backend (Page[T]) με τη δημόσια σελίδα.
// ΣΗΜΕΙΩΣΗ ασφάλειας: η ορατότητα του admin panel ελέγχεται με τον ρόλο του Clerk
// (publicMetadata.role === "admin", δες admin_panel.md §3.9). Σε production τα
// endpoints πρέπει επιπλέον να κλειδώνουν με Depends(require_admin) στο backend.

import type { Page } from "./movies";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// --- Τύποι, αντίστοιχοι με τα *Response schemas του backend ---

// UserResponse
export type AdminUser = {
  id: string;
  email: string;
  username: string;
  fullname: string;
};

// RentalResponse
export type Rental = {
  id: string;
  user_id: string;
  movie_id: string;
  start_date: string;
  end_date: string;
};

// PurchaseResponse
export type Purchase = {
  id: string;
  user_id: string;
  movie_id: string;
  amount_paid: number; // σε λεπτά του ευρώ
  purchased_at: string;
};

// SubscriptionResponse
export type Subscription = {
  id: string;
  user_id: string;
  plan: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
};

async function getPage<T>(path: string, limit: number): Promise<Page<T>> {
  const res = await fetch(`${API_URL}${path}?limit=${limit}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Αποτυχία φόρτωσης (${res.status})`);
  }
  return res.json();
}

export const getUsers = (limit = 100) => getPage<AdminUser>("/users/", limit);
export const getRentals = (limit = 50) => getPage<Rental>("/rentals/", limit);
export const getPurchases = (limit = 50) => getPage<Purchase>("/purchases/", limit);
export const getSubscriptions = (limit = 100) =>
  getPage<Subscription>("/subscriptions/", limit);

// Σύντομη μορφή UUID για ευανάγνωστους πίνακες (π.χ. "3f2a1b9c")
export function shortId(id: string): string {
  return id.slice(0, 8);
}
