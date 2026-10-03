# Prime Ticket

Internal support ticketing app for Frappe/ERPNext.

Users submit tickets through a login-required web form, operators work them
through a status workflow, and email notifications keep both sides informed.

## Features

- **Support Ticket** DocType (`TICK-00001` naming) with category, priority,
  attachments, a replies thread, and resolution notes
- **Status workflow:** Open / Working in Progress / Pending / Waiting for
  Reply / Resolved / Reopened / Closed
- **Web form** at `/new-ticket` (login required) — users also get a list of
  their own past tickets
- **Roles:** `Ticket Operator` (sees and works all tickets) and `Ticket User`
  (sees only their own) — created automatically on install
- **Email notifications** (shipped as fixtures):
  - New ticket -> all Ticket Operators
  - Status -> Resolved -> email to the ticket raiser
  - Status -> Waiting for Reply -> email to the ticket raiser
  - Status -> Reopened -> all Ticket Operators
- Color-coded list view by status

## Install

On your bench (Frappe v15/v16):

```bash
cd ~/frappe-bench
bench get-app https://github.com/Steeif/prime_ticket
bench --site your-erp-domain.com install-app prime_ticket
bench --site your-erp-domain.com migrate
```

To update later:

```bash
bench update --app prime_ticket
# or: cd apps/prime_ticket && git pull && cd ../.. && bench --site your-erp-domain.com migrate
```

## Post-install setup

1. **Assign roles** (User list -> select user -> Roles):
   - Support staff -> add **Ticket Operator**
   - Regular users -> add **Ticket User** (they keep their normal roles too)
2. Make sure **email is configured** on the site (Email Account / outgoing
   SMTP), otherwise notifications queue but never send.
3. Share the form link: `https://your-erp-domain.com/new-ticket`

## DocType Structure

This app is built around a simple parent-child structure:

```mermaid
erDiagram
    SUPPORT_TICKET ||--o{ TICKET_REPLY : contains
    WEB_FORM ||--o| SUPPORT_TICKET : creates

    SUPPORT_TICKET {
        string ticket_name PK
        string subject
        string category
        string priority
        string status
        string description
        string raised_by
        string email
        datetime opened_at
        datetime resolved_at
        string resolution
    }

    TICKET_REPLY {
        string name PK
        string parent FK
        string reply
        string reply_by
        string reply_by_name
        datetime reply_on
    }

    WEB_FORM {
        string name
        string title
        string route
        string doc_type
    }
```

### Ticket lifecycle

```mermaid
flowchart TD
    A[User visits /new-ticket] -->|Login required| B[User fills web form]
    B --> C[Submit ticket]
    C --> D[Support Ticket created<br/>Status: Open]

    D --> E[Email notification sent<br/>to Ticket Operators]
    E --> F{Operator reviews ticket}

    F -->|Takes action| G[Status: Working in Progress]
    G --> H{More info needed?}

    H -->|Yes| I[Status: Pending]
    I --> J[Operator adds reply]
    J --> K[Email notification sent<br/>to User]
    K --> L[User sees reply]
    L --> M[Status: Waiting for Reply]

    M --> N{User responds?}
    N -->|Yes| O[User adds reply]
    O --> P[Status: Reopened]
    P --> G

    N -->|No / Timeout| Q[Status: Closed]

    H -->|No, resolved| R[Operator adds resolution notes]
    R --> S[Status: Resolved]
    S --> T[Email sent to User with resolution]
    T --> U{User satisfied?}

    U -->|Yes| V[Status: Closed]
    U -->|No| W[Status: Reopened]
    W --> G

    V --> X[Ticket archived]
```

## Uninstall

```bash
bench --site your-erp-domain.com remove-app prime_ticket
```

Warning: this drops the `tabSupport Ticket` and `tabTicket Reply` tables and
all ticket data with them. Export first if you need the history.

## License

MIT
