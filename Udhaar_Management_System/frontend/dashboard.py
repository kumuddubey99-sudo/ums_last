import flet as ft
from api import api_get
from language import t

def create_dashboard_view(page: ft.Page, on_view_transaction=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    text_color = "#FFFFFF" if is_dark else "#212121"
    sub_text = "#A0A0A0" if is_dark else "#616161"
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    border_color = "#333333" if is_dark else "#E0E0E0"

    data, code = api_get("/api/dashboard")
    if code != 200:
        data = {
            "total_customers": 0,
            "total_credit": 0.0,
            "total_paid": 0.0,
            "outstanding_balance": 0.0,
            "recent_transactions": []
        }

    total_customers = data.get("total_customers", 0)
    total_credit = data.get("total_credit", 0.0)
    total_paid = data.get("total_paid", 0.0)
    outstanding = data.get("outstanding_balance", 0.0)
    recent_txns = data.get("recent_transactions", [])

    def stat_card(label, val, prefix=""):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=13, color=sub_text, weight=ft.FontWeight.W_500),
                    ft.Text(f"{prefix}{val}", size=22, weight=ft.FontWeight.BOLD, color=text_color),
                ],
                spacing=6
            ),
            bgcolor=card_bg,
            border=ft.border.all(1, border_color),
            border_radius=6,
            padding=18,
            expand=True
        )

    # Status color helper
    def get_status_color(status_str):
        if status_str == "Paid":
            return "#2E7D32"
        elif status_str == "Overdue":
            return "#D32F2F"
        return "#ED6C02"

    rows = []
    for txn in recent_txns:
        st = txn.get("payment_status", "Pending")
        st_color = get_status_color(st)
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Text(txn["transaction_id"], weight=ft.FontWeight.BOLD, color="#1565C0"),
                        on_tap=lambda e, tid=txn["transaction_id"]: on_view_transaction(tid) if on_view_transaction else None
                    ),
                    ft.DataCell(ft.Text(txn.get("customer_name", "-"), color=text_color)),
                    ft.DataCell(ft.Text(f"₹{txn.get('total_amount', 0):,.2f}", color=text_color)),
                    ft.DataCell(ft.Text(txn.get("transaction_date", "-"), color=text_color)),
                    ft.DataCell(ft.Text(txn.get("due_date", "-"), color=text_color)),
                    ft.DataCell(ft.Text(st, color=st_color, weight=ft.FontWeight.W_600)),
                ]
            )
        )

    table_container = ft.Container(
        content=ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(t("transaction_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                ft.DataColumn(ft.Text(t("customer_name"), weight=ft.FontWeight.BOLD, color=text_color)),
                ft.DataColumn(ft.Text(t("total_amount"), weight=ft.FontWeight.BOLD, color=text_color)),
                ft.DataColumn(ft.Text(t("transaction_date"), weight=ft.FontWeight.BOLD, color=text_color)),
                ft.DataColumn(ft.Text(t("due_date"), weight=ft.FontWeight.BOLD, color=text_color)),
                ft.DataColumn(ft.Text(t("payment_status"), weight=ft.FontWeight.BOLD, color=text_color)),
            ],
            rows=rows,
            heading_row_color="#2A2A2A" if is_dark else "#F0F4F8",
            border=ft.border.all(1, border_color),
        ),
        bgcolor=card_bg,
        border_radius=6,
        padding=12
    )

    return ft.Column(
        [
            ft.Text(t("dashboard"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Row(
                [
                    stat_card(t("total_customers"), total_customers),
                    stat_card(t("total_credit"), f"{total_credit:,.2f}", "₹"),
                    stat_card(t("total_paid"), f"{total_paid:,.2f}", "₹"),
                    stat_card(t("outstanding_balance"), f"{outstanding:,.2f}", "₹"),
                ],
                spacing=16
            ),
            ft.Container(height=16),
            ft.Text(t("recent_activities"), size=16, weight=ft.FontWeight.BOLD, color=text_color),
            table_container if rows else ft.Container(
                content=ft.Text(t("no_results"), color=sub_text),
                padding=24,
                bgcolor=card_bg,
                border=ft.border.all(1, border_color),
                border_radius=6
            )
        ],
        spacing=12,
        expand=True
    )
