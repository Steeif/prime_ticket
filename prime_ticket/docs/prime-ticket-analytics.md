# Prime Ticket Analytics Guide

Open **Ticket Analytics** from the Prime Ticket workspace. The page is available to **Ticket Operators** and **System Managers**. The dashboard preview in the repository README uses illustrative sample data and contains no site-specific information. For downloadable tabular analysis, see the [SQL Reports Guide](prime-ticket-sql-reports.md).

## Filter the reports

Use the **From** and **To** date fields to choose the ticket creation period, then select **Refresh**. The page loads the latest saved ticket data for that range. The open backlog and oldest-open-ticket list show the current workload, regardless of the selected creation dates.

## Reports on the page

- **Tickets received** counts tickets opened within the selected dates.
- **Open backlog** counts tickets in Open, Working in Progress, Pending, Waiting for Reply, or Reopened. The note below it shows currently overdue first responses and resolutions.
- **First response SLA** compares first replies with the response deadlines saved on each ticket. Met and missed percentages use tickets that have either received a reply or passed their response deadline. Tickets that are still within their deadline are not counted in that rate.
- **Average first response** is the average time from ticket opening to the first operator reply, for tickets opened in the selected period.
- **Incoming tickets**, **Status mix**, and **Categories** summarize tickets opened in the selected period.
- **SLA by priority** shows ticket counts, first-response performance, missed deadlines, and average response hours by priority.
- **Oldest open tickets** lists the eight oldest tickets that are still active, with direct links to their Support Ticket records.

## Data and permissions

The reports use saved Support Ticket fields: opened time, status, category, priority, first response time, and SLA deadlines. Existing records without SLA deadlines are excluded from SLA calculations. Only users with the **Ticket Operator** or **System Manager** role can open the report page or retrieve its report data.
