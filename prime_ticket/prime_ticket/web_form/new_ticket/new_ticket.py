import frappe
from prime_ticket.utils import get_app_logo


def get_context(context):
    context.title = "Submit a Support Ticket"
    # The standard Web Form template renders this as its banner image.
    context.banner_image = get_app_logo()
    return context


def before_submit(doc, data=None):
    pass

