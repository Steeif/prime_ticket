frappe.pages["prime-ticket-analytics"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Ticket Analytics"),
		single_column: true,
	});

	page.main.addClass("prime-ticket-analytics-page");
	page.main.html(frappe.render_template("prime_ticket_analytics", {}));

	const root = $(page.main);
	const localDate = (date) => {
		const offset = date.getTimezoneOffset();
		return new Date(date.getTime() - offset * 60000).toISOString().slice(0, 10);
	};
	const end = new Date();
	const start = new Date();
	start.setDate(start.getDate() - 29);
	root.find('[data-filter="from"]').val(localDate(start));
	root.find('[data-filter="to"]').val(localDate(end));

	const esc = (value) => $("<div>").text(value == null ? "" : String(value)).html();
	const number = (value) => Number(value || 0);
	const prettyHours = (value) => {
		if (value == null || value === "") return "—";
		const hours = number(value);
		if (hours < 1) return Math.max(1, Math.round(hours * 60)) + " min";
		return hours < 10 ? hours.toFixed(1) + " h" : Math.round(hours) + " h";
	};

	function renderBars(selector, rows, options = {}) {
		const target = root.find(selector);
		if (!rows || !rows.length) {
			target.html('<div class="pta-empty-inline">No ticket data for this period.</div>');
			return;
		}
		const max = Math.max(...rows.map((row) => number(row.value)), 1);
		target.html(rows.map((row, index) => {
			const value = number(row.value);
			const width = Math.max(value ? 4 : 0, Math.round((value / max) * 100));
			return `<div class="pta-bar-row">
				<div class="pta-bar-label"><span>${esc(row.label)}</span><strong>${value}</strong></div>
				<div class="pta-bar-track"><span class="pta-bar-fill ${options.palette ? "pta-tone-" + (index % 5) : ""}" style="width:${width}%"></span></div>
			</div>`;
		}).join(""));
	}

	function renderTrend(rows) {
		const target = root.find('[data-chart="trend"]');
		if (!rows || !rows.length) {
			target.html('<div class="pta-empty-inline">No tickets were created in this period.</div>');
			return;
		}
		const max = Math.max(...rows.map((row) => number(row.value)), 1);
		target.html(rows.map((row) => {
			const value = number(row.value);
			const height = Math.max(value ? 5 : 2, Math.round((value / max) * 100));
			const date = new Date(row.label + "T00:00:00");
			const label = date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
			return `<div class="pta-trend-col" title="${esc(row.label)}: ${value} tickets">
				<strong>${value || ""}</strong><span class="pta-trend-bar" style="height:${height}%"></span><small>${esc(label)}</small>
			</div>`;
		}).join(""));
	}

	function renderTables(data) {
		const priorities = data.priorities || [];
		root.find('[data-table="sla"]').html(priorities.map((row) => {
			const met = number(row.met);
			const breached = number(row.breached);
			const responseCount = met + breached;
			const rate = responseCount ? Math.round((met / responseCount) * 100) : null;
			return `<tr><td><span class="pta-priority pta-priority-${esc(String(row.priority).toLowerCase())}">${esc(row.priority)}</span></td>
				<td>${number(row.total)}</td><td>${rate == null ? "—" : rate + "%"}</td>
				<td class="${breached ? "pta-cell-alert" : ""}">${breached}</td><td>${prettyHours(row.avg_response_hours)}</td></tr>`;
		}).join("") || '<tr><td colspan="5" class="pta-empty-cell">No tickets in this period.</td></tr>');

		const oldest = data.oldest || [];
		root.find('[data-empty="oldest"]').prop("hidden", oldest.length > 0);
		root.find('[data-table="oldest"]').html(oldest.map((row) => {
			const opened = row.opened_at ? new Date(row.opened_at.replace(" ", "T")) : null;
			const ageHours = opened ? Math.max(0, (Date.now() - opened.getTime()) / 3600000) : 0;
			const age = ageHours >= 48 ? Math.floor(ageHours / 24) + " days" : prettyHours(ageHours);
			return `<tr>
				<td><a href="/app/support-ticket/${encodeURIComponent(row.name)}">${esc(row.name)}</a></td>
				<td class="pta-subject">${esc(row.subject)}</td><td>${esc(row.category)}</td>
				<td><span class="pta-priority pta-priority-${esc(String(row.priority || "").toLowerCase())}">${esc(row.priority)}</span></td>
				<td><span class="pta-status">${esc(row.status)}</span></td><td>${opened ? esc(opened.toLocaleDateString()) : "—"}</td><td>${age}</td>
			</tr>`;
		}).join(""));
	}

	function load() {
		const fromDate = root.find('[data-filter="from"]').val();
		const toDate = root.find('[data-filter="to"]').val();
		root.find(".pta-error").prop("hidden", true).text("");
		root.find(".pta-content").prop("hidden", true);
		root.find(".pta-loading").prop("hidden", false);

		frappe.call({
			method: "prime_ticket.prime_ticket.page.prime_ticket_analytics.prime_ticket_analytics.get_report_data",
			args: { from_date: fromDate, to_date: toDate },
			callback: (response) => {
				root.find(".pta-loading").prop("hidden", true);
				if (response.exc || !response.message) {
					root.find(".pta-error").prop("hidden", false).text(__("Could not load the reports. Check your access and try again."));
					return;
				}
				const data = response.message;
				const period = data.period || {};
				const backlog = data.backlog || {};
				root.find('[data-kpi="total"]').text(number(period.total).toLocaleString());
				root.find('[data-kpi="open"]').text(number(backlog.open_count).toLocaleString());
				root.find('[data-kpi-note="backlog"]').text(__(`${number(backlog.response_overdue)} first response late · ${number(backlog.resolution_overdue)} resolution late`));
				const eligible = number(period.response_met) + number(period.response_breached);
				const rate = eligible ? Math.round((number(period.response_met) / eligible) * 100) : null;
				root.find('[data-kpi="sla"]').text(rate == null ? "—" : rate + "%");
				root.find('[data-kpi-note="sla"]').text(eligible ? `${number(period.response_met)} met · ${number(period.response_breached)} missed` : __("No response deadlines in this period"));
				root.find('[data-kpi="response"]').text(prettyHours(period.avg_response_hours));
				root.find(".pta-meta [data-range]").text(`${data.from_date} — ${data.to_date}`);
				root.find("[data-updated]").text(new Date(data.generated_at.replace(" ", "T")).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
				renderTrend(data.trend);
				renderBars('[data-chart="statuses"]', data.statuses, { palette: true });
				renderBars('[data-chart="categories"]', data.categories, { palette: true });
				renderTables(data);
				root.find(".pta-content").prop("hidden", false);
			},
			error: () => {
				root.find(".pta-loading").prop("hidden", true);
				root.find(".pta-error").prop("hidden", false).text(__("Could not load the reports. Check your access and try again."));
			},
		});
	}

	root.find(".pta-refresh").on("click", load);
	root.find('[data-filter="from"], [data-filter="to"]').on("change", load);
	load();
};
