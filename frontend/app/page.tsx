import { Suspense } from "react";
import { redirect } from "next/navigation";
import { Show, RedirectToSignIn } from "@clerk/nextjs";
import { currentUser } from "@clerk/nextjs/server";
import MovieGrid from "./components/MovieGrid";
import CheckoutBanner from "./components/CheckoutBanner";

function GridSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="h-32 animate-pulse rounded-2xl border border-foreground/10 bg-foreground/[0.05]"
        />
      ))}
    </div>
  );
}

export default async function Home() {
  // Οι admins «προσγειώνονται» κατευθείαν στον Πίνακα Διαχείρισης.
  const user = await currentUser();
  if ((user?.publicMetadata as { role?: string } | undefined)?.role === "admin") {
    redirect("/admin");
  }

  return (
    <>
      <Show when="signed-in">
        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
          <Suspense fallback={null}>
            <CheckoutBanner />
          </Suspense>
          <header className="mb-8">
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              Ταινίες
            </h1>
            <p className="mt-2 text-foreground/60">
              Δημοφιλείς ταινίες ταξινομημένες κατά βαθμολογία.
            </p>
          </header>
          <Suspense fallback={<GridSkeleton />}>
            <MovieGrid />
          </Suspense>
        </main>
      </Show>
      <Show when="signed-out">
        <RedirectToSignIn />
      </Show>
    </>
  );
}
