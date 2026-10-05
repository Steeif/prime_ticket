# Prime Ticket Settings Guide

Open **Prime Ticket Settings** from the Prime Ticket workspace. The guide is also available in the app at `/prime-ticket-settings-guide`.

## Before you start

Settings is a single-document form for site-wide Prime Ticket configuration. You need the **System Manager** role to edit it. Save the form after making changes.

> **Current implementation note:** the settings fields below are present in the form, but most are not read by the app's current ticket-handling code. In particular, assignment, SLA timers, custom workflow, automatic close/escalation, the notification switches, API token, webhook, and custom JSON fields do not currently change runtime behavior. Treat these as stored configuration fields, not active features. The configured Application Logo is displayed on the Submit a Ticket form and this guide. Ticket emails currently come from Frappe Notification records created by the app's install/migrate routine.

## General Settings

| Setting | What it is for | Current behavior |
| --- | --- | --- |
| Application Name | A branding label for the Prime Ticket app. | Stored in settings; not currently applied to the UI. |
| Application Logo | An uploaded image used as the app's brand mark. | Displayed on the Submit a Ticket web form and Settings Guide page when configured. |
| Enable Auto-Assignment of Tickets | Master switch intended to enable automatic ticket assignment. | No automatic assignment code currently reads this switch. |
| Auto-Assignment Method | Intended selection: Round Robin, Least Busy, Same Category, or Random. | Only shown when auto-assignment is enabled; no method is currently applied. |
| Enable Email Notifications | Intended master switch for ticket email notifications. | Does not enable or disable the Notification records created by the app. Manage those under Frappe **Notification**. |
| Enable SLA Tracking | Intended switch for SLA monitoring. | Does not start SLA timers or calculate ticket deadlines. |
| Default SLA Response Time (Hours) | Intended fallback response target; defaults to 24 hours. | Stored only; SLA policy rows and this value are not currently enforced. |

## Operators Management

| Setting | What it is for | Current behavior |
| --- | --- | --- |
| Support Operators | A child table selecting Prime Ticket Operator records. | Stores selected operators in settings; it does not assign tickets or grant roles. Assign **Ticket Operator** to users separately in Frappe **User**. |

The **Prime Ticket Operator** DocType stores a linked User, contact details, active flag, supported categories, capacity, skill, working hours, timezone, availability, and capability flags. The present ticket controller does not use these values to route work or enforce capabilities.

## Workflow Configuration

| Setting | What it is for | Current behavior |
| --- | --- | --- |
| Enable Custom Workflow | Intended switch for using custom status definitions. | Does not change the Support Ticket status options or validate transitions. |
| Custom Workflow Statuses | Child rows with status name, description, color, and sequence. | Stored only. Support Ticket currently uses its fixed status list: Open, Working in Progress, Pending, Waiting for Reply, Resolved, Reopened, and Closed. |
| Auto-Close Resolved Tickets (Days) | Intended delay before closing a resolved ticket; defaults to 7 days. | No scheduled auto-close job currently reads this value. |
| Auto-Escalate Unresponded Tickets (Days) | Intended delay before escalation; defaults to 3 days. | No scheduled escalation job currently reads this value. |

## Ticket Categories

**Categories** selects Prime Ticket Category records in a settings child table. Prime Ticket Category stores a name, description, color, icon class, and active flag. The customer web form currently has its own fixed category choices (Question, Bug Report, Feature Request, How-To, Other); the settings selection does not currently populate those choices.

## SLA Policies

Each **SLA Policy** child row stores a priority name, response-time target in hours, resolution-time target in hours, and optional color. Policies belong inside Prime Ticket Settings because this is a child table; do not open the SLA Policy DocType as a standalone list. The current app does not compare ticket age with these targets or issue SLA breach alerts.

## Notification Settings

| Setting | What it is for | Current behavior |
| --- | --- | --- |
| Notify Operators on New Ticket | Intended control for new-ticket alerts. | App-created Notification records currently notify the Ticket Operator role regardless of this switch. |
| Notify Customer on Status Change | Intended control for customer status emails. | App-created notifications currently send for Resolved and Waiting for Reply status changes regardless of this switch. |
| Notify Operator on Assignment | Intended assignment alert. | No assignment notification behavior is currently implemented. |
| Custom Email Template | Selects an Email Template. | Stored only; the app-created notifications do not currently use this field. |

Frappe must have an outgoing email account configured for email delivery. Existing app notifications are listed in Frappe **Notification**.

## Escalation Rules

| Setting | What it is for | Current behavior |
| --- | --- | --- |
| Enable Escalation | Intended master switch for escalation. | No escalation worker currently reads this switch. |
| Escalation Levels | Child rows define a level, description, wait in days, and optional role to notify. | Stored only; no scheduled escalation process currently uses these rows. |

## Integrations

| Setting | What it is for | Current behavior |
| --- | --- | --- |
| Enable External API Access | Intended switch for integration access. | Does not create an endpoint or change Frappe authentication. |
| API Token | Password-type field intended for a token. | Prime Ticket has no endpoint that reads or validates this field. For API access, use Frappe's API authentication and the permissions of the Frappe user. Do not paste a production secret here expecting it to activate API access. |
| Webhook URL | Intended destination for outbound events. | No code currently sends events to this URL. |

## Advanced Settings

| Setting | What it is for | Current behavior |
| --- | --- | --- |
| Custom Fields (JSON) | Intended JSON configuration for extra ticket fields. | Stored as code text; not currently parsed or applied. |
| Custom Business Rules (JSON) | Intended JSON configuration for custom rules. | Stored as code text; not currently parsed or applied. |
| Allow Customers to Reassign Tickets | Intended permission switch. | Does not currently change Support Ticket permissions or expose reassignment. |

## What works today

- Frappe user roles and DocType permissions govern ticket access.
- Support Ticket records the current user as the raiser and captures that user's email when available.
- The app creates Frappe notifications for new tickets, tickets marked Resolved, tickets marked Waiting for Reply, and tickets marked Reopened.
- Support Ticket's status choices are fixed in its DocType. The app tracks `resolved_at` when a ticket is marked Resolved and clears it when the ticket returns to an active status.

To change active notification behavior, use Frappe **Notification**. To change the ticket form's category choices or status list, update the corresponding Support Ticket DocType definition and migrate the site.

