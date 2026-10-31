# Copyright (c) 2026, Ahmed Mostafa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime


class SupportTicket(Document):
    def _get_response_sla_hours(self):
        settings = frappe.get_single("Prime Ticket Settings")
        if not settings.enable_sla:
            return None

        for policy in settings.sla_policies or []:
            if (policy.priority or "").strip().casefold() == (self.priority or "").strip().casefold():
                return int(policy.response_time_hours)

        if settings.default_sla_hours:
            return int(settings.default_sla_hours)
        return None

    def validate(self):
        # Stamp the creator / contact email (web form doesn't send these fields)
        if not self.raised_by:
            self.raised_by = frappe.session.user
        if not self.email and self.raised_by:
            self.email = frappe.db.get_value("User", self.raised_by, "email")

        if not self.opened_at:
            self.opened_at = now_datetime()

        # Calculate the first-response deadline once when SLA tracking is enabled.
        if not self.response_due_at and self.opened_at:
            response_hours = self._get_response_sla_hours()
            if response_hours is not None:
                self.response_due_at = add_to_date(self.opened_at, hours=response_hours)

        # Track resolution timestamp
        if self.status == "Resolved" and not self.resolved_at:
            self.resolved_at = now_datetime()
        if self.status in ("Open", "Working in Progress", "Pending", "Waiting for Reply", "Reopened"):
            self.resolved_at = None

        # Stamp any new replies with author + time
        for row in self.replies or []:
            if row.is_new() and not row.reply_by:
                row.reply_by = frappe.session.user
                row.reply_by_name = frappe.db.get_value("User", frappe.session.user, "full_name")
                row.reply_on = now_datetime()
