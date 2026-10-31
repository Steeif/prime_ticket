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
    """Runs on every migrate — restores missing roles, categories, and notifications."""
    create_roles()
    create_default_categories()
    create_notifications()
    frappe.db.commit()


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
