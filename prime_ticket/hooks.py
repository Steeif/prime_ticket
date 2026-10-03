app_name = "prime_ticket"
app_title = "Prime Ticket"
app_publisher = "Ahmed Mostafa"
app_description = "Internal support ticketing app for ERPNext: login-required web form intake, operator workflow, and status-based email notifications."
app_email = ""
app_license = "MIT"

required_apps = ["frappe"]

# Run after the app is installed on a site: create custom roles
after_install = "prime_ticket.install.after_install"

# Ship the email notification rules as fixtures (imported on install/migrate)
fixtures = [
    {"dt": "Notification", "filters": [["module", "=", "Prime Ticket"]]},
]
