app_name = "prime_ticket"
app_title = "Prime Ticket"
app_publisher = "Ahmed Mostafa"
app_description = "Internal support ticketing app for ERPNext: login-required web form intake, operator workflow, and status-based email notifications."
app_email = ""
app_license = "MIT"

required_apps = ["frappe"]

after_install = "prime_ticket.install.after_install"

fixtures = [
    {"dt": "Notification", "filters": [["module", "=", "Prime Ticket"]]},
    {"dt": "Workspace", "filters": [["module", "=", "Prime Ticket"]]},
]
