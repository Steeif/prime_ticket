"""Shared helpers for Prime Ticket website pages."""

import frappe


def get_app_logo():
    """Return the configured app logo, if settings metadata is available."""
    if not frappe.db.exists("DocType", "Prime Ticket Settings"):
        return None
    return frappe.db.get_single_value("Prime Ticket Settings", "app_logo")

