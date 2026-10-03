import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class SupportTicket(Document):
    def validate(self):
        # Stamp the creator / email for desk-created tickets
        if not self.raised_by:
            self.raised_by = frappe.session.user
        if not self.email and self.raised_by:
            self.email = frappe.db.get_value("User", self.raised_by, "email")

        if not self.opened_at:
            self.opened_at = now_datetime()

        # Track resolution timestamp
        if self.status == "Resolved" and not self.resolved_at:
            self.resolved_at = now_datetime()
        if self.status in ("Reopened", "Open", "Working in Progress", "Pending", "Waiting for Reply"):
            self.resolved_at = None

        # Stamp any new replies with author + time
        for row in self.replies or []:
            if row.is_new() and not row.reply_by:
                row.reply_by = frappe.session.user
                row.reply_by_name = frappe.db.get_value("User", frappe.session.user, "full_name")
                row.reply_on = now_datetime()

    def has_permission(doc, ptype="read", user=None):
        """Ticket Users can only see their own tickets; operators see all."""
        user = user or frappe.session.user
        if "System Manager" in frappe.get_roles(user) or "Ticket Operator" in frappe.get_roles(user):
            return True
        return doc.raised_by == user
