import frappe


def get_context(context):
    context.title = "Submit a Support Ticket"
    return context


def before_submit(doc, data=None):
    pass
