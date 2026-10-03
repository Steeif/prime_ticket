frappe.listview_settings["Support Ticket"] = {
    add_fields: ["status", "priority"],
    get_indicator(doc) {
        const colors = {
            "Open": "orange",
            "Working in Progress": "blue",
            "Pending": "yellow",
            "Waiting for Reply": "purple",
            "Resolved": "green",
            "Reopened": "red",
            "Closed": "gray",
        };
        return [__(doc.status), colors[doc.status] || "gray", "status,=," + doc.status];
    },
};
