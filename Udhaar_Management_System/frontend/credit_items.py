import flet as ft
from api import api_get, api_post, api_put, api_delete
from language import t

def create_add_item_view(page: ft.Page, on_saved=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    next_id_res, _ = api_get("/api/items/next-id")
    item_id = next_id_res.get("next_id", "ITEM001")

    txns, _ = api_get("/api/transactions")
    if not isinstance(txns, list):
        txns = []

    txn_options = [
        ft.dropdown.Option(t_row["transaction_id"], f"{t_row['transaction_id']} - {t_row.get('customer_name', '')}")
        for t_row in txns
    ]

    id_field = ft.TextField(label=t("item_id"), value=item_id, disabled=True, width=340, border_color=border_color)
    txn_dropdown = ft.Dropdown(
        label=t("transaction_id"),
        options=txn_options,
        value=txns[0]["transaction_id"] if txns else None,
        width=340,
        border_color=border_color
    )
    name_field = ft.TextField(label=t("item_name"), width=340, border_color=border_color)
    qty_field = ft.TextField(label=t("quantity"), value="1", width=165, border_color=border_color)
    price_field = ft.TextField(label=t("unit_price"), value="0.0", width=165, border_color=border_color)
    subtotal_field = ft.TextField(label=t("subtotal"), value="0.00", disabled=True, width=340, border_color=border_color)

    msg_text = ft.Text("", size=13)

    def calc_subtotal(e):
        try:
            q = float(qty_field.value) if qty_field.value else 0.0
            p = float(price_field.value) if price_field.value else 0.0
            subtotal_field.value = f"{q * p:,.2f}"
            page.update()
        except ValueError:
            pass

    qty_field.on_change = calc_subtotal
    price_field.on_change = calc_subtotal

    def on_clear(e):
        name_field.value = ""
        qty_field.value = "1"
        price_field.value = "0.0"
        subtotal_field.value = "0.00"
        msg_text.value = ""
        page.update()

    def on_save(e):
        msg_text.value = ""
        if not txn_dropdown.value:
            msg_text.value = "Please select a valid transaction"
            msg_text.color = "#D32F2F"
            page.update()
            return
        if not name_field.value or not name_field.value.strip():
            msg_text.value = t("error_required")
            msg_text.color = "#D32F2F"
            page.update()
            return
        try:
            q = float(qty_field.value)
            p = float(price_field.value)
            if q <= 0 or p < 0:
                raise ValueError()
        except Exception:
            msg_text.value = "Invalid quantity or price"
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "transaction_id": txn_dropdown.value,
            "item_name": name_field.value.strip(),
            "quantity": q,
            "unit_price": p
        }
        res, code = api_post("/api/items", payload)
        if code == 200:
            msg_text.value = t("success_save")
            msg_text.color = "#2E7D32"
            on_clear(None)
            n_res, _ = api_get("/api/items/next-id")
            id_field.value = n_res.get("next_id", "")
            page.update()
            if on_saved:
                on_saved()
        else:
            msg_text.value = res.get("detail", res.get("error", "Failed to add item"))
            msg_text.color = "#D32F2F"
            page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("add_credit_item"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                id_field,
                txn_dropdown,
                name_field,
                ft.Row([qty_field, price_field], spacing=10, width=340),
                subtotal_field,
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

def create_view_items_view(page: ft.Page, on_go_to_update):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    items, _ = api_get("/api/items")
    if not isinstance(items, list):
        items = []

    msg_banner = ft.Text("", size=13)

    def delete_item_handler(iid):
        res, code = api_delete(f"/api/items/{iid}")
        if code == 200:
            msg_banner.value = t("success_delete")
            msg_banner.color = "#2E7D32"
            page.update()
        else:
            msg_banner.value = res.get("detail", "Error deleting item")
            msg_banner.color = "#D32F2F"
            page.update()

    rows = []
    for it in items:
        iid = it["item_id"]
        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(iid, weight=ft.FontWeight.BOLD, color="#1565C0")),
                    ft.DataCell(ft.Text(it["transaction_id"], color=text_color)),
                    ft.DataCell(ft.Text(it["item_name"], color=text_color)),
                    ft.DataCell(ft.Text(str(it["quantity"]), color=text_color)),
                    ft.DataCell(ft.Text(f"₹{it['unit_price']:,.2f}", color=text_color)),
                    ft.DataCell(ft.Text(f"₹{it['subtotal']:,.2f}", weight=ft.FontWeight.BOLD, color=text_color)),
                    ft.DataCell(ft.Text(it["credited_at"], color=text_color)),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(ft.Icons.EDIT, icon_size=18, tooltip=t("update"), on_click=lambda e, i=iid: on_go_to_update(i)),
                                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=18, icon_color="#D32F2F", tooltip=t("delete"), on_click=lambda e, i=iid: delete_item_handler(i)),
                            ],
                            spacing=0
                        )
                    )
                ]
            )
        )

    return ft.Column(
        [
            ft.Text(t("view_credit_items"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            msg_banner,
            ft.Container(
                content=ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text(t("item_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("transaction_id"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("item_name"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("quantity"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("unit_price"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("subtotal"), weight=ft.FontWeight.BOLD, color=text_color)),
                        ft.DataColumn(ft.Text(t("credited_at"), weight=ft.FontWeight.BOLD, color=text_color)),
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

def create_update_item_view(page: ft.Page, initial_id=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    items, _ = api_get("/api/items")
    if not isinstance(items, list):
        items = []

    txns, _ = api_get("/api/transactions")
    if not isinstance(txns, list):
        txns = []

    item_options = [
        ft.dropdown.Option(i["item_id"], f"{i['item_id']} - {i['item_name']}")
        for i in items
    ]
    txn_options = [
        ft.dropdown.Option(t_row["transaction_id"], f"{t_row['transaction_id']} - {t_row.get('customer_name', '')}")
        for t_row in txns
    ]

    selected_item_dropdown = ft.Dropdown(
        label=t("item_id"),
        options=item_options,
        value=initial_id if initial_id else (items[0]["item_id"] if items else None),
        width=340,
        border_color=border_color
    )

    txn_dropdown = ft.Dropdown(label=t("transaction_id"), options=txn_options, width=340, border_color=border_color)
    name_field = ft.TextField(label=t("item_name"), width=340, border_color=border_color)
    qty_field = ft.TextField(label=t("quantity"), width=165, border_color=border_color)
    price_field = ft.TextField(label=t("unit_price"), width=165, border_color=border_color)
    subtotal_field = ft.TextField(label=t("subtotal"), disabled=True, width=340, border_color=border_color)

    msg_text = ft.Text("", size=13)

    def calc_subtotal(e):
        try:
            q = float(qty_field.value) if qty_field.value else 0.0
            p = float(price_field.value) if price_field.value else 0.0
            subtotal_field.value = f"{q * p:,.2f}"
            page.update()
        except ValueError:
            pass

    qty_field.on_change = calc_subtotal
    price_field.on_change = calc_subtotal

    def on_load(e):
        iid = selected_item_dropdown.value
        if not iid:
            return
        data, code = api_get(f"/api/items/{iid}")
        if code == 200:
            txn_dropdown.value = data.get("transaction_id")
            name_field.value = data.get("item_name", "")
            qty_field.value = str(data.get("quantity", 1))
            price_field.value = str(data.get("unit_price", 0.0))
            subtotal_field.value = f"{data.get('subtotal', 0.0):,.2f}"
            msg_text.value = ""
            page.update()

    def on_clear(e):
        name_field.value = ""
        qty_field.value = "1"
        price_field.value = "0.0"
        subtotal_field.value = "0.00"
        msg_text.value = ""
        page.update()

    def on_update(e):
        iid = selected_item_dropdown.value
        if not iid or not txn_dropdown.value:
            msg_text.value = "Select item and transaction"
            msg_text.color = "#D32F2F"
            page.update()
            return
        try:
            q = float(qty_field.value)
            p = float(price_field.value)
            if q <= 0 or p < 0:
                raise ValueError()
        except Exception:
            msg_text.value = "Invalid quantity or price"
            msg_text.color = "#D32F2F"
            page.update()
            return

        payload = {
            "transaction_id": txn_dropdown.value,
            "item_name": name_field.value.strip(),
            "quantity": q,
            "unit_price": p
        }

        res, code = api_put(f"/api/items/{iid}", payload)
        if code == 200:
            msg_text.value = t("success_update")
            msg_text.color = "#2E7D32"
            page.update()
        else:
            msg_text.value = res.get("detail", "Update failed")
            msg_text.color = "#D32F2F"
            page.update()

    if selected_item_dropdown.value:
        on_load(None)

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("update_credit_item"), size=18, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Row([selected_item_dropdown, ft.ElevatedButton(t("load"), bgcolor="#1565C0", color="#FFFFFF", on_click=on_load)], spacing=8),
                txn_dropdown,
                name_field,
                ft.Row([qty_field, price_field], spacing=10, width=340),
                subtotal_field,
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
