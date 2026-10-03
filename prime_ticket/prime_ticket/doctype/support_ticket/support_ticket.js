frappe.ui.form.on("Support Ticket", {
    refresh(frm) {
        // Let the ticket raiser reopen a resolved ticket from the desk
        if (frm.doc.status === "Resolved" && frm.doc.raised_by === frappe.session.user) {
            frm.add_custom_button(__("Reopen Ticket"), () => {
                frm.set_value("status", "Reopened");
                frm.save();
            });
        }
    },
});
