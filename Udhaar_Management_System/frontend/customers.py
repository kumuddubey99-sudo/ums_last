import flet as ft
from datetime import datetime
from api import api_get, api_post, api_put, api_delete
from language import t

def create_add_customer_view(page: ft.Page, on_saved=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    next_id_res, _ = api_get("/api/customers/next-id")
    cust_id = next_id_res.get("next_id", "CUST001")

    now = datetime.now()
    created_d = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    id_field = ft.TextField(label=t("customer_id"), value=cust_id, disabled=True, width=340, border_color=border_color)
    name_field = ft.TextField(label=f"{t('customer_name')} *", width=340, border_color=border_color)
    phone_field = ft.TextField(label=f"{t('mobile_number')} *", width=340, border_color=border_color, hint_text="10-digit mobile number", max_length=10)
    alt_phone_field = ft.TextField(label=t("alternate_number"), width=340, border_color=border_color, max_length=10)
    email_field = ft.TextField(label=t("email"), width=340, border_color=border_color)
    address_field = ft.TextField(label=f"{t('address')} *", multiline=True, min_lines=2, max_lines=3, width=340, border_color=border_color)

    created_field = ft.TextField(label=f"{t('created_date')} *", value="", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    updated_field = ft.TextField(label=f"{t('updated_date')} *", value="", width=165, border_color=border_color, hint_text="YYYY-MM-DD")

    # Calendar pickers for created and updated dates
    created_picker = ft.DatePicker(
        on_change=lambda e: (setattr(created_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update())
    )
    updated_picker = ft.DatePicker(
        on_change=lambda e: (setattr(updated_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update())
    )
    if hasattr(page, "overlay"):
        page.overlay.extend([created_picker, updated_picker])

    created_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(created_picker, "open", True) or page.update())
    updated_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(updated_picker, "open", True) or page.update())

    msg_text = ft.Text("", size=13)

    def on_clear(e):
        name_field.value = ""
        phone_field.value = ""
        alt_phone_field.value = ""
        email_field.value = ""
        address_field.value = ""
        created_field.value = ""
        updated_field.value = ""
        msg_text.value = ""
        page.update()

    def on_save(e):
        msg_text.value = ""
        name = name_field.value.strip() if name_field.value else ""
        phone = phone_field.value.strip() if phone_field.value else ""
        alt_phone = alt_phone_field.value.strip() if alt_phone_field.value else ""
        address = address_field.value.strip() if address_field.value else ""
        c_date = created_field.value.strip() if created_field.value else ""
        u_date = updated_field.value.strip() if updated_field.value else ""

        if not name:
            msg_text.value = f"{t('customer_name')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not phone:
            msg_text.value = f"{t('mobile_number')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if len(phone) != 10 or not phone.isdigit():
            msg_text.value = t("error_phone_10_digits")
            msg_text.color = "#D32F2F"
            page.update()
            return

        if alt_phone and (len(alt_phone) != 10 or not alt_phone.isdigit()):
            msg_text.value = "Alternate number must contain exactly 10 digits."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not address:
            msg_text.value = f"{t('address')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not c_date:
            msg_text.value = f"{t('created_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not u_date:
            msg_text.value = f"{t('updated_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "customer_name": name,
            "phone_number": phone,
            "alternate_number": alt_phone,
            "email": email_field.value.strip() if email_field.value else "",
            "address": address,
            "created_date": c_date,
            "updated_date": u_date
        }

        res, code = api_post("/api/customers", payload)
        if code == 200:
            msg_text.value = t("success_save")
            msg_text.color = "#2E7D32"
            on_clear(None)
            # reload next id
            n_res, _ = api_get("/api/customers/next-id")
            id_field.value = n_res.get("next_id", "")
            page.update()
            if on_saved:
                on_saved()
        else:
            msg_text.value = res.get("detail", res.get("error", "Failed to save customer"))
            msg_text.color = "#D32F2F"
            page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("add_customer"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Container(height=4),
                id_field,
                name_field,
                phone_field,
                alt_phone_field,
                email_field,
                address_field,
                ft.Row([created_field, time_field], spacing=10, width=340),
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

def create_view_customers_view(page: ft.Page, on_view_summary, on_go_to_update):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    customers, _ = api_get("/api/customers")
    if not isinstance(customers, list):
        customers = []

    msg_banner = ft.Text("", size=13)

    def delete_cust(cid):
        res, code = api_delete(f"/api/customers/{cid}")
        if code == 200:
            msg_banner.value = t("success_delete")
            msg_banner.color = "#2E7D32"
            page.update()
        else:
            msg_banner.value = res.get("detail", res.get("error", t("error_delete_restricted")))
            msg_banner.color = "#D32F2F"
            page.update()

    rows = []
    for c in customers:
        cid = c["customer_id"]
        perf_status = c.get("performance_status", "Good")
        perf_pct = c.get("performance_percentage", 100.0)

        perf_color = "#2E7D32" if perf_status == "Excellent" else ("#1565C0" if perf_status == "Good" else ("#ED6C02" if perf_status == "Average" else "#D32F2F"))

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Text(cid, weight=ft.FontWeight.BOLD, color="#1565C0"),
                        on_tap=lambda e, customer_id=cid: on_view_summary(customer_id)
                    ),
                    ft.DataCell(ft.Text(c["customer_name"], color=text_color)),
                    ft.DataCell(ft.Text(c["phone_number"], color=text_color)),
                    ft.DataCell(ft.Text(c.get("email") or "-", color=text_color)),
                    ft.DataCell(ft.Text(f"{perf_status} ({perf_pct}%)", color=perf_color, weight=ft.FontWeight.W_600)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(ft.Icons.EDIT, icon_size=18, tooltip=t("update"), on_click=lambda e, cid=cid: on_go_to_update(cid)),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=18, icon_color="#D32F2F", tooltip=t("delete"), on_click=lambda e, cid=cid: delete_cust(cid)),
                            ],
                            spacing=0
                        )
                    )
                ]
            )
        )

    return ft.Column(
        [
            ft.Text(t("view_customers"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            msg_banner,
            ft.Container(
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(t("customer_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("customer_name"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("mobile_number"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("email"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("customer_performance"), weight=ft.FontWeight.BOLD, color=text_color)),
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

def create_update_customer_view(page: ft.Page, initial_id=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    customers, _ = api_get("/api/customers")
    if not isinstance(customers, list):
        customers = []

    dropdown_options = [
        ft.dropdown.Option(c["customer_id"], f"{c['customer_id']} - {c['customer_name']}")
        for c in customers
    ]

    selected_id_dropdown = ft.Dropdown(
        label=t("customer_id"),
        options=dropdown_options,
        value=initial_id if initial_id else (customers[0]["customer_id"] if customers else None),
        width=340,
        border_color=border_color
    )

    name_field = ft.TextField(label=f"{t('customer_name')} *", width=340, border_color=border_color)
    phone_field = ft.TextField(label=f"{t('mobile_number')} *", width=340, border_color=border_color, hint_text="10-digit mobile number", max_length=10)
    alt_phone_field = ft.TextField(label=t("alternate_number"), width=340, border_color=border_color, max_length=10)
    email_field = ft.TextField(label=t("email"), width=340, border_color=border_color)
    address_field = ft.TextField(label=f"{t('address')} *", multiline=True, min_lines=2, max_lines=3, width=340, border_color=border_color)
    created_field = ft.TextField(label=f"{t('created_date')} *", width=165, border_color=border_color, hint_text="YYYY-MM-DD")
    updated_field = ft.TextField(label=f"{t('updated_date')} *", width=165, border_color=border_color, hint_text="YYYY-MM-DD")

    up_created_picker = ft.DatePicker(
        on_change=lambda e: (setattr(created_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update())
    )
    up_updated_picker = ft.DatePicker(
        on_change=lambda e: (setattr(updated_field, "value", e.control.value.strftime("%Y-%m-%d") if e.control.value else ""), page.update())
    )
    if hasattr(page, "overlay"):
        page.overlay.extend([up_created_picker, up_updated_picker])

    created_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(up_created_picker, "open", True) or page.update())
    updated_field.suffix = ft.IconButton(ft.Icons.CALENDAR_MONTH, on_click=lambda _: setattr(up_updated_picker, "open", True) or page.update())

    msg_text = ft.Text("", size=13)

    def on_load(e):
        cid = selected_id_dropdown.value
        if not cid:
            return
        data, code = api_get(f"/api/customers/{cid}")
        if code == 200:
            name_field.value = data.get("customer_name", "")
            phone_field.value = data.get("phone_number", "")
            alt_phone_field.value = data.get("alternate_number", "")
            email_field.value = data.get("email", "")
            address_field.value = data.get("address", "")
            created_field.value = data.get("created_date", "")
            updated_field.value = data.get("updated_date", "")
            msg_text.value = ""
            page.update()

    def on_clear(e):
        name_field.value = ""
        phone_field.value = ""
        alt_phone_field.value = ""
        email_field.value = ""
        address_field.value = ""
        created_field.value = ""
        updated_field.value = ""
        msg_text.value = ""
        page.update()

    def on_update(e):
        cid = selected_id_dropdown.value
        if not cid:
            msg_text.value = "Please select a customer to update."
            msg_text.color = "#D32F2F"
            page.update()
            return

        name = name_field.value.strip() if name_field.value else ""
        phone = phone_field.value.strip() if phone_field.value else ""
        alt_phone = alt_phone_field.value.strip() if alt_phone_field.value else ""
        address = address_field.value.strip() if address_field.value else ""
        c_date = created_field.value.strip() if created_field.value else ""
        u_date = updated_field.value.strip() if updated_field.value else ""

        if not name:
            msg_text.value = f"{t('customer_name')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not phone:
            msg_text.value = f"{t('mobile_number')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if len(phone) != 10 or not phone.isdigit():
            msg_text.value = t("error_phone_10_digits")
            msg_text.color = "#D32F2F"
            page.update()
            return

        if alt_phone and (len(alt_phone) != 10 or not alt_phone.isdigit()):
            msg_text.value = "Alternate number must contain exactly 10 digits."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not address:
            msg_text.value = f"{t('address')} is required."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not c_date:
            msg_text.value = f"{t('created_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        if not u_date:
            msg_text.value = f"{t('updated_date')} is required. Please select from calendar."
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "customer_name": name,
            "phone_number": phone,
            "alternate_number": alt_phone,
            "email": email_field.value.strip() if email_field.value else "",
            "address": address,
            "created_date": c_date,
            "updated_date": u_date
        }

        res, code = api_put(f"/api/customers/{cid}", payload)
        if code == 200:
            msg_text.value = t("success_update")
            msg_text.color = "#2E7D32"
            page.update()
        else:
            msg_text.value = res.get("detail", res.get("error", "Update failed"))
            msg_text.color = "#D32F2F"
            page.update()

    # Preload if initial id
    if selected_id_dropdown.value:
        on_load(None)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("update_customer"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Row([selected_id_dropdown, ft.ElevatedButton(t("load"), bgcolor="#1565C0", color="#FFFFFF", on_click=on_load)], spacing=8),
                name_field,
                phone_field,
                alt_phone_field,
                email_field,
                address_field,
                ft.Row([created_field, updated_field], spacing=10, width=340),
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

def create_customer_summary_view(page: ft.Page, customer_id: str, on_back):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"
    sub_text = "#A0A0A0" if is_dark else "#616161"

    data, code = api_get(f"/api/customers/{customer_id}/summary")
    if code != 200:
        return ft.Column([ft.Text("Customer not found", color="#D32F2F"), ft.ElevatedButton("Back", on_click=lambda e: on_back())])

    c = data["customer"]
    txns = data.get("transactions", [])
    items = data.get("items", [])
    payments = data.get("payments", [])
    perf = data.get("performance", {})

    total_credit = perf.get("total_credit", 0.0)
    total_paid = perf.get("total_paid", 0.0)
    pending = perf.get("pending_amount", 0.0)
    status_str = "Paid" if pending <= 0 else "Pending"

    def section_header(title):
        return ft.Container(
            content=ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color="#1565C0"),
            padding=ft.padding.only(top=14, bottom=6),
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )

    def info_row(label, val):
        return ft.Row(
            [
                ft.Text(f"{label}:", width=140, color=sub_text, size=13),
                ft.Text(str(val if val else "-"), weight=ft.FontWeight.W_500, color=text_color, size=13)
            ],
            spacing=4
        )

    # Vertical Summary List
    content_list = [
        ft.Row([
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: on_back()),
            ft.Text(f"{t('customer_summary')} - {c['customer_name']} ({c['customer_id']})", size=18, weight=ft.FontWeight.BOLD, color=text_color),
        ], spacing=8),
        section_header("CUSTOMER INFORMATION"),
        info_row(t("customer_id"), c["customer_id"]),
        info_row(t("customer_name"), c["customer_name"]),
        info_row(t("mobile_number"), c["phone_number"]),
        info_row(t("alternate_number"), c.get("alternate_number")),
        info_row(t("email"), c.get("email")),
        info_row(t("address"), c.get("address")),
        
        section_header("TRANSACTIONS"),
        info_row("Total Transactions", len(txns)),
        info_row("Total Credit", f"₹{total_credit:,.2f}"),
        info_row("Total Paid", f"₹{total_paid:,.2f}"),
        info_row("Pending", f"₹{pending:,.2f}"),
    ]

    # Credited Items list
    content_list.append(section_header("CREDITED ITEMS"))
    if items:
        for it in items:
            content_list.append(
                info_row(f"{it['item_id']} - {it['item_name']}", f"Qty: {it['quantity']} × ₹{it['unit_price']} = ₹{it['subtotal']:,.2f}")
            )
    else:
        content_list.append(ft.Text("No items credited yet.", size=13, color=sub_text))

    # Payments list
    content_list.append(section_header("PAYMENTS"))
    if payments:
        for p in payments:
            content_list.append(
                info_row(f"{p['payment_id']} ({p['payment_date']})", f"₹{p['payment_amount']:,.2f} via {p['payment_method']}")
            )
    else:
        content_list.append(ft.Text("No payments made yet.", size=13, color=sub_text))

    # Performance
    content_list.append(section_header("PERFORMANCE"))
    content_list.append(info_row("Performance", f"{perf.get('percentage', 0)}%"))
    content_list.append(info_row("Status", perf.get("status", "Good")))

    # Outstanding
    content_list.append(section_header("OUTSTANDING"))
    content_list.append(info_row("Total Due", f"₹{total_credit:,.2f}"))
    content_list.append(info_row("Total Paid", f"₹{total_paid:,.2f}"))
    content_list.append(info_row("Pending", f"₹{pending:,.2f}"))
    content_list.append(info_row("Status", status_str))

    return ft.Container(
        content=ft.Column(content_list, spacing=6, scroll=ft.ScrollMode.AUTO),
        bgcolor=card_bg,
        padding=24,
        border_radius=6,
        border=ft.border.all(1, border_color),
        width=560,
        expand=True
    )
