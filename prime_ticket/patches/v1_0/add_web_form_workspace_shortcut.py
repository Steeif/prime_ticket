"""Add the customer-facing ticket form to the existing Prime Ticket workspace."""

import json

import frappe


def execute():
    workspace_path = frappe.get_app_path(
        "prime_ticket", "prime_ticket", "workspace", "prime_ticket", "prime_ticket.json"
    )
    with open(workspace_path, encoding="utf-8") as workspace_file:
        workspace_data = json.load(workspace_file)

    if frappe.db.exists("Workspace", "Prime Ticket"):
        workspace = frappe.get_doc("Workspace", "Prime Ticket")
    else:
        workspace = frappe.get_doc(workspace_data)

    # Update the app-owned layout and links without replacing the Workspace.
    for field in ("content", "links", "shortcuts", "quick_lists", "charts"):
        workspace.set(field, workspace_data.get(field, []))
    workspace.save(ignore_permissions=True)
