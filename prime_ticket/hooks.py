app_name = "prime_ticket"
app_title = "Prime Ticket"
app_publisher = "Ahmed Mostafa"
app_description = "Internal support ticketing app for ERPNext: login-required web form intake, operator workflow, and status-based email notifications."
app_email = ""
app_license = "MIT"

required_apps = ["frappe"]

# Roles + notifications are created idempotently (safe to run on every migrate)
after_install = "prime_ticket.install.after_install"
after_migrate = "prime_ticket.install.after_migrate"
