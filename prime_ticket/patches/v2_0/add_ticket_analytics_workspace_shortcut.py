"""Add the analytics shortcut to the existing Prime Ticket workspace."""

import json

import frappe


def execute():
    workspace_path = frappe.get_app_path(
        "prime_ticket", "prime_ticket", "workspace", "prime_ticket", "prime_ticket.json"
    )
    with open(workspace_path, encoding="utf-8") as workspace_file:
        workspace_data = json.load(workspace_file)

    # This patch runs before standard Report documents are synced.
    workspace_data["links"] = [
        link for link in workspace_data.get("links", [])
        if link.get("link_type") != "Report" or frappe.db.exists("Report", link.get("link_to"))
    ]

    if frappe.db.exists("Workspace", "Prime Ticket"):
        workspace = frappe.get_doc("Workspace", "Prime Ticket")
    else:
        workspace = frappe.get_doc(workspace_data)

    for field in ("content", "links", "shortcuts", "quick_lists", "charts"):
        workspace.set(field, workspace_data.get(field, []))
    workspace.save(ignore_permissions=True)
