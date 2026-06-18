import { getMovies, formatDate, type Movie } from "../../lib/movies";
import { PageHeading, Table, Td, EmptyState, ErrorState } from "../components/ui";

export default async function MoviesAdminPage() {
  let page;
  try {
    page = await getMovies({ limit: 50, sort_by: "title", order: "asc" });
  } catch (e) {
    return (
      <>
        <PageHeading title="Ταινίες" />
        <ErrorState message={(e as Error).message} />
      </>
    );
  }

  return (
    <>
      <PageHeading
        title="Ταινίες"
        subtitle="Ο κατάλογος ταινιών"
        count={page.total}
      />
      {page.items.length === 0 ? (
        <EmptyState message="Δεν υπάρχουν ταινίες ακόμη." />
      ) : (
        <Table headers={["ID", "Τίτλος", "Βαθμολογία", "Κυκλοφορία"]}>
          {page.items.map((m: Movie) => (
            <tr key={m.id} className="hover:bg-foreground/[0.02]">
              <Td mono>{m.id.slice(0, 8)}</Td>
              <Td>{m.title}</Td>
              <Td>{m.rating.toFixed(1)}</Td>
              <Td>{formatDate(m.release_date)}</Td>
            </tr>
          ))}
        </Table>
      )}
    </>
  );
}
