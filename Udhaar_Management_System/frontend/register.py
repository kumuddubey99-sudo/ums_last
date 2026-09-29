import flet as ft
from api import api_post
from language import t

def create_register_view(page: ft.Page, on_register_success, on_go_to_login, on_back_to_language=None):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    admin_name_field = ft.TextField(label=t("admin_name"), width=320, border_color=border_color)
    role_field = ft.Dropdown(
        label=f"{t('role')} *",
        options=[
            ft.dropdown.Option("Admin"),
            ft.dropdown.Option("Manager"),
            ft.dropdown.Option("Staff"),
            ft.dropdown.Option("Cashier"),
        ],
        value="Admin",
        width=320,
        border_color=border_color,
    )
    username_field = ft.TextField(label=t("username"), width=320, border_color=border_color)
    password_field = ft.TextField(label=t("password"), password=True, can_reveal_password=True, width=320, border_color=border_color)
    confirm_password_field = ft.TextField(label=t("confirm_password"), password=True, can_reveal_password=True, width=320, border_color=border_color)
    error_msg = ft.Text("", color="#D32F2F", size=13)
    success_msg = ft.Text("", color="#2E7D32", size=13)

    def on_register_click(e):
        error_msg.value = ""
        success_msg.value = ""
        
        name = admin_name_field.value.strip() if admin_name_field.value else ""
        user = username_field.value.strip() if username_field.value else ""
        pwd = password_field.value if password_field.value else ""
        cpwd = confirm_password_field.value if confirm_password_field.value else ""

        if not name or not user or not pwd or not cpwd:
            error_msg.value = t("error_required")
            page.update()
            return
        if pwd != cpwd:
            error_msg.value = "Passwords do not match"
            page.update()
            return

        res, code = api_post("/api/auth/register", {
            "admin_name": name,
            "role": role_field.value or "Admin",
            "username": user,
            "password": pwd,
            "confirm_password": cpwd
        })

        if code == 200:
            success_msg.value = t("success_save")
            page.update()
            on_register_success()
        else:
            error_msg.value = res.get("detail", res.get("error", "Registration failed"))
            page.update()

    column_controls = [
        ft.Text(t("shop_name"), size=14, weight=ft.FontWeight.W_600, color="#1565C0"),
        ft.Text(t("admin_registration"), size=22, weight=ft.FontWeight.BOLD, color=text_color),
        ft.Container(height=10),
        admin_name_field,
        role_field,
        username_field,
        password_field,
        confirm_password_field,
        error_msg,
        success_msg,
        ft.Container(height=5),
        ft.ElevatedButton(
            t("register"),
            bgcolor="#1565C0",
            color="#FFFFFF",
            width=320,
            height=42,
            on_click=on_register_click
        ),
        ft.TextButton(
            t("already_registered"),
            on_click=lambda e: on_go_to_login()
        )
    ]
    if on_back_to_language:
        column_controls.append(
            ft.TextButton(
                f"← {t('select_language')}",
                on_click=lambda e: on_back_to_language()
            )
        )

    return ft.Container(
        content=ft.Column(
            column_controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12
        ),
        bgcolor=card_bg,
        padding=32,
        border_radius=8,
        border=ft.border.all(1, border_color),
        alignment=ft.alignment.center,
        width=380
    )
