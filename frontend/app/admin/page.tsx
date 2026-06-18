import { getMovies } from "../lib/movies";
import { getUsers, getRentals, getPurchases, getSubscriptions } from "../lib/admin";
import { PageHeading, StatCard } from "./components/ui";

// Dashboard: φέρνει μόνο το πλήθος (limit=1) κάθε resource και δείχνει κάρτες.
export default async function AdminDashboard() {
  const results = await Promise.allSettled([
    getMovies({ limit: 1 }),
    getUsers(1),
    getRentals(1),
    getPurchases(1),
    getSubscriptions(1),
  ]);

  const total = (i: number): number | string => {
    const r = results[i];
    return r.status === "fulfilled" ? (r.value as { total: number }).total : "—";
  };

  return (
    <>
      <PageHeading
        title="Καλώς ήρθες στον Πίνακα Διαχείρισης"
        subtitle="Σύνοψη του καταλόγου — πάτησε μια κάρτα για λεπτομέρειες."
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard label="Ταινίες" value={total(0)} href="/admin/movies" />
        <StatCard label="Χρήστες" value={total(1)} href="/admin/users" />
        <StatCard label="Ενοικιάσεις" value={total(2)} href="/admin/rentals" />
        <StatCard label="Αγορές" value={total(3)} href="/admin/purchases" />
        <StatCard label="Συνδρομές" value={total(4)} href="/admin/subscriptions" />
      </div>
    </>
  );
}
