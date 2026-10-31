# Copyright (c) 2026, Ahmed Mostafa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime


class SupportTicket(Document):
    def _get_matching_sla_policy(self, settings):
        priority = (self.priority or "").strip().casefold()
        for policy in settings.sla_policies or []:
            if (policy.priority or "").strip().casefold() == priority:
                return policy
        return None

    def _get_hours(self, value):
        try:
            return max(int(value), 0)
        except (TypeError, ValueError):
            return None

    def validate(self):
        # Stamp the creator / contact email (web form doesn't send these fields)
        if not self.raised_by:
            self.raised_by = frappe.session.user
        if not self.email and self.raised_by:
            self.email = frappe.db.get_value("User", self.raised_by, "email")

        if not self.opened_at:
            self.opened_at = now_datetime()

        settings = frappe.get_single("Prime Ticket Settings")
        if settings.enable_sla and self.opened_at:
            policy = self._get_matching_sla_policy(settings)

            # Keep the first-response deadline stable once it has been set.
            if not self.response_due_at:
                response_hours = self._get_hours(
                    policy.response_time_hours if policy else None
                )
                if response_hours is None:
                    response_hours = self._get_hours(settings.default_sla_hours)
                if response_hours is not None:
                    self.response_due_at = add_to_date(self.opened_at, hours=response_hours)

            # Resolution targets have no global fallback, so use a matching policy only.
            if not self.resolution_due_at and policy:
                resolution_hours = self._get_hours(policy.resolution_time_hours)
                if resolution_hours is not None:
                    self.resolution_due_at = add_to_date(self.opened_at, hours=resolution_hours)

        # Track resolution timestamp
        if self.status == "Resolved" and not self.resolved_at:
            self.resolved_at = now_datetime()
        if self.status in ("Open", "Working in Progress", "Pending", "Waiting for Reply", "Reopened"):
            self.resolved_at = None

        # Stamp new replies and record the first reply from an operator.
        for row in self.replies or []:
            if not row.is_new():
                continue
            if not row.reply_by:
                row.reply_by = frappe.session.user
            if not row.reply_by_name:
                row.reply_by_name = frappe.db.get_value("User", row.reply_by, "full_name")
            if not row.reply_on:
                row.reply_on = now_datetime()

            if not self.first_response_at and {"Ticket Operator", "System Manager"}.intersection(
                frappe.get_roles(row.reply_by)
            ):
                self.first_response_at = row.reply_on
