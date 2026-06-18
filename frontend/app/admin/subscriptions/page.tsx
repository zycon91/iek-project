import { formatDate } from "../../lib/movies";
import { getSubscriptions, shortId } from "../../lib/admin";
import {
  PageHeading,
  Table,
  Td,
  StatusBadge,
  EmptyState,
  ErrorState,
} from "../components/ui";

export default async function SubscriptionsAdminPage() {
  let page;
  try {
    page = await getSubscriptions(100);
  } catch (e) {
    return (
      <>
        <PageHeading title="Συνδρομές" />
        <ErrorState message={(e as Error).message} />
      </>
    );
  }

  return (
    <>
      <PageHeading
        title="Συνδρομές"
        subtitle="Όλες οι συνδρομές χρηστών"
        count={page.total}
      />
      {page.items.length === 0 ? (
        <EmptyState message="Δεν υπάρχουν συνδρομές." />
      ) : (
        <Table
          headers={["ID", "Χρήστης", "Πακέτο", "Έναρξη", "Λήξη", "Κατάσταση"]}
        >
          {page.items.map((s) => (
            <tr key={s.id} className="hover:bg-foreground/[0.02]">
              <Td mono>{shortId(s.id)}</Td>
              <Td mono>{shortId(s.user_id)}</Td>
              <Td>{s.plan}</Td>
              <Td>{formatDate(s.start_date)}</Td>
              <Td>{formatDate(s.end_date)}</Td>
              <Td>
                <StatusBadge active={s.is_active} />
              </Td>
            </tr>
          ))}
        </Table>
      )}
    </>
  );
}
