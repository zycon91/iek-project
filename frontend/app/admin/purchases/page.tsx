import { formatDate, formatPrice } from "../../lib/movies";
import { getPurchases, shortId } from "../../lib/admin";
import { PageHeading, Table, Td, EmptyState, ErrorState } from "../components/ui";

export default async function PurchasesAdminPage() {
  let page;
  try {
    page = await getPurchases(50);
  } catch (e) {
    return (
      <>
        <PageHeading title="Αγορές" />
        <ErrorState message={(e as Error).message} />
      </>
    );
  }

  return (
    <>
      <PageHeading
        title="Αγορές"
        subtitle="Όλες οι μόνιμες αγορές ταινιών"
        count={page.total}
      />
      {page.items.length === 0 ? (
        <EmptyState message="Δεν υπάρχουν αγορές." />
      ) : (
        <Table headers={["ID", "Χρήστης", "Ταινία", "Ποσό", "Ημ/νία"]}>
          {page.items.map((p) => (
            <tr key={p.id} className="hover:bg-foreground/[0.02]">
              <Td mono>{shortId(p.id)}</Td>
              <Td mono>{shortId(p.user_id)}</Td>
              <Td mono>{shortId(p.movie_id)}</Td>
              <Td>{formatPrice(p.amount_paid)}</Td>
              <Td>{formatDate(p.purchased_at)}</Td>
            </tr>
          ))}
        </Table>
      )}
    </>
  );
}
