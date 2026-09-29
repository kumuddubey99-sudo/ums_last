import flet as ft
from api import api_post
from language import t

def create_login_view(page: ft.Page, on_login_success, on_go_to_register):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"

    username_field = ft.TextField(label=t("username"), width=320, border_color=border_color)
    password_field = ft.TextField(label=t("password"), password=True, can_reveal_password=True, width=320, border_color=border_color)
    error_msg = ft.Text("", color="#D32F2F", size=13)

    def on_login_click(e):
        error_msg.value = ""
        user = username_field.value.strip() if username_field.value else ""
        pwd = password_field.value if password_field.value else ""

        if not user or not pwd:
            error_msg.value = t("error_required")
            page.update()
            return

        res, code = api_post("/api/auth/login", {
            "username": user,
            "password": pwd
        })

        if code == 200:
            on_login_success(res.get("admin"))
        else:
            error_msg.value = res.get("detail", res.get("error", "Invalid username or password"))
            page.update()

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(t("shop_name"), size=14, weight=ft.FontWeight.W_600, color="#1565C0"),
                ft.Text(t("login"), size=22, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Container(height=10),
                username_field,
                password_field,
                error_msg,
                ft.Container(height=5),
                ft.ElevatedButton(
                    t("login"),
                    bgcolor="#1565C0",
                    color="#FFFFFF",
                    width=320,
                    height=42,
                    on_click=on_login_click
                ),
                ft.TextButton(
                    t("admin_registration"),
                    on_click=lambda e: on_go_to_register()
                )
            ],
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
