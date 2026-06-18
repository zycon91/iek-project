import { getUsers, shortId } from "../../lib/admin";
import { PageHeading, Table, Td, EmptyState, ErrorState } from "../components/ui";

export default async function UsersAdminPage() {
  let page;
  try {
    page = await getUsers(100);
  } catch (e) {
    return (
      <>
        <PageHeading title="Χρήστες" />
        <ErrorState message={(e as Error).message} />
      </>
    );
  }

  return (
    <>
      <PageHeading
        title="Χρήστες"
        subtitle="Όλοι οι εγγεγραμμένοι χρήστες"
        count={page.total}
      />
      {page.items.length === 0 ? (
        <EmptyState message="Δεν υπάρχουν χρήστες." />
      ) : (
        <Table headers={["ID", "Username", "Ονοματεπώνυμο", "Email"]}>
          {page.items.map((u) => (
            <tr key={u.id} className="hover:bg-foreground/[0.02]">
              <Td mono>{shortId(u.id)}</Td>
              <Td>{u.username}</Td>
              <Td>{u.fullname}</Td>
              <Td mono>{u.email}</Td>
            </tr>
          ))}
        </Table>
      )}
    </>
  );
}
