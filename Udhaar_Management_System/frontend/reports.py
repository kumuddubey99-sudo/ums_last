import flet as ft
from datetime import datetime, date
import os
import csv
from api import api_get
from language import t, get_language

def create_reports_view(page: ft.Page):
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    card_bg = "#1E1E1E" if is_dark else "#FFFFFF"
    text_color = "#FFFFFF" if is_dark else "#212121"
    border_color = "#333333" if is_dark else "#E0E0E0"
    doc_bg = "#242424" if is_dark else "#FAFAFA"

    customers, _ = api_get("/api/customers")
    if not isinstance(customers, list):
        customers = []

    txns, _ = api_get("/api/transactions")
    if not isinstance(txns, list):
        txns = []

    report_types = [
        "Customer Report",
        "Credit Transaction Report",
        "Credited Items Report",
        "Payment Report",
        "Outstanding Balance Report",
        "Customer Performance Summary Report",
        "Complete Summary Report"
    ]

    report_type_dropdown = ft.Dropdown(
        label="Report Type",
        options=[ft.dropdown.Option(rt) for rt in report_types],
        value="Customer Report",
        width=280,
        border_color=border_color
    )

    cust_options = [ft.dropdown.Option("", "All Customers")] + [
        ft.dropdown.Option(c["customer_id"], f"{c['customer_id']} - {c['customer_name']}")
        for c in customers
    ]
    customer_dropdown = ft.Dropdown(
        label=t("customers"),
        options=cust_options,
        value=customers[0]["customer_id"] if customers else "",
        width=280,
        border_color=border_color
    )

    txn_options = [ft.dropdown.Option("", "All Transactions")] + [
        ft.dropdown.Option(t_row["transaction_id"], f"{t_row['transaction_id']} - {t_row.get('customer_name', '')}")
        for t_row in txns
    ]
    txn_dropdown = ft.Dropdown(
        label=t("credit_transactions"),
        options=txn_options,
        value="",
        width=280,
        border_color=border_color
    )

    from_date_field = ft.TextField(label="From Date", value="", hint_text="YYYY-MM-DD", width=135, border_color=border_color)
    to_date_field = ft.TextField(label="To Date", value="", hint_text="YYYY-MM-DD", width=135, border_color=border_color)

    lang_dropdown = ft.Dropdown(
        label="Report Language",
        options=[
            ft.dropdown.Option("English"),
            ft.dropdown.Option("Hindi"),
            ft.dropdown.Option("Marathi"),
            ft.dropdown.Option("Malwari / Rajasthani")
        ],
        value="English",
        width=280,
        border_color=border_color
    )

    status_text = ft.Text("", size=13)
    preview_container = ft.Container(
        content=ft.Text("Click GENERATE REPORT to preview printable document.", color="#888888", size=13),
        padding=24,
        bgcolor=doc_bg,
        border=ft.border.all(1, border_color),
        border_radius=4,
        alignment=ft.alignment.center,
        width=620
    )

    current_report_data = {"data": None}

    def render_vertical_preview(data, r_lang):
        c_lines = []
        c_lines.append(ft.Text("NAV DURGA SUPER MARKET", size=18, weight=ft.FontWeight.BOLD, color="#1565C0", text_align=ft.TextAlign.CENTER))
        c_lines.append(ft.Text("UDHAAR MANAGEMENT SYSTEM", size=13, weight=ft.FontWeight.W_600, color=text_color, text_align=ft.TextAlign.CENTER))
        c_lines.append(ft.Text(f"{data.get('report_type', 'REPORT').upper()}", size=15, weight=ft.FontWeight.BOLD, color=text_color, text_align=ft.TextAlign.CENTER))
        c_lines.append(ft.Text(f"Generated: {data.get('generated_at', '')} | Language: {r_lang}", size=11, color="#888888", text_align=ft.TextAlign.CENTER))
        c_lines.append(ft.Divider(color=border_color, height=16))

        cust = data.get("customer")
        if cust:
            c_lines.append(ft.Text("Customer Information", weight=ft.FontWeight.BOLD, color="#1565C0", size=14))
            c_lines.append(ft.Text(f"Customer ID: {cust['customer_id']}", size=12, color=text_color))
            c_lines.append(ft.Text(f"Customer Name: {cust['customer_name']}", size=12, color=text_color))
            c_lines.append(ft.Text(f"Mobile: {cust['phone_number']}", size=12, color=text_color))
            if cust.get("email"):
                c_lines.append(ft.Text(f"Email: {cust['email']}", size=12, color=text_color))
            if cust.get("address"):
                c_lines.append(ft.Text(f"Address: {cust['address']}", size=12, color=text_color))
            c_lines.append(ft.Divider(color=border_color, height=16))

        perf = data.get("performance")
        if perf:
            c_lines.append(ft.Text("Summary & Performance", weight=ft.FontWeight.BOLD, color="#1565C0", size=14))
            c_lines.append(ft.Text(f"Total Transactions: {perf.get('total_transactions', 0)}", size=12, color=text_color))
            c_lines.append(ft.Text(f"Total Credit: ₹{perf.get('total_credit', 0):,.2f}", size=12, color=text_color))
            c_lines.append(ft.Text(f"Total Paid: ₹{perf.get('total_paid', 0):,.2f}", size=12, color=text_color))
            c_lines.append(ft.Text(f"Pending Amount: ₹{perf.get('pending_amount', 0):,.2f}", size=12, weight=ft.FontWeight.BOLD, color=text_color))
            c_lines.append(ft.Text(f"Performance: {perf.get('percentage', 0)}% ({perf.get('status', 'Good')})", size=12, color=text_color))
            c_lines.append(ft.Divider(color=border_color, height=16))

        txns_list = data.get("transactions", [])
        if txns_list:
            c_lines.append(ft.Text("Transactions", weight=ft.FontWeight.BOLD, color="#1565C0", size=14))
            for t_item in txns_list:
                c_lines.append(ft.Text(
                    f"• {t_item['transaction_id']} | Date: {t_item['transaction_date']} | Due: {t_item['due_date']} | Total: ₹{t_item['total_amount']:,.2f} | Status: {t_item.get('payment_status', 'Pending')}",
                    size=12, color=text_color
                ))
            c_lines.append(ft.Divider(color=border_color, height=16))

        items_list = data.get("items", [])
        if items_list:
            c_lines.append(ft.Text("Credited Items", weight=ft.FontWeight.BOLD, color="#1565C0", size=14))
            for i_item in items_list:
                c_lines.append(ft.Text(
                    f"• {i_item['item_id']} - {i_item['item_name']} | Qty: {i_item['quantity']} × ₹{i_item['unit_price']} = ₹{i_item['subtotal']:,.2f}",
                    size=12, color=text_color
                ))
            c_lines.append(ft.Divider(color=border_color, height=16))

        pays_list = data.get("payments", [])
        if pays_list:
            c_lines.append(ft.Text("Payments", weight=ft.FontWeight.BOLD, color="#1565C0", size=14))
            for p_item in pays_list:
                c_lines.append(ft.Text(
                    f"• {p_item['payment_id']} | Date: {p_item['payment_date']} | Amount: ₹{p_item['payment_amount']:,.2f} ({p_item['payment_method']})",
                    size=12, color=text_color
                ))
            c_lines.append(ft.Divider(color=border_color, height=16))

        recs = data.get("records", [])
        if recs:
            c_lines.append(ft.Text("Detailed Records", weight=ft.FontWeight.BOLD, color="#1565C0", size=14))
            for r in recs:
                if "pending_amount" in r and "customer_name" in r:
                    c_lines.append(ft.Text(
                        f"• {r.get('customer_id')} - {r.get('customer_name')}: Due: ₹{r.get('total_due', 0):,.2f} | Paid: ₹{r.get('total_paid', 0):,.2f} | Pending: ₹{r.get('pending_amount', 0):,.2f} ({r.get('status')})",
                        size=12, color=text_color
                    ))
                elif "percentage" in r:
                    c_lines.append(ft.Text(
                        f"• {r.get('customer_id')} - {r.get('customer_name')}: {r.get('percentage')}% ({r.get('status')}) | Txns: {r.get('total_transactions')}",
                        size=12, color=text_color
                    ))
                elif "customer" in r:
                    c_obj = r["customer"]
                    p_obj = r.get("performance", {})
                    c_lines.append(ft.Text(
                        f"• {c_obj['customer_id']} - {c_obj['customer_name']}: Credit: ₹{p_obj.get('total_credit', 0):,.2f} | Paid: ₹{p_obj.get('total_paid', 0):,.2f} | Pending: ₹{p_obj.get('pending_amount', 0):,.2f}",
                        size=12, color=text_color
                    ))

        return ft.Container(
            content=ft.Column(c_lines, spacing=4, scroll=ft.ScrollMode.AUTO),
            padding=24,
            bgcolor=doc_bg,
            border=ft.border.all(1, border_color),
            border_radius=4,
            width=620,
            alignment=ft.alignment.top_left
        )

    def on_generate(e):
        status_text.value = ""
        r_type = report_type_dropdown.value
        cid = customer_dropdown.value if customer_dropdown.value else None
        tid = txn_dropdown.value if txn_dropdown.value else None
        fd = from_date_field.value.strip() if from_date_field.value else None
        td = to_date_field.value.strip() if to_date_field.value else None
        rl = lang_dropdown.value

        if fd and td and fd > td:
            status_text.value = "From Date cannot be greater than To Date"
            status_text.color = "#D32F2F"
            page.update()
            return

        params = {
            "report_type": r_type,
            "report_lang": rl
        }
        if cid:
            params["customer_id"] = cid
        if tid:
            params["transaction_id"] = tid
        if fd:
            params["from_date"] = fd
        if td:
            params["to_date"] = td

        data, code = api_get("/api/reports", params)
        if code == 200:
            current_report_data["data"] = data
            preview_container.content = render_vertical_preview(data, rl)
            status_text.value = "Report generated successfully."
            status_text.color = "#2E7D32"
            page.update()
        else:
            status_text.value = data.get("detail", t("no_records_report"))
            status_text.color = "#D32F2F"
            page.update()

    def on_download_csv(e):
        data = current_report_data.get("data")
        if not data:
            status_text.value = "Please generate report first."
            status_text.color = "#D32F2F"
            page.update()
            return

        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(os.path.expanduser("~"), filename)

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Nav Durga Super Market - Udhaar Management System"])
                writer.writerow(["Report Type", data.get("report_type")])
                writer.writerow(["Generated At", data.get("generated_at")])
                writer.writerow([])

                if data.get("records"):
                    first = data["records"][0]
                    headers = list(first.keys())
                    writer.writerow(headers)
                    for r in data["records"]:
                        writer.writerow([r.get(h) for h in headers])
                elif data.get("transactions"):
                    writer.writerow(["Transaction ID", "Customer", "Date", "Due Date", "Total", "Paid", "Pending", "Status"])
                    for t_item in data["transactions"]:
                        writer.writerow([
                            t_item["transaction_id"],
                            t_item.get("customer_name", ""),
                            t_item["transaction_date"],
                            t_item["due_date"],
                            t_item["total_amount"],
                            t_item.get("total_paid", 0),
                            t_item.get("pending_amount", 0),
                            t_item.get("payment_status", "")
                        ])
                elif data.get("items"):
                    writer.writerow(["Item ID", "Transaction ID", "Item Name", "Quantity", "Unit Price", "Subtotal"])
                    for i_item in data["items"]:
                        writer.writerow([
                            i_item["item_id"],
                            i_item["transaction_id"],
                            i_item["item_name"],
                            i_item["quantity"],
                            i_item["unit_price"],
                            i_item["subtotal"]
                        ])
                elif data.get("payments"):
                    writer.writerow(["Payment ID", "Customer", "Date", "Amount", "Method", "Ref ID"])
                    for p_item in data["payments"]:
                        writer.writerow([
                            p_item["payment_id"],
                            p_item.get("customer_name", ""),
                            p_item["payment_date"],
                            p_item["payment_amount"],
                            p_item["payment_method"],
                            p_item.get("reference_id", "")
                        ])

            status_text.value = f"CSV saved to: {filename}"
            status_text.color = "#2E7D32"
            page.update()
        except Exception as ex:
            status_text.value = f"CSV error: {str(ex)}"
            status_text.color = "#D32F2F"
            page.update()

    def on_download_pdf(e):
        data = current_report_data.get("data")
        if not data:
            status_text.value = "Please generate report first."
            status_text.color = "#D32F2F"
            page.update()
            return

        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.path.expanduser("~"), filename)

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(filepath, pagesize=letter)
            y = 750
            c.setFont("Helvetica-Bold", 16)
            c.drawString(180, y, "NAV DURGA SUPER MARKET")
            y -= 20
            c.setFont("Helvetica", 12)
            c.drawString(200, y, "Udhaar Management System")
            y -= 20
            c.drawString(210, y, f"{data.get('report_type', 'REPORT')}")
            y -= 15
            c.line(50, y, 550, y)
            y -= 25

            c.setFont("Helvetica", 10)
            c.drawString(50, y, f"Generated: {data.get('generated_at', '')}")
            y -= 20

            cust = data.get("customer")
            if cust:
                c.setFont("Helvetica-Bold", 11)
                c.drawString(50, y, "CUSTOMER INFORMATION")
                y -= 15
                c.setFont("Helvetica", 10)
                c.drawString(60, y, f"Customer: {cust['customer_name']} ({cust['customer_id']}) | Mobile: {cust['phone_number']}")
                y -= 25

            perf = data.get("performance")
            if perf:
                c.setFont("Helvetica-Bold", 11)
                c.drawString(50, y, "SUMMARY & PERFORMANCE")
                y -= 15
                c.setFont("Helvetica", 10)
                c.drawString(60, y, f"Total Credit: Rs. {perf.get('total_credit', 0):,.2f} | Total Paid: Rs. {perf.get('total_paid', 0):,.2f} | Pending: Rs. {perf.get('pending_amount', 0):,.2f}")
                y -= 15
                c.drawString(60, y, f"Performance: {perf.get('percentage', 0)}% ({perf.get('status', 'Good')})")
                y -= 25

            c.save()
            status_text.value = f"PDF saved to: {filename}"
            status_text.color = "#2E7D32"
            page.update()
        except Exception as ex:
            status_text.value = f"PDF error: {str(ex)}"
            status_text.color = "#D32F2F"
            page.update()

    return ft.Column(
        [
            ft.Text(t("reports"), size=20, weight=ft.FontWeight.BOLD, color=text_color),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row([report_type_dropdown, lang_dropdown], spacing=12),
                        ft.Row([customer_dropdown, txn_dropdown], spacing=12),
                        ft.Row([from_date_field, to_date_field], spacing=10),
                        ft.Row(
                            [
                                ft.ElevatedButton(t("generate_report"), bgcolor="#1565C0", color="#FFFFFF", on_click=on_generate),
                                ft.OutlinedButton(t("download_pdf"), on_click=on_download_pdf),
                                ft.OutlinedButton(t("download_csv"), on_click=on_download_csv),
                            ],
                            spacing=12
                        ),
                        status_text,
                    ],
                    spacing=12
                ),
                padding=20,
                bgcolor=card_bg,
                border=ft.border.all(1, border_color),
                border_radius=6,
                width=620
            ),
            ft.Container(height=10),
            ft.Text("REPORT PREVIEW", size=15, weight=ft.FontWeight.BOLD, color=text_color),
            preview_container
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )
