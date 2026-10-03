import frappe


ROLES = ["Ticket Operator", "Ticket User"]


def after_install():
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
    frappe.db.commit()
