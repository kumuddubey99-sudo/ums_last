import flet as ft
from language import set_language, get_language, t
from sidebar import create_sidebar
from register import create_register_view
from login import create_login_view
from dashboard import create_dashboard_view
from customers import (
    create_add_customer_view,
    create_view_customers_view,
    create_update_customer_view,
    create_customer_summary_view
)
from customer_performance import create_customer_performance_view
from credit_items import (
    create_add_item_view,
    create_view_items_view,
    create_update_item_view
)
from payments import (
    create_add_payment_view,
    create_view_payments_view,
    create_update_payment_view
)
from credit_transactions import (
    create_add_transaction_view,
    create_view_transactions_view,
    create_update_transaction_view,
    create_transaction_summary_view
)
from outstanding_balance import create_outstanding_balance_view
from reports import create_reports_view
from api import api_get

def main(page: ft.Page):
    page.title = "Udhaar Management System - Nav Durga Super Market"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    # Application state
    state = {
        "current_view": "language_select",  # language_select -> register -> login -> app
        "active_route": "dashboard",
        "sidebar_open": True,
        "admin": None,
        "selected_customer_id": None,
        "selected_transaction_id": None,
        "search_results": None,
        "search_query": ""
    }

    # Central Theme Colors
    def get_colors():
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        return {
            "bg": "#121212" if is_dark else "#F5F7FA",
            "header": "#1F1F1F" if is_dark else "#1565C0",
            "footer": "#1A1A1A" if is_dark else "#ECEFF1",
            "text": "#FFFFFF" if is_dark else "#212121",
            "border": "#333333" if is_dark else "#E0E0E0",
            "search_bg": "#2B2B2B" if is_dark else "#FFFFFF",
            "search_text": "#FFFFFF" if is_dark else "#212121"
        }

    main_container = ft.Container(expand=True)

    def navigate_to(route: str):
        state["active_route"] = route
        state["search_results"] = None
        render_app()

    def logout():
        state["admin"] = None
        state["has_logged_out"] = True
        state["current_view"] = "language_select"
        render()

    def toggle_dark_mode(e):
        page.theme_mode = ft.ThemeMode.LIGHT if page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
        render()

    def toggle_sidebar(e):
        state["sidebar_open"] = not state["sidebar_open"]
        render_app()

    def on_search_change(e):
        q = e.control.value.strip() if e.control.value else ""
        state["search_query"] = q
        if not q:
            state["search_results"] = None
            render_app()
            return
        res, code = api_get("/api/search", {"q": q})
        if code == 200:
            state["search_results"] = res
        else:
            state["search_results"] = {"empty": True}
        render_app()

    def render_search_results(colors):
        sr = state.get("search_results")
        if not sr or "empty" in sr:
            return ft.Container(
                content=ft.Text(t("no_results"), color="#888888", size=14),
                padding=24,
                bgcolor="#1E1E1E" if page.theme_mode == ft.ThemeMode.DARK else "#FFFFFF",
                border=ft.border.all(1, colors["border"]),
                border_radius=6
            )

        c_list = [ft.Text(f"Search Results for: \"{state['search_query']}\"", size=16, weight=ft.FontWeight.BOLD, color=colors["text"])]
        
        # Customers
        custs = sr.get("customers", [])
        if custs:
            c_list.append(ft.Text("Matching Customers:", size=13, weight=ft.FontWeight.BOLD, color="#1565C0"))
            for c in custs:
                c_list.append(
                    ft.TextButton(
                        f"{c['customer_id']} - {c['customer_name']} ({c['phone_number']})",
                        on_click=lambda e, cid=c["customer_id"]: on_view_customer_summary(cid)
                    )
                )

        # Transactions
        txns = sr.get("transactions", [])
        if txns:
            c_list.append(ft.Text("Matching Transactions:", size=13, weight=ft.FontWeight.BOLD, color="#1565C0"))
            for t_item in txns:
                c_list.append(
                    ft.TextButton(
                        f"{t_item['transaction_id']} - {t_item.get('customer_name', '')} | Total: ₹{t_item['total_amount']:,.2f}",
                        on_click=lambda e, tid=t_item["transaction_id"]: on_view_txn_summary(tid)
                    )
                )

        return ft.Container(
            content=ft.Column(c_list, spacing=6),
            padding=20,
            bgcolor="#1E1E1E" if page.theme_mode == ft.ThemeMode.DARK else "#FFFFFF",
            border=ft.border.all(1, colors["border"]),
            border_radius=6
        )

    # View transitions
    def on_view_customer_summary(cid):
        state["selected_customer_id"] = cid
        state["active_route"] = "customer_summary"
        render_app()

    def on_view_txn_summary(tid):
        state["selected_transaction_id"] = tid
        state["active_route"] = "transaction_summary"
        render_app()

    def on_go_to_update_cust(cid):
        state["selected_customer_id"] = cid
        state["active_route"] = "customers_update"
        render_app()

    def on_go_to_update_item(iid):
        state["selected_item_id"] = iid
        state["active_route"] = "items_update"
        render_app()

    def on_go_to_update_pay(pid):
        state["selected_payment_id"] = pid
        state["active_route"] = "payments_update"
        render_app()

    def on_go_to_update_txn(tid):
        state["selected_transaction_id"] = tid
        state["active_route"] = "transactions_update"
        render_app()

    def render_app():
        colors = get_colors()
        is_dark = page.theme_mode == ft.ThemeMode.DARK

        # Top Header
        theme_icon = "☀️ Light Mode" if is_dark else "🌙 Dark Mode"
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.MENU,
                                icon_color="#FFFFFF",
                                tooltip="Menu",
                                on_click=toggle_sidebar
                            ),
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, color="#FFFFFF", size=24),
                            ft.Text(
                                t("app_title"),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color="#FFFFFF"
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Row(
                        [
                            # Compact search field 360px
                            ft.Container(
                                content=ft.TextField(
                                    hint_text=t("search_placeholder"),
                                    hint_style=ft.TextStyle(size=12, color="#9E9E9E"),
                                    prefix_icon=ft.Icons.SEARCH,
                                    border=ft.InputBorder.NONE,
                                    dense=True,
                                    content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
                                    text_size=13,
                                    color=colors["search_text"],
                                    on_change=on_search_change
                                ),
                                width=360,
                                height=38,
                                bgcolor=colors["search_bg"],
                                border_radius=6,
                                border=ft.border.all(1, colors["border"])
                            ),
                            # Language selector dropdown
                            ft.Dropdown(
                                value=get_language(),
                                options=[
                                    ft.dropdown.Option("English", "🌐 English"),
                                    ft.dropdown.Option("Hindi", "🌐 हिंदी"),
                                    ft.dropdown.Option("Marathi", "🌐 मराठी"),
                                    ft.dropdown.Option("Marwari", "🌐 मारवाड़ी"),
                                ],
                                width=135,
                                text_size=12,
                                content_padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                border_color="#555555" if is_dark else "#BBDEFB",
                                color="#FFFFFF",
                                on_change=lambda e: (set_language(e.control.value), render_app()),
                                tooltip="Change Language"
                            ),
                            ft.TextButton(
                                theme_icon,
                                style=ft.ButtonStyle(color="#FFFFFF"),
                                on_click=toggle_dark_mode
                            )
                        ],
                        spacing=16,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=colors["header"],
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, colors["border"]))
        )

        # Footer
        footer = ft.Container(
            content=ft.Row(
                [
                    ft.Text(f"{t('shop_name')} · {t('app_title')}", size=12, color="#757575"),
                    ft.Text("Nav Durga Super Market - TYIT", size=12, color="#757575")
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=colors["footer"],
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            border=ft.border.only(top=ft.BorderSide(1, colors["border"]))
        )

        # Main Content routing
        if state.get("search_results") is not None:
            content_view = render_search_results(colors)
        elif state["active_route"] == "dashboard":
            content_view = create_dashboard_view(page, on_view_transaction=on_view_txn_summary)
        elif state["active_route"] == "customers_add":
            content_view = create_add_customer_view(page, on_saved=lambda: navigate_to("customers_view"))
        elif state["active_route"] == "customers_view":
            content_view = create_view_customers_view(page, on_view_summary=on_view_customer_summary, on_go_to_update=on_go_to_update_cust)
        elif state["active_route"] == "customers_update":
            content_view = create_update_customer_view(page, initial_id=state.get("selected_customer_id"))
        elif state["active_route"] == "customer_summary":
            content_view = create_customer_summary_view(page, state.get("selected_customer_id"), on_back=lambda: navigate_to("customers_view"))
        elif state["active_route"] == "customer_performance":
            content_view = create_customer_performance_view(page, on_view_summary=on_view_customer_summary)
        elif state["active_route"] == "items_add":
            content_view = create_add_item_view(page, on_saved=lambda: navigate_to("items_view"))
        elif state["active_route"] == "items_view":
            content_view = create_view_items_view(page, on_go_to_update=on_go_to_update_item)
        elif state["active_route"] == "items_update":
            content_view = create_update_item_view(page, initial_id=state.get("selected_item_id"))
        elif state["active_route"] == "payments_add":
            content_view = create_add_payment_view(page, on_saved=lambda: navigate_to("payments_view"))
        elif state["active_route"] == "payments_view":
            content_view = create_view_payments_view(page, on_go_to_update=on_go_to_update_pay)
        elif state["active_route"] == "payments_update":
            content_view = create_update_payment_view(page, initial_id=state.get("selected_payment_id"))
        elif state["active_route"] == "transactions_add":
            content_view = create_add_transaction_view(page, on_saved=lambda: navigate_to("transactions_view"))
        elif state["active_route"] == "transactions_view":
            content_view = create_view_transactions_view(page, on_view_summary=on_view_txn_summary, on_go_to_update=on_go_to_update_txn)
        elif state["active_route"] == "transactions_update":
            content_view = create_update_transaction_view(page, initial_id=state.get("selected_transaction_id"))
        elif state["active_route"] == "transaction_summary":
            content_view = create_transaction_summary_view(page, state.get("selected_transaction_id"), on_back=lambda: navigate_to("transactions_view"))
        elif state["active_route"] == "outstanding_balance":
            content_view = create_outstanding_balance_view(page, on_view_summary=on_view_customer_summary)
        elif state["active_route"] == "reports":
            content_view = create_reports_view(page)
        else:
            content_view = create_dashboard_view(page)

        body_row = ft.Row(
            [
                create_sidebar(page, on_navigate=navigate_to, on_logout=logout, active_route=state["active_route"])
                if state["sidebar_open"] else ft.Container(width=0),
                ft.Container(
                    content=content_view,
                    bgcolor=colors["bg"],
                    padding=24,
                    expand=True,
                    alignment=ft.alignment.top_left
                )
            ],
            spacing=0,
            expand=True
        )

        main_container.content = ft.Column(
            [
                header,
                body_row,
                footer
            ],
            spacing=0,
            expand=True
        )
        page.bgcolor = colors["bg"]
        page.update()

    # Language selection screen
    def render_language_select():
        colors = get_colors()
        is_dark = page.theme_mode == ft.ThemeMode.DARK

        selected_lang_ref = {"lang": "English"}

        def choose_lang(l):
            clean_l = "Marwari" if "Malwari" in l or "Marwari" in l else l
            selected_lang_ref["lang"] = clean_l
            set_language(clean_l)
            if state.get("has_logged_out") or state.get("registered"):
                state["current_view"] = "login"
            else:
                state["current_view"] = "register"
            render()

        langs = [
            ("English", "English"),
            ("Hindi", "हिंदी"),
            ("Marathi", "मराठी"),
            ("Malwari / Rajasthani", "मारवाड़ी / राजस्थानी")
        ]

        buttons = []
        for code_name, display_name in langs:
            buttons.append(
                ft.ElevatedButton(
                    display_name,
                    width=280,
                    height=46,
                    bgcolor="#1565C0",
                    color="#FFFFFF",
                    on_click=lambda e, l=code_name: choose_lang(l)
                )
            )

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Nav Durga Super Market", size=14, weight=ft.FontWeight.W_600, color="#1565C0"),
                    ft.Text("Udhaar Management System", size=22, weight=ft.FontWeight.BOLD, color=colors["text"]),
                    ft.Container(height=10),
                    ft.Text("Select Language / भाषा चुनें", size=15, weight=ft.FontWeight.W_500, color=colors["text"]),
                    ft.Container(height=10),
                    ft.Column(buttons, spacing=12),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            bgcolor="#1E1E1E" if is_dark else "#FFFFFF",
            padding=36,
            border_radius=8,
            border=ft.border.all(1, colors["border"]),
            width=360,
            alignment=ft.alignment.center
        )

        main_container.content = ft.Container(
            content=card,
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=colors["bg"]
        )
        page.bgcolor = colors["bg"]
        page.update()

    def render_register():
        colors = get_colors()
        reg_view = create_register_view(
            page,
            on_register_success=lambda: go_to_login(),
            on_go_to_login=lambda: go_to_login()
        )
        main_container.content = ft.Container(
            content=reg_view,
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=colors["bg"]
        )
        page.bgcolor = colors["bg"]
        page.update()

    def render_login():
        colors = get_colors()
        login_view = create_login_view(
            page,
            on_login_success=lambda admin_info: on_logged_in(admin_info),
            on_go_to_register=lambda: go_to_register()
        )
        main_container.content = ft.Container(
            content=login_view,
            alignment=ft.alignment.center,
            expand=True,
            bgcolor=colors["bg"]
        )
        page.bgcolor = colors["bg"]
        page.update()

    def go_to_login():
        state["current_view"] = "login"
        render()

    def go_to_register():
        state["current_view"] = "register"
        render()

    def on_logged_in(admin_info):
        state["admin"] = admin_info
        state["current_view"] = "app"
        state["active_route"] = "dashboard"
        render()

    def render():
        if state["current_view"] == "language_select":
            render_language_select()
        elif state["current_view"] == "register":
            render_register()
        elif state["current_view"] == "login":
            render_login()
        else:
            render_app()

    page.add(main_container)
    render()

if __name__ == "__main__":
    ft.app(target=main)
