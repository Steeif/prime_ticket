# Copyright (c) 2026, Ahmed Mostafa and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PrimeTicketCategory(Document):
    def before_naming(self):
        if not self.name_field:
            frappe.throw(_("Enter a category name before creating the category."))

        self.name_field = self.name_field.strip()
        self.name = self.name_field
