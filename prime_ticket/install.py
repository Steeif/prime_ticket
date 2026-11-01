import json
from pathlib import Path

import frappe

ROLES = ["Ticket Operator", "Ticket User"]

DEFAULT_CATEGORIES = [
    {
        "name_field": "Other / Miscellaneous",
        "description": "Uncategorized support requests, special administrative tasks, or unique operational feedback.",
        "color": "#918e8e",
        "icon": "fa fa-folder",
    },
    {
        "name_field": "New Requests & Features",
        "description": "Suggestions for system enhancements, new custom reports, workflow additions, or feature requests from store staff.",
        "color": "#449CF0",
        "icon": "fa fa-lightbulb",
    },
    {
        "name_field": "General Inquiries",
        "description": "General store operations questions, staff scheduling inquiries, internal announcements, or policy clarifications.",
        "color": "#CB2929",
        "icon": "fa fa-info-circle",
    },
    {
        "name_field": "Technical Issues",
        "description": "System downtime, login failures, permission errors, synchronization delays, or application bugs.",
        "color": "#4463F0",
        "icon": "fa fa-info-circle",
    },
    {
        "name_field": "Pricing & Promotions",
        "description": "Inaccurate item prices, promotional discount applications, markdown errors, and coupon validation.",
        "color": "#761ACB",
        "icon": "fa fa-tags",
    },
    {
        "name_field": "Customer Service & Returns",
        "description": "Handling customer complaints, exchange policies, loyalty program issues, and refund processing.",
        "color": "#EC864B",
        "icon": "fa fa-undo",
    },
    {
        "name_field": "Inventory & Stock",
        "description": "Discrepancies in stock levels, barcode scanning failures, stock transfers, and warehouse adjustments.",
        "color": "#29CD42",
        "icon": "fa fa-boxes",
    },
    {
        "name_field": "Sales & POS Support",
        "description": "Issues related to daily register operations, checkout transactions, customer receipts, and point-of-sale terminal software.",
        "color": "#4463F0",
        "icon": "fa fa-cash-register",
    },
]


def after_install():
    """Runs once when the app is installed on a site."""
    create_roles()
    create_default_categories()
    create_notifications()
    frappe.db.commit()


def after_migrate():
    """Restore app-managed reports and workspace after every site migration."""
    create_roles()
    create_default_categories()
    create_notifications()
    sync_reports()
    sync_workspace()
    frappe.db.commit()
    frappe.clear_cache(doctype="Report")
    frappe.clear_cache(doctype="Workspace")


def sync_reports():
    """Apply the app's standard Query Report definitions to the site database."""
    reports_path = Path(frappe.get_app_path("prime_ticket", "prime_ticket", "report"))

    for report_file in reports_path.glob("*/*.json"):
        with report_file.open(encoding="utf-8") as source_file:
            report_data = json.load(source_file)

        if report_data.get("doctype") != "Report" or report_data.get("report_type") != "Query Report":
            continue

        report_name = report_data["name"]
        if frappe.db.exists("Report", report_name):
            report = frappe.get_doc("Report", report_name)
            for field in (
                "report_name",
                "ref_doctype",
                "report_type",
                "query",
                "filters",
                "roles",
                "add_total_row",
                "disabled",
                "prepared_report",
                "module",
                "is_standard",
            ):
                if field in report_data:
                    report.set(field, report_data[field])
            report.save(ignore_permissions=True)
        else:
            frappe.get_doc(report_data).insert(ignore_permissions=True)


def sync_workspace():
    """Refresh the app-managed workspace after standard documents have synced."""
    workspace_path = frappe.get_app_path(
        "prime_ticket", "prime_ticket", "workspace", "prime_ticket", "prime_ticket.json"
    )
    with open(workspace_path, encoding="utf-8") as workspace_file:
        workspace_data = json.load(workspace_file)

    if frappe.db.exists("Workspace", "Prime Ticket"):
        workspace = frappe.get_doc("Workspace", "Prime Ticket")
    else:
        workspace = frappe.get_doc(workspace_data)

    for field in ("content", "links", "shortcuts", "quick_lists", "charts"):
        workspace.set(field, workspace_data.get(field, []))
    workspace.save(ignore_permissions=True)


def create_roles():
    """Create the custom roles used by the ticketing workflow."""
    for role_name in ROLES:
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1,
            })
            role.insert(ignore_permissions=True)
            frappe.logger().info(f"prime_ticket: created role {role_name}")


