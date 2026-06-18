import { redirect } from "next/navigation";
import Link from "next/link";
import { currentUser } from "@clerk/nextjs/server";
import { RedirectToSignIn, UserButton } from "@clerk/nextjs";

import AdminSidebar from "./components/AdminSidebar";

// Server component gate:
//  - signed out            -> RedirectToSignIn
//  - signed in, όχι admin  -> redirect στην αρχική
//  - admin                 -> δείχνει sidebar + περιεχόμενο
// Ο ρόλος διαβάζεται από το Clerk publicMetadata.role (δες admin_panel.md §3.9).
export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await currentUser();

  if (!user) {
    return <RedirectToSignIn />;
  }

  const role = (user.publicMetadata as { role?: string })?.role;
  if (role !== "admin") {
    redirect("/");
  }

  return (
    <div className="flex min-h-screen w-full">
      <AdminSidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-foreground/10 px-6 py-3">
          <span className="text-sm text-foreground/50">Πίνακας Διαχείρισης</span>
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-sm text-foreground/60 transition-colors hover:text-foreground"
            >
              ← Στο site
            </Link>
            <UserButton />
          </div>
        </header>
        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
          {children}
        </main>
      </div>
    </div>
  );
}
