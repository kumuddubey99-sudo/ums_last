import flet as ft
from language import t

def create_sidebar(page: ft.Page, on_navigate, on_logout, active_route="dashboard"):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    bg_color = "#1F1F1F" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"
    active_color = "#1565C0"

    menu_items = [
        {"route": "dashboard", "icon": ft.Icons.DASHBOARD_OUTLINED, "label": t("dashboard")},
        {"header": t("customers")},
        {"route": "customers_add", "icon": ft.Icons.PERSON_ADD_ALT_1_OUTLINED, "label": t("add_customer")},
        {"route": "customers_view", "icon": ft.Icons.PEOPLE_ALT_OUTLINED, "label": t("view_customers")},
        {"route": "customers_update", "icon": ft.Icons.MANAGE_ACCOUNTS_OUTLINED, "label": t("update_customer")},
        {"route": "customer_performance", "icon": ft.Icons.TRENDING_UP, "label": t("customer_performance")},
        {"header": t("credit_items")},
        {"route": "items_add", "icon": ft.Icons.ADD_SHOPPING_CART, "label": t("add_credit_item")},
        {"route": "items_view", "icon": ft.Icons.VIEW_LIST_OUTLINED, "label": t("view_credit_items")},
        {"route": "items_update", "icon": ft.Icons.EDIT_NOTE, "label": t("update_credit_item")},
        {"header": t("payments")},
        {"route": "payments_add", "icon": ft.Icons.ADD_CARD_OUTLINED, "label": t("add_payment")},
        {"route": "payments_view", "icon": ft.Icons.RECEIPT_LONG_OUTLINED, "label": t("view_payments")},
        {"route": "payments_update", "icon": ft.Icons.EDIT_CALENDAR_OUTLINED, "label": t("update_payment")},
        {"header": t("credit_transactions")},
        {"route": "transactions_add", "icon": ft.Icons.POST_ADD, "label": t("add_transaction")},
        {"route": "transactions_view", "icon": ft.Icons.MENU_BOOK_OUTLINED, "label": t("view_transactions")},
        {"route": "transactions_update", "icon": ft.Icons.EDIT_DOCUMENT, "label": t("update_transaction")},
        {"header": t("reports")},
        {"route": "outstanding_balance", "icon": ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, "label": t("outstanding_balance")},
        {"route": "reports", "icon": ft.Icons.ASSESSMENT_OUTLINED, "label": t("reports")},
    ]

    content_controls = []
    
    # Store title / brand indicator in sidebar header
    content_controls.append(
        ft.Container(
            content=ft.Text(t("shop_name"), weight=ft.FontWeight.BOLD, size=15, color=text_color),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=12),
            border=ft.border.only(bottom=ft.BorderSide(1, border_color))
        )
    )

    for item in menu_items:
        if "header" in item:
            content_controls.append(
                ft.Container(
                    content=ft.Text(item["header"], size=11, weight=ft.FontWeight.W_600, color="#757575"),
                    padding=ft.padding.only(left=16, top=12, bottom=4)
                )
            )
        else:
            is_active = active_route == item["route"]
            btn_bg = active_color if is_active else ft.Colors.TRANSPARENT
            btn_text_color = "#FFFFFF" if is_active else text_color

            def on_click_handler(e, r=item["route"]):
                on_navigate(r)

            content_controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(item["icon"], size=18, color=btn_text_color),
                            ft.Text(item["label"], size=13, weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.NORMAL, color=btn_text_color)
                        ],
                        spacing=10
                    ),
                    bgcolor=btn_bg,
                    border_radius=4,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    margin=ft.margin.symmetric(horizontal=8, vertical=2),
                    on_click=on_click_handler,
                    ink=True
                )
            )

    # Logout button at bottom
    content_controls.append(ft.Divider(height=20, color=border_color))
    content_controls.append(
        ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOGOUT, size=18, color="#D32F2F"),
                    ft.Text(t("logout"), size=13, weight=ft.FontWeight.BOLD, color="#D32F2F")
                ],
                spacing=10
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            on_click=lambda e: on_logout(),
            ink=True
        )
    )

    return ft.Container(
        content=ft.ListView(content_controls, spacing=0, padding=0),
        width=250,
        bgcolor=bg_color,
        border=ft.border.only(right=ft.BorderSide(1, border_color))
    )
