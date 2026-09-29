import flet as ft
from api import api_get
from language import t

def create_outstanding_balance_view(page: ft.Page, on_view_summary, on_go_to_update=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    data, _ = api_get("/api/outstanding")
    if not isinstance(data, list):
        data = []

    def get_status_color(st):
        if st == "Paid":
            return "#2E7D32"
        elif st == "Overdue":
            return "#D32F2F"
        return "#ED6C02"

    rows = []
    for item in data:
        cid = item["customer_id"]
        st = item.get("status", "Pending")
        action_controls = [
            ft.TextButton("View", on_click=lambda e, customer_id=cid: on_view_summary(customer_id))
        ]
        if on_go_to_update:
            action_controls.append(
                ft.TextButton(t("update"), on_click=lambda e, customer_id=cid: on_go_to_update(customer_id))
            )

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Text(cid, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        on_tap=lambda e, customer_id=cid: on_view_summary(customer_id)
                    ),
                    ft.DataCell(ft.Text(item["customer_name"], color=text_color)),
                    ft.DataCell(ft.Text(f"₹{item['total_due']:,.2f}", color=text_color)),
                    ft.DataCell(ft.Text(f"₹{item['total_paid']:,.2f}", color=text_color)),
                    ft.DataCell(ft.Text(f"₹{item['pending_amount']:,.2f}", weight=ft.FontWeight.BOLD, color=text_color)),
                    ft.DataCell(ft.Text(item.get("due_date", "-"), color=text_color)),
                    ft.DataCell(ft.Text(st, color=get_status_color(st), weight=ft.FontWeight.W_600)),
                    ft.DataCell(ft.Row(action_controls, spacing=0)),
                ]
            )
        )

    return ft.Column(
        [
            ft.Text(t("outstanding_balance"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Container(
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(t("customer_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("customer_name"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text("Total Due", weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("total_paid"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("pending_amount"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("due_date"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("payment_status"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, color=text_color)),
                    ],
                    rows=rows,
                    heading_row_color="#2A2A2A" if is_dark else "#F0F4F8",
                    border=ft.border.all(1, border_color),
                ),
                bgcolor=card_bg,
                border_radius=6,
                padding=12
            ) if rows else ft.Container(
                content=ft.Text(t("no_results"), color="#888888"),
                padding=24,
                bgcolor=card_bg,
                border=ft.border.all(1, border_color),
                border_radius=6
            )
        ],
        spacing=12,
        expand=True
    )
