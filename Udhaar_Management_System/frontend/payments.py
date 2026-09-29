import flet as ft
from datetime import datetime
from api import api_get, api_post, api_put, api_delete
from language import t

def create_add_payment_view(page: ft.Page, on_saved=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    next_id_res, _ = api_get("/api/payments/next-id")
    pay_id = next_id_res.get("next_id", "PAY001")

    txns, _ = api_get("/api/transactions")
    if not isinstance(txns, list):
        txns = []

    txn_options = [
        ft.dropdown.Option(t_row["transaction_id"], f"{t_row['transaction_id']} - {t_row.get('customer_name', '')} (Pending: ₹{t_row.get('pending_amount', 0):,.2f})")
        for t_row in txns
    ]

    id_field = ft.TextField(label=t("payment_id"), value=pay_id, disabled=True, width=340, border_color=border_color)
    txn_dropdown = ft.Dropdown(
        label=t("transaction_id"),
        options=txn_options,
        value=txns[0]["transaction_id"] if txns else None,
        width=340,
        border_color=border_color
    )
    amount_field = ft.TextField(label=f"{t('payment_amount')} (₹) *", width=340, border_color=border_color)
    date_field = ft.TextField(label=t("payment_date"), value=datetime.now().strftime("%Y-%m-%d"), width=340, border_color=border_color)
    method_dropdown = ft.Dropdown(
        label=t("payment_method"),
        options=[
            ft.dropdown.Option("Cash"),
            ft.dropdown.Option("UPI"),
            ft.dropdown.Option("Bank Transfer"),
            ft.dropdown.Option("Cheque")
        ],
        value="Cash",
        width=340,
        border_color=border_color
    )
    ref_field = ft.TextField(label=t("reference_id"), width=340, border_color=border_color)
    msg_text = ft.Text("", size=13)

    def on_clear(e):
        amount_field.value = ""
        ref_field.value = ""
        msg_text.value = ""
        page.update()

    def on_save(e):
        msg_text.value = ""
        if not txn_dropdown.value:
            msg_text.value = "Select transaction"
            msg_text.color = "#D32F2F"
            page.update()
            return
        try:
            amt = float(amount_field.value)
            if amt <= 0:
                raise ValueError()
        except Exception:
            msg_text.value = "Enter valid positive payment amount"
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "transaction_id": txn_dropdown.value,
            "payment_amount": amt,
            "payment_date": date_field.value.strip(),
            "payment_method": method_dropdown.value,
            "reference_id": ref_field.value.strip() if ref_field.value else ""
        }

        res, code = api_post("/api/payments", payload)
        if code == 200:
            msg_text.value = t("success_save")
            msg_text.color = "#2E7D32"
            on_clear(None)
            n_res, _ = api_get("/api/payments/next-id")
            id_field.value = n_res.get("next_id", "")
            page.update()
            if on_saved:
                on_saved()
        else:
            msg_text.value = res.get("detail", "Failed to save payment")
            msg_text.color = "#D32F2F"
            page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("add_payment"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                id_field,
                txn_dropdown,
                amount_field,
                date_field,
                method_dropdown,
                ref_field,
                msg_text,
                ft.Row(
                    [
                        ft.ElevatedButton(t("save"), bgcolor="#1565C0", color="#FFFFFF", width=120, height=40, on_click=on_save),
                        ft.OutlinedButton(t("clear"), width=120, height=40, on_click=on_clear),
                    ],
                    spacing=12
                )
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=24,
        bgcolor=card_bg,
        border_radius=6,
        border=ft.border.all(1, border_color),
        width=400
    )

