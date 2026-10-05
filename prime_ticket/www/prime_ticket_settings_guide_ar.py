from prime_ticket.utils import get_app_logo


def get_context(context):
    context.title = "دليل إعدادات برايم تكت"
    context.app_logo = get_app_logo()
    return context

