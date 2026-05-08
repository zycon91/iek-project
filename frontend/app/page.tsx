import { Show } from "@clerk/nextjs";
import { RedirectToSignIn } from "@clerk/nextjs";

export default function Home() {
  return (
    <>
      <Show when="signed-in">
        <main className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            Καλώς ήρθες!
          </h1>
          <p className="max-w-xl text-foreground/60">
            Εξερεύνησε ταινίες και σειρές από το μενού πιο πάνω.
          </p>
        </main>
      </Show>
      <Show when="signed-out">
        <RedirectToSignIn />
      </Show>
    </>
  );
}
