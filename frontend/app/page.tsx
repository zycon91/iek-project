import { Show } from "@clerk/nextjs";
import { RedirectToSignIn } from "@clerk/nextjs";

export default function Home() {
  return (
    <>
      <Show when="signed-in">
        <div className="flex flex-1 items-center justify-center">
          <p>Καλώς ήρθες!</p>
        </div>
      </Show>
      <Show when="signed-out">
        <RedirectToSignIn />
      </Show>
    </>
  );
}
