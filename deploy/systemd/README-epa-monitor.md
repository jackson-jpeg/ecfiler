# EPA user-group monitor on the VPS

Installed 2026-11-13 as an approved exception to the VPS retired list
(Jackson, via the lead: "install the rewritten EPA monitor ... one quiet alert
path, no paging storms"). Recorded in `/root/CLAUDE.md`.

Why: the Electronic Public Access Public User Group's call for members was
expected around August 2026 and has not gone out. Current terms end
2026-12-31, so the call is overdue rather than missed. In 2024 uscourts.gov
posted the call 17 days before PACER did. ECFiler wants a seat
(`docs/outreach/c3-epa-application.md`, `docs/pacer-engagement-plan.md`).

What runs: `scripts/epa-window-monitor.sh`, copied (not linked) to
`/usr/local/lib/ecfiler-epa-monitor/`, once a day, niced, idle IO, 10% CPU.
State in `/var/lib/ecfiler-epa-monitor`. Alerts: `ops-page` at default
priority, each kind once (see the script header). It stops itself after
2027-03-31 with one last page.

Install (or update after changing the script):

    install -D -m 755 scripts/epa-window-monitor.sh /usr/local/lib/ecfiler-epa-monitor/epa-window-monitor.sh
    install -m 644 deploy/systemd/ecfiler-epa-monitor.{service,timer} /etc/systemd/system/
    systemctl daemon-reload && systemctl enable --now ecfiler-epa-monitor.timer

Remove:

    systemctl disable --now ecfiler-epa-monitor.timer
    rm /etc/systemd/system/ecfiler-epa-monitor.{service,timer} && systemctl daemon-reload
    rm -r /usr/local/lib/ecfiler-epa-monitor /var/lib/ecfiler-epa-monitor
