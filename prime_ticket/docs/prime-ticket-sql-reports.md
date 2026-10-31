# Prime Ticket SQL Reports

The **Prime Ticket** workspace provides three standard SQL Query Reports. Open a report from the workspace shortcut or from **Reports** in the Desk. All reports are available to users with the **Ticket Operator** or **System Manager** role.

## Ticket Volume by Category

Groups created tickets by category, status, and priority. It includes the ticket count, average first-response time in hours for tickets that have a first reply, and the first and latest opened dates in each group.

Filters: **From Date**, **To Date**, **Status**, and **Priority**. The date range includes both selected dates.

## First Response SLA by Priority

Summarizes tickets that have a saved first-response deadline, grouped by priority. It shows total SLA-tracked tickets, responses made on time, missed deadlines, tickets still awaiting a response, on-time rate, and average first-response time in hours.

Filters: **From Date**, **To Date**, and **Priority**. The on-time rate is calculated from tickets that have either met or missed the response deadline; tickets still within the deadline are excluded from the rate. Tickets without a saved response deadline are excluded.

## Open Ticket Aging

Lists active tickets from oldest to newest, including the age in hours, saved response and resolution deadlines, and first-response SLA state.

Filters: **Status**, **Priority**, **Opened From**, and **Opened To**. Resolved and closed tickets are excluded.

## Notes

- Query report dates filter on the ticket's **Opened At** timestamp.
- SLA results depend on the deadlines and response timestamps saved on each Support Ticket. Existing tickets without those values may be excluded from SLA metrics.
- The reports are read-only and do not update ticket records.
- The custom **Ticket Analytics** page is a separate visual summary; see the [Analytics Guide](prime-ticket-analytics.md).
