# Copyright (c) 2026, Ahmed Mostafa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PrimeTicketOperator(Document):
    def before_naming(self):
        if not self.user:
            frappe.throw(_("Select a Frappe user before creating an operator."))

        user_details = frappe.db.get_value(
            "User", self.user, ["full_name", "email"], as_dict=True
        )
        if not user_details or not user_details.full_name:
            frappe.throw(_("The selected user must have a full name."))

        operator_name = user_details.full_name.strip()
        existing = frappe.db.get_value(
            "Prime Ticket Operator", {"full_name": operator_name}, "name"
        )
        if existing:
            frappe.throw(
                _("An operator named {0} already exists. Operator names must be unique.").format(
                    frappe.bold(operator_name)
                )
            )

        self.full_name = operator_name
        self.email = user_details.email
