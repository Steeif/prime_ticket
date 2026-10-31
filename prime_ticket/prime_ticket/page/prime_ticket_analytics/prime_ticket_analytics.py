import frappe
from frappe.utils import add_days, getdate, now_datetime, today


OPEN_STATUSES = ["Open", "Working in Progress", "Pending", "Waiting for Reply", "Reopened"]


@frappe.whitelist()
def get_report_data(from_date=None, to_date=None):
    """Return permission-gated support ticket metrics for the analytics page."""
    frappe.only_for(["System Manager", "Ticket Operator"])

    from_date = getdate(from_date) if from_date else getdate(add_days(today(), -29))
    to_date = getdate(to_date) if to_date else getdate(today())
    if from_date > to_date:
        frappe.throw("The start date must be on or before the end date.")

    params = {"from_date": from_date, "to_date": to_date}
    date_filter = "opened_at >= %(from_date)s AND opened_at < DATE_ADD(%(to_date)s, INTERVAL 1 DAY)"

    period = frappe.db.sql(
        f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS completed,
            SUM(CASE WHEN response_due_at IS NOT NULL THEN 1 ELSE 0 END) AS response_eligible,
            SUM(CASE WHEN response_due_at IS NOT NULL
                AND first_response_at IS NOT NULL
                AND first_response_at <= response_due_at THEN 1 ELSE 0 END) AS response_met,
            SUM(CASE WHEN response_due_at IS NOT NULL
                AND (first_response_at > response_due_at
                    OR (first_response_at IS NULL AND response_due_at < NOW()))
                THEN 1 ELSE 0 END) AS response_breached,
            AVG(CASE WHEN first_response_at IS NOT NULL
                THEN TIMESTAMPDIFF(SECOND, opened_at, first_response_at) / 3600.0
                ELSE NULL END) AS avg_response_hours
        FROM `tabSupport Ticket`
        WHERE {date_filter}
        """,
        params,
        as_dict=True,
    )[0]

    backlog = frappe.db.sql(
        """
        SELECT
            SUM(CASE WHEN status IN ('Open', 'Working in Progress', 'Pending', 'Waiting for Reply', 'Reopened')
                THEN 1 ELSE 0 END) AS open_count,
            SUM(CASE WHEN status IN ('Open', 'Working in Progress', 'Pending', 'Waiting for Reply', 'Reopened')
                AND response_due_at IS NOT NULL AND first_response_at IS NULL AND response_due_at < NOW()
                THEN 1 ELSE 0 END) AS response_overdue,
            SUM(CASE WHEN status IN ('Open', 'Working in Progress', 'Pending', 'Waiting for Reply', 'Reopened')
                AND resolution_due_at IS NOT NULL AND resolution_due_at < NOW()
                THEN 1 ELSE 0 END) AS resolution_overdue
        FROM `tabSupport Ticket`
        """,
        as_dict=True,
    )[0]

    trend = frappe.db.sql(
        f"""
        SELECT DATE(opened_at) AS label, COUNT(*) AS value
        FROM `tabSupport Ticket`
        WHERE {date_filter}
        GROUP BY DATE(opened_at)
        ORDER BY DATE(opened_at)
        """,
        params,
        as_dict=True,
    )

    statuses = frappe.db.sql(
        f"""
        SELECT status AS label, COUNT(*) AS value
        FROM `tabSupport Ticket`
        WHERE {date_filter}
        GROUP BY status
        ORDER BY value DESC, label
        """,
        params,
        as_dict=True,
    )

    categories = frappe.db.sql(
        f"""
        SELECT COALESCE(NULLIF(category, ''), 'Uncategorized') AS label, COUNT(*) AS value
        FROM `tabSupport Ticket`
        WHERE {date_filter}
        GROUP BY COALESCE(NULLIF(category, ''), 'Uncategorized')
        ORDER BY value DESC, label
        """,
        params,
        as_dict=True,
    )

    priorities = frappe.db.sql(
        f"""
        SELECT COALESCE(NULLIF(priority, ''), 'Unspecified') AS priority,
            COUNT(*) AS total,
            SUM(CASE WHEN response_due_at IS NOT NULL
                AND first_response_at IS NOT NULL
                AND first_response_at <= response_due_at THEN 1 ELSE 0 END) AS met,
            SUM(CASE WHEN response_due_at IS NOT NULL
                AND (first_response_at > response_due_at
                    OR (first_response_at IS NULL AND response_due_at < NOW()))
                THEN 1 ELSE 0 END) AS breached,
            AVG(CASE WHEN first_response_at IS NOT NULL
                THEN TIMESTAMPDIFF(SECOND, opened_at, first_response_at) / 3600.0
                ELSE NULL END) AS avg_response_hours
        FROM `tabSupport Ticket`
        WHERE {date_filter}
        GROUP BY COALESCE(NULLIF(priority, ''), 'Unspecified')
        ORDER BY FIELD(priority, 'Urgent', 'High', 'Medium', 'Low'), priority
        """,
        params,
        as_dict=True,
    )

    oldest = frappe.get_list(
        "Support Ticket",
        filters={"status": ["in", OPEN_STATUSES]},
        fields=["name", "subject", "status", "priority", "category", "opened_at"],
        order_by="opened_at asc",
        page_length=8,
    )

    return {
        "from_date": str(from_date),
        "to_date": str(to_date),
        "generated_at": str(now_datetime()),
        "period": period,
        "backlog": backlog,
        "trend": [{"label": str(row.label), "value": row.value} for row in trend],
        "statuses": statuses,
        "categories": categories,
        "priorities": priorities,
        "oldest": oldest,
    }
