import flet as ft
from datetime import datetime
from api import api_get, api_post, api_put, api_delete
from language import t

def create_add_transaction_view(page: ft.Page, on_saved=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    next_id_res, _ = api_get("/api/transactions/next-id")
    txn_id = next_id_res.get("next_id", "TXN001")

    customers, _ = api_get("/api/customers")
    if not isinstance(customers, list):
        customers = []

    cust_options = [
        ft.dropdown.Option(c["customer_id"], f"{c['customer_id']} - {c['customer_name']}")
        for c in customers
    ]

    id_field = ft.TextField(label=t("transaction_id"), value=txn_id, disabled=True, width=340, border_color=border_color)
    cust_dropdown = ft.Dropdown(
        label=f"{t('customers')} *",
        options=cust_options,
        value=customers[0]["customer_id"] if customers else None,
        width=340,
        border_color=border_color
    )
    txn_date_field = ft.TextField(label=f"{t('transaction_date')} *", value="", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    due_date_field = ft.TextField(label=f"{t('due_date')} *", value="", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    created_date_field = ft.TextField(label=f"{t('created_date')} *", value="", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    updated_date_field = ft.TextField(label=f"{t('updated_date')} *", value="", width=165, border_color=border_color, hint_text="YYYY-MM-DD")

    t_picker = ft.DatePicker(on_change=lambda e: (setattr(txn_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    d_picker = ft.DatePicker(on_change=lambda e: (setattr(due_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    c_picker = ft.DatePicker(on_change=lambda e: (setattr(created_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    u_picker = ft.DatePicker(on_change=lambda e: (setattr(updated_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    if hasattr(page, "overlay"):
        page.overlay.extend([t_picker, d_picker, c_picker, u_picker])

    txn_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(t_picker, "open", True) or page.update())
    due_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(d_picker, "open", True) or page.update())
    created_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(c_picker, "open", True) or page.update())
    updated_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(u_picker, "open", True) or page.update())

    amount_field = ft.TextField(label=f"{t('total_amount')} (₹) *", width=340, border_color=border_color)
    note_field = ft.TextField(label=t("notes"), multiline=True, min_lines=2, max_lines=3, width=340, border_color=border_color)

    msg_text = ft.Text("", size=13)

    def on_clear(e):
        amount_field.value = ""
        note_field.value = ""
        txn_date_field.value = ""
        due_date_field.value = ""
        created_date_field.value = ""
        updated_date_field.value = ""
        msg_text.value = ""
        page.update()

    def on_save(e):
        msg_text.value = ""
        if not cust_dropdown.value:
            msg_text.value = f"{t('customers')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not txn_date_field.value.strip():
            msg_text.value = f"{t('transaction_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not due_date_field.value.strip():
            msg_text.value = f"{t('due_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not created_date_field.value.strip():
            msg_text.value = f"{t('created_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not updated_date_field.value.strip():
            msg_text.value = f"{t('updated_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not amount_field.value.strip():
            msg_text.value = f"{t('total_amount')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        try:
            amt = float(amount_field.value)
            if amt <= 0:
                raise ValueError()
        except Exception:
            msg_text.value = "Enter valid positive total amount"
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "customer_id": cust_dropdown.value,
            "transaction_date": txn_date_field.value.strip(),
            "due_date": due_date_field.value.strip(),
            "created_date": created_date_field.value.strip(),
            "updated_date": updated_date_field.value.strip(),
            "total_amount": amt,
            "note": note_field.value.strip() if note_field.value else ""
        }

        res, code = api_post("/api/transactions", payload)
        if code == 200:
            msg_text.value = t("success_save")
            msg_text.color = "#2E7D32"
            on_clear(None)
            n_res, _ = api_get("/api/transactions/next-id")
            id_field.value = n_res.get("next_id", "")
            page.update()
            if on_saved:
                on_saved()
        else:
            msg_text.value = res.get("detail", "Failed to save transaction")
            msg_text.color = "#D32F2F"
            page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("add_transaction"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                id_field,
                cust_dropdown,
                ft.Row([txn_date_field, due_date_field], spacing=10, width=340),
                amount_field,
                note_field,
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

def create_view_transactions_view(page: ft.Page, on_view_summary, on_go_to_update):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    txns, _ = api_get("/api/transactions")
    if not isinstance(txns, list):
        txns = []

    msg_banner = ft.Text("", size=13)

    def delete_txn_handler(tid):
        res, code = api_delete(f"/api/transactions/{tid}")
        if code == 200:
            msg_banner.value = t("success_delete")
            msg_banner.color = "#2E7D32"
            page.update()
        else:
            msg_banner.value = res.get("detail", "Error deleting transaction")
            msg_banner.color = "#D32F2F"
            page.update()

    def get_status_color(st):
        if st == "Paid":
            return "#2E7D32"
        elif st == "Overdue":
            return "#D32F2F"
        return "#ED6C02"

    rows = []
    for t_row in txns:
        tid = t_row["transaction_id"]
        st = t_row.get("payment_status", "Pending")
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Text(tid, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        on_tap=lambda e, transaction_id=tid: on_view_summary(transaction_id)
                    ),
                    ft.DataCell(ft.Text(t_row.get("customer_name", "-"), color=text_color)),
                    ft.DataCell(ft.Text(t_row["transaction_date"], color=text_color)),
                    ft.DataCell(ft.Text(t_row["due_date"], color=text_color)),
                    ft.DataCell(ft.Text(f"₹{t_row['total_amount']:,.2f}", weight=ft.FontWeight.BOLD, color=text_color)),
                    ft.DataCell(ft.Text(st, color=get_status_color(st), weight=ft.FontWeight.W_600)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(ft.Icons.EDIT, icon_size=18, tooltip=t("update"), on_click=lambda e, i=tid: on_go_to_update(i)),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=18, icon_color="#D32F2F", tooltip=t("delete"), on_click=lambda e, i=tid: delete_txn_handler(i)),
                            ],
                            spacing=0
                        )
                    )
                ]
            )
        )

    return ft.Column(
        [
            ft.Text(t("view_transactions"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            msg_banner,
            ft.Container(
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(t("transaction_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("customer_name"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("transaction_date"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("due_date"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("total_amount"), weight=ft.FontWeight.BOLD, color=text_color)),
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

def create_update_transaction_view(page: ft.Page, initial_id=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    txns, _ = api_get("/api/transactions")
    if not isinstance(txns, list):
        txns = []

    customers, _ = api_get("/api/customers")
    if not isinstance(customers, list):
        customers = []

    txn_options = [
        ft.dropdown.Option(t_row["transaction_id"], f"{t_row['transaction_id']} - {t_row.get('customer_name', '')}")
        for t_row in txns
    ]

    cust_options = [
        ft.dropdown.Option(c["customer_id"], f"{c['customer_id']} - {c['customer_name']}")
        for c in customers
    ]

    selected_txn_dropdown = ft.Dropdown(
        label=t("transaction_id"),
        options=txn_options,
        value=initial_id if initial_id else (txns[0]["transaction_id"] if txns else None),
        width=340,
        border_color=border_color
    )

    cust_dropdown = ft.Dropdown(label=f"{t('customers')} *", options=cust_options, width=340, border_color=border_color)
    txn_date_field = ft.TextField(label=f"{t('transaction_date')} *", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    due_date_field = ft.TextField(label=f"{t('due_date')} *", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    created_date_field = ft.TextField(label=f"{t('created_date')} *", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    updated_date_field = ft.TextField(label=f"{t('updated_date')} *", width=165, border_color=border_color, hint_text="YYYY-MM-DD")

    up_t_picker = ft.DatePicker(on_change=lambda e: (setattr(txn_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    up_d_picker = ft.DatePicker(on_change=lambda e: (setattr(due_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    up_c_picker = ft.DatePicker(on_change=lambda e: (setattr(created_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    up_u_picker = ft.DatePicker(on_change=lambda e: (setattr(updated_date_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update()))
    if hasattr(page, "overlay"):
        page.overlay.extend([up_t_picker, up_d_picker, up_c_picker, up_u_picker])

    txn_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(up_t_picker, "open", True) or page.update())
    due_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(up_d_picker, "open", True) or page.update())
    created_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(up_c_picker, "open", True) or page.update())
    updated_date_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(up_u_picker, "open", True) or page.update())

    amount_field = ft.TextField(label=f"{t('total_amount')} (₹) *", width=340, border_color=border_color)
    note_field = ft.TextField(label=t("notes"), multiline=True, min_lines=2, max_lines=3, width=340, border_color=border_color)
    status_field = ft.TextField(label=t("payment_status"), disabled=True, width=340, border_color=border_color)

    msg_text = ft.Text("", size=13)

    def on_load(e):
        tid = selected_txn_dropdown.value
        if not tid:
            return
        data, code = api_get(f"/api/transactions/{tid}")
        if code == 200:
            cust_dropdown.value = data.get("customer_id")
            txn_date_field.value = data.get("transaction_date", "")
            due_date_field.value = data.get("due_date", "")
            created_date_field.value = data.get("created_date", "")
            updated_date_field.value = data.get("updated_date", "")
            amount_field.value = str(data.get("total_amount", 0.0))
            note_field.value = data.get("note", "")
            status_field.value = data.get("payment_status", "Pending")
            msg_text.value = ""
            page.update()

    def on_clear(e):
        amount_field.value = ""
        note_field.value = ""
        txn_date_field.value = ""
        due_date_field.value = ""
        created_date_field.value = ""
        updated_date_field.value = ""
        status_field.value = ""
        msg_text.value = ""
        page.update()

    def on_update(e):
        tid = selected_txn_dropdown.value
        if not tid:
            msg_text.value = "Please select a transaction to update."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not cust_dropdown.value:
            msg_text.value = f"{t('customers')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not txn_date_field.value.strip():
            msg_text.value = f"{t('transaction_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not due_date_field.value.strip():
            msg_text.value = f"{t('due_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not created_date_field.value.strip():
            msg_text.value = f"{t('created_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not updated_date_field.value.strip():
            msg_text.value = f"{t('updated_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not amount_field.value.strip():
            msg_text.value = f"{t('total_amount')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        try:
            amt = float(amount_field.value)
            if amt <= 0:
                raise ValueError()
        except Exception:
            msg_text.value = "Enter valid positive total amount"
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "customer_id": cust_dropdown.value,
            "transaction_date": txn_date_field.value.strip(),
            "due_date": due_date_field.value.strip(),
            "created_date": created_date_field.value.strip(),
            "updated_date": updated_date_field.value.strip(),
            "total_amount": amt,
            "note": note_field.value.strip() if note_field.value else ""
        }

        res, code = api_put(f"/api/transactions/{tid}", payload)
        if code == 200:
            msg_text.value = t("success_update")
            msg_text.color = "#2E7D32"
            page.update()
        else:
            msg_text.value = res.get("detail", "Update failed")
            msg_text.color = "#D32F2F"
            page.update()

    if selected_txn_dropdown.value:
        on_load(None)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("update_transaction"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Row([selected_txn_dropdown, ft.ElevatedButton(t("load"), bgcolor="#1565C0", color="#FFFFFF", on_click=on_load)], spacing=8),
                cust_dropdown,
                ft.Row([txn_date_field, due_date_field], spacing=10, width=340),
                amount_field,
                note_field,
                status_field,
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

def create_transaction_summary_view(page: ft.Page, transaction_id: str, on_back):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"
    sub_text = "#A0A0A0" if is_dark else "#616161"

    data, code = api_get(f"/api/transactions/{transaction_id}/summary")
    if code != 200:
        return ft.Column([ft.Text("Transaction not found", color="#D32F2F"), ft.ElevatedButton("Back", on_click=lambda e: on_back())])

    t_data = data["transaction"]
    items = data.get("items", [])
    payments = data.get("payments", [])

    def section_header(title):
        return ft.Container(
            content=ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color="#1565C0"),
            padding=ft.padding.only(top=14, bottom=6),
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )

    def info_row(label, val):
        return ft.Row(
            [
                ft.Text(f"{label}:", width=150, color=sub_text, size=13),
                ft.Text(str(val if val else "-"), weight=ft.FontWeight.W_500, color=text_color, size=13)
            ],
            spacing=4
        )

    content_list = [
        ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: on_back()),
            ft.Text(f"{t('transaction_summary')} - {t_data['transaction_id']}", size=18, weight=ft.FontWeight.BOLD, color=text_color),
        ], spacing=8),
        section_header("TRANSACTION INFORMATION"),
        info_row(t("transaction_id"), t_data["transaction_id"]),
        info_row(t("customer_name"), t_data.get("customer_name")),
        info_row(t("transaction_date"), t_data["transaction_date"]),
        info_row(t("due_date"), t_data["due_date"]),
        info_row(t("total_amount"), f"₹{t_data['total_amount']:,.2f}"),
        info_row("Total Paid", f"₹{t_data.get('total_paid', 0.0):,.2f}"),
        info_row("Pending", f"₹{t_data.get('pending_amount', 0.0):,.2f}"),
        info_row(t("payment_status"), t_data.get("payment_status")),
        info_row(t("notes"), t_data.get("note")),
    ]

    content_list.append(section_header("CREDITED ITEMS"))
    if items:
        for it in items:
            content_list.append(
                info_row(f"{it['item_id']} - {it['item_name']}", f"Qty: {it['quantity']} × ₹{it['unit_price']} = ₹{it['subtotal']:,.2f}")
            )
    else:
        content_list.append(ft.Text("No credited items recorded for this bill.", size=13, color=sub_text))

    content_list.append(section_header("PAYMENTS"))
    if payments:
        for p in payments:
            content_list.append(
                info_row(f"{p['payment_id']} ({p['payment_date']})", f"₹{p['payment_amount']:,.2f} via {p['payment_method']}")
            )
    else:
        content_list.append(ft.Text("No payments recorded for this bill.", size=13, color=sub_text))

    return ft.Container(
        content=ft.Column(content_list, spacing=6, scroll=ft.ScrollMode.AUTO),
        bgcolor=card_bg,
        padding=24,
        border_radius=6,
        border=ft.border.all(1, border_color),
        width=560,
        expand=True
    )
