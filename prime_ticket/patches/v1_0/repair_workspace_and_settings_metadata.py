"""Repair the standard workspace and register its settings child DocTypes."""

import json

import frappe


def execute():
    # Older installations may have missed the child DocType during an earlier
    # sync. Reload its controller metadata before loading the Single settings
    # DocType that references it.
    frappe.reload_doc("prime_ticket", "doctype", "prime_ticket_sla_policy", force=True)
    frappe.reload_doc("prime_ticket", "doctype", "prime_ticket_settings_category", force=True)
    frappe.reload_doc("prime_ticket", "doctype", "prime_ticket_settings_operator", force=True)
    frappe.reload_doc("prime_ticket", "doctype", "prime_ticket_settings", force=True)

    settings_meta = frappe.get_meta("Prime Ticket Settings", cached=False)
    if not settings_meta.issingle:
        frappe.throw("Prime Ticket Settings must remain a Single DocType")
    if not frappe.db.exists("DocType", "Prime Ticket SLA Policy"):
        frappe.throw("Prime Ticket SLA Policy metadata could not be registered")
    if not frappe.db.exists("DocType", "Prime Ticket Settings Operator"):
        frappe.throw("Prime Ticket Settings Operator metadata could not be registered")
    if not frappe.db.exists("DocType", "Prime Ticket Settings Category"):
        frappe.throw("Prime Ticket Settings Category metadata could not be registered")

    workspace_path = frappe.get_app_path(
        "prime_ticket", "prime_ticket", "workspace", "prime_ticket", "prime_ticket.json"
    )
    with open(workspace_path, encoding="utf-8") as workspace_file:
        workspace_data = json.load(workspace_file)

    if frappe.db.exists("Workspace", "Prime Ticket"):
        workspace = frappe.get_doc("Workspace", "Prime Ticket")
    else:
        workspace = frappe.get_doc(workspace_data)

    # Keep the existing Workspace document and its identity while repairing
    # the app-owned navigation and layout fields from the standard definition.
    for field in ("content", "links", "shortcuts", "quick_lists", "charts"):
        workspace.set(field, workspace_data.get(field, []))
    workspace.save(ignore_permissions=True)