def create_view_payments_view(page: ft.Page, on_go_to_update):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    payments, _ = api_get("/api/payments")
    if not isinstance(payments, list):
        payments = []

    msg_banner = ft.Text("", size=13)

    def delete_pay_handler(pid):
        res, code = api_delete(f"/api/payments/{pid}")
        if code == 200:
            msg_banner.value = t("success_delete")
            msg_banner.color = "#2E7D32"
            page.update()
        else:
            msg_banner.value = res.get("detail", "Error deleting payment")
            msg_banner.color = "#D32F2F"
            page.update()

    rows = []
    for p in payments:
        pid = p["payment_id"]
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(pid, weight=ft.FontWeight.BOLD, color="#1565C0")),
                    ft.DataCell(ft.Text(p.get("customer_name", "-"), color=text_color)),
                    ft.DataCell(ft.Text(p["transaction_id"], color=text_color)),
                    ft.DataCell(ft.Text(f"₹{p['payment_amount']:,.2f}", weight=ft.FontWeight.BOLD, color=text_color)),
                    ft.DataCell(ft.Text(p["payment_date"], color=text_color)),
                    ft.DataCell(ft.Text(p["payment_method"], color=text_color)),
                    ft.DataCell(ft.Text(p.get("reference_id") or "-", color=text_color)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(ft.Icons.EDIT, icon_size=18, tooltip=t("update"), on_click=lambda e, i=pid: on_go_to_update(i)),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=18, icon_color="#D32F2F", tooltip=t("delete"), on_click=lambda e, i=pid: delete_pay_handler(i)),
                            ],
                            spacing=0
                        )
                    )
                ]
            )
        )

    return ft.Column(
        [
            ft.Text(t("view_payments"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            msg_banner,
            ft.Container(
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(t("payment_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("customer_name"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("transaction_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("payment_amount"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("payment_date"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("payment_method"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("reference_id"), weight=ft.FontWeight.BOLD, color=text_color)),
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

def create_update_payment_view(page: ft.Page, initial_id=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    payments, _ = api_get("/api/payments")
    if not isinstance(payments, list):
        payments = []

    pay_options = [
        ft.dropdown.Option(p["payment_id"], f"{p['payment_id']} - ₹{p['payment_amount']} ({p.get('customer_name', '')})")
        for p in payments
    ]

    selected_pay_dropdown = ft.Dropdown(
        label=t("payment_id"),
        options=pay_options,
        value=initial_id if initial_id else (payments[0]["payment_id"] if payments else None),
        width=340,
        border_color=border_color
    )

    cust_name_field = ft.TextField(label=t("customer_name"), disabled=True, width=340, border_color=border_color)
    txn_id_field = ft.TextField(label=t("transaction_id"), disabled=True, width=340, border_color=border_color)
    amount_field = ft.TextField(label=t("payment_amount"), width=340, border_color=border_color)
    date_field = ft.TextField(label=t("payment_date"), width=340, border_color=border_color)
    method_dropdown = ft.Dropdown(
        label=t("payment_method"),
        options=[
            ft.dropdown.Option("Cash"),
            ft.dropdown.Option("UPI"),
            ft.dropdown.Option("Bank Transfer"),
            ft.dropdown.Option("Cheque")
        ],
        width=340,
        border_color=border_color
    )
    ref_field = ft.TextField(label=t("reference_id"), width=340, border_color=border_color)
    msg_text = ft.Text("", size=13)

    def on_load(e):
        pid = selected_pay_dropdown.value
        if not pid:
            return
        data, code = api_get(f"/api/payments/{pid}")
        if code == 200:
            cust_name_field.value = data.get("customer_name", "")
            txn_id_field.value = data.get("transaction_id", "")
            amount_field.value = str(data.get("payment_amount", 0.0))
            date_field.value = data.get("payment_date", "")
            method_dropdown.value = data.get("payment_method", "Cash")
            ref_field.value = data.get("reference_id", "")
            msg_text.value = ""
            page.update()

    def on_clear(e):
        amount_field.value = ""
        ref_field.value = ""
        msg_text.value = ""
        page.update()

    def on_update(e):
        pid = selected_pay_dropdown.value
        if not pid:
            msg_text.value = "Select payment"
            msg_text.color = "#D32F2F"
            page.update()
            return
        try:
            amt = float(amount_field.value)
            if amt <= 0:
                raise ValueError()
        except Exception:
            msg_text.value = "Invalid payment amount"
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "payment_amount": amt,
            "payment_date": date_field.value.strip(),
            "payment_method": method_dropdown.value,
            "reference_id": ref_field.value.strip() if ref_field.value else ""
        }

        res, code = api_put(f"/api/payments/{pid}", payload)
        if code == 200:
            msg_text.value = t("success_update")
            msg_text.color = "#2E7D32"
            page.update()
        else:
            msg_text.value = res.get("detail", "Update failed")
            msg_text.color = "#D32F2F"
            page.update()

    if selected_pay_dropdown.value:
        on_load(None)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("update_payment"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Row([selected_pay_dropdown, ft.ElevatedButton(t("load"), bgcolor="#1565C0", color="#FFFFFF", on_click=on_load)], spacing=8),
                cust_name_field,
                txn_id_field,
                amount_field,
                date_field,
                method_dropdown,
                ref_field,
                msg_text,
                ft.Row(
                    [
                        ft.ElevatedButton(t("update"), bgcolor="#1565C0", color="#FFFFFF", width=120, height=40, on_click=on_update),
                        ft.OutlinedButton(t("clear"), width=120, height=40, on_click=on_clear),
                    ],
                    spacing=12
                )
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=24,
        bgcolor=card_bg,
        border_radius=6,
        border=ft.border.all(1, border_color),
        width=460
    )
