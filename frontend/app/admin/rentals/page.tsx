import { formatDate } from "../../lib/movies";
import { getRentals, shortId } from "../../lib/admin";
import { PageHeading, Table, Td, EmptyState, ErrorState } from "../components/ui";

export default async function RentalsAdminPage() {
  let page;
  try {
    page = await getRentals(50);
  } catch (e) {
    return (
      <>
        <PageHeading title="Ενοικιάσεις" />
        <ErrorState message={(e as Error).message} />
      </>
    );
  }

  return (
    <>
      <PageHeading
        title="Ενοικιάσεις"
        subtitle="Όλες οι ενοικιάσεις ταινιών"
        count={page.total}
      />
      {page.items.length === 0 ? (
        <EmptyState message="Δεν υπάρχουν ενοικιάσεις." />
      ) : (
        <Table headers={["ID", "Χρήστης", "Ταινία", "Έναρξη", "Λήξη"]}>
          {page.items.map((r) => (
            <tr key={r.id} className="hover:bg-foreground/[0.02]">
              <Td mono>{shortId(r.id)}</Td>
              <Td mono>{shortId(r.user_id)}</Td>
              <Td mono>{shortId(r.movie_id)}</Td>
              <Td>{formatDate(r.start_date)}</Td>
              <Td>{formatDate(r.end_date)}</Td>
            </tr>
          ))}
        </Table>
      )}
    </>
  );
}
