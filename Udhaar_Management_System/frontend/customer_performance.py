import flet as ft
from api import api_get
from language import t

def create_customer_performance_view(page: ft.Page, on_view_summary):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    data, _ = api_get("/api/performance")
    if not isinstance(data, list):
        data = []

    def get_status_color(status_str):
        if status_str == "Excellent":
            return "#2E7D32"
        elif status_str == "Good":
            return "#1565C0"
        elif status_str == "Average":
            return "#ED6C02"
        return "#D32F2F"

    rows = []
    for item in data:
        cid = item["customer_id"]
        status_str = item.get("performance_status", "Good")
        st_color = get_status_color(status_str)

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Text(cid, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        on_tap=lambda e, customer_id=cid: on_view_summary(customer_id)
                    ),
                    ft.DataCell(ft.Text(item["customer_name"], color=text_color)),
                    ft.DataCell(ft.Text(str(item["total_transactions"]), color=text_color)),
                    ft.DataCell(ft.Text(f"₹{item['total_credit']:,.2f}", color=text_color)),
                    ft.DataCell(ft.Text(f"₹{item['total_paid']:,.2f}", color=text_color)),
                    ft.DataCell(ft.Text(f"₹{item['pending_amount']:,.2f}", color=text_color)),
                    ft.DataCell(ft.Text(str(item["overdue_count"]), color="#D32F2F" if item["overdue_count"] > 0 else text_color)),
                    ft.DataCell(ft.Text(f"{item['performance_percentage']}%", weight=ft.FontWeight.W_600, color=text_color)),
                    ft.DataCell(ft.Text(status_str, color=st_color, weight=ft.FontWeight.BOLD)),
                ]
            )
        )

    return ft.Column(
        [
            ft.Text(t("customer_performance"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Container(
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(t("customer_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("customer_name"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text("Txns", weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("total_credit"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("total_paid"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("pending_amount"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("overdue_count"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("performance_percentage"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("performance_status"), weight=ft.FontWeight.BOLD, color=text_color)),
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