def create_notifications():
    """Create custom notifications for ticket workflows (idempotent)."""
    notifications = [
        {
            "doctype": "Notification",
            "name": "New Support Ticket - Notify Operators",
            "channel": "Email",
            "event": "New",
            "document_type": "Support Ticket",
            "enabled": 1,
            "is_standard": 0,
            "message": "<p>A new support ticket has been submitted.</p><p><b>Ticket:</b> {{ doc.name }}<br><b>Subject:</b> {{ doc.subject }}<br><b>Category:</b> {{ doc.category }}<br><b>Priority:</b> {{ doc.priority }}<br><b>Raised by:</b> {{ doc.raised_by }}</p><p>Open the ticket in the desk to respond.</p>",
            "subject": "New support ticket: {{ doc.subject }}",
            "send_system_notification": 1,
            "recipients": [{"receiver_by_role": "Ticket Operator", "doctype": "Notification Recipient"}],
        },
        {
            "doctype": "Notification",
            "name": "Ticket Resolved - Notify Raiser",
            "channel": "Email",
            "event": "Value Change",
            "document_type": "Support Ticket",
            "enabled": 1,
            "is_standard": 0,
            "condition": "doc.status == 'Resolved'",
            "value_changed": "status",
            "message": "<p>Hello,</p><p>Your support ticket <b>{{ doc.name }} - {{ doc.subject }}</b> has been marked as <b>Resolved</b>.</p>{% if doc.resolution %}<p><b>Resolution:</b><br>{{ doc.resolution }}</p>{% endif %}<p>If your issue is not solved, you can reopen the ticket or reply to this email.</p>",
            "subject": "Resolved: {{ doc.name }} - {{ doc.subject }}",
            "send_system_notification": 1,
            "recipients": [{"receiver_by_document_field": "email", "doctype": "Notification Recipient"}],
        },
        {
            "doctype": "Notification",
            "name": "Ticket Waiting for Reply - Notify Raiser",
            "channel": "Email",
            "event": "Value Change",
            "document_type": "Support Ticket",
            "enabled": 1,
            "is_standard": 0,
            "condition": "doc.status == 'Waiting for Reply'",
            "value_changed": "status",
            "message": "<p>Hello,</p><p>Your support ticket <b>{{ doc.name }} - {{ doc.subject }}</b> is waiting for your reply. Please log in and add a response so our team can continue working on it.</p>",
            "subject": "Action needed: {{ doc.name }} - {{ doc.subject }}",
            "send_system_notification": 1,
            "recipients": [{"receiver_by_document_field": "email", "doctype": "Notification Recipient"}],
        },
        {
            "doctype": "Notification",
            "name": "Ticket Reopened - Notify Operators",
            "channel": "Email",
            "event": "Value Change",
            "document_type": "Support Ticket",
            "enabled": 1,
            "is_standard": 0,
            "condition": "doc.status == 'Reopened'",
            "value_changed": "status",
            "message": "<p>Ticket <b>{{ doc.name }} - {{ doc.subject }}</b> has been reopened by the requester and needs attention again.</p><p><b>Raised by:</b> {{ doc.raised_by }}<br><b>Priority:</b> {{ doc.priority }}</p><p>Please review and continue working on this ticket.</p>",
            "subject": "Reopened ticket: {{ doc.name }} - {{ doc.subject }}",
            "send_system_notification": 1,
            "recipients": [{"receiver_by_role": "Ticket Operator", "doctype": "Notification Recipient"}],
        },
    ]

    for notification in notifications:
        if not frappe.db.exists("Notification", notification["name"]):
            doc = frappe.get_doc(notification)
            doc.insert(ignore_permissions=True)
            frappe.logger().info(f"prime_ticket: created notification {notification['name']}")


def create_default_categories():
    """Add the built-in categories when missing; leave existing records untouched."""
    for category in DEFAULT_CATEGORIES:
        category_name = category["name_field"]
        if frappe.db.exists("Prime Ticket Category", category_name):
            continue

        doc = frappe.get_doc({
            "doctype": "Prime Ticket Category",
            **category,
            "is_active": 1,
        })
        doc.insert(ignore_permissions=True)
        frappe.logger().info(f"prime_ticket: created default category {category_name}")
