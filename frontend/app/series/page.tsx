import { Show, RedirectToSignIn } from "@clerk/nextjs";

export default function SeriesPage() {
  return (
    <>
      <Show when="signed-in">
        <main className="flex flex-1 flex-col items-center justify-center gap-4 p-8">
          <h1 className="text-3xl font-semibold">Σειρές</h1>
          <p className="text-foreground/60">Σύντομα κοντά σας.</p>
        </main>
      </Show>
      <Show when="signed-out">
        <RedirectToSignIn />
      </Show>
    </>
  );
}
