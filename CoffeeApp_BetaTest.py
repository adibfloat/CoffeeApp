import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import os
import json
import sys
# =========================
# PATH APLIKASI
# =========================

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

receipt_folder = os.path.join(BASE_DIR, "receipts")
sales_file = os.path.join(BASE_DIR, "sales_data.json")

# =========================
# MODEL
# =========================
class Coffee:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class Order:
    TAX_RATE = 0
    DISCOUNT_RATE = 0

    def __init__(self):
        self.items = {}  # {coffee_name: {"coffee": object, "qty": jumlah}}

    def add_item(self, coffee):
        if coffee.name in self.items:
            self.items[coffee.name]["qty"] += 1
        else:
            self.items[coffee.name] = {"coffee": coffee, "qty": 1}

    def remove_item(self, coffee_name):
        if coffee_name in self.items:
            if self.items[coffee_name]["qty"] > 1:
                self.items[coffee_name]["qty"] -= 1
            else:
                del self.items[coffee_name]

    def subtotal(self):
        return sum(
            item["coffee"].price * item["qty"]
            for item in self.items.values()
        )

    def discount(self):
        if self.subtotal() > 15000:
            return self.subtotal() * self.DISCOUNT_RATE
        return 0

    def tax(self):
        return round(self.subtotal() - self.discount()) * self.TAX_RATE #-- Untuk dollar dsb bisa hapus round

    def total(self):
        return self.subtotal() - self.discount() + self.tax()

    def clear(self):
        self.items.clear()


# =========================
# GUI APP
# =========================
class CoffeeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coffee Shop Modern Adib Niatno ☕")
        # self.root.geometry("850x650")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.menu = [
            Coffee("Espresso", 2000),
            Coffee("Latte", 6000),
            Coffee("Americano", 4000),
            Coffee("Kopi Jawa", 7000)
        ]

        self.order = Order()
        self.sales_history = []
        self.load_sales_data()

        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.state("zoomed")

    def table_click(self, event):

        region = self.order_table.identify("region", event.x, event.y)

        if region != "cell":
            return

        column = self.order_table.identify_column(event.x)
        row = self.order_table.identify_row(event.y)

        if not row:
            return

        item = self.order_table.item(row)
        coffee_name = item["values"][0]

        # Kolom ke-3 = minus
        if column == "#3":
            self.order.remove_item(coffee_name)
            self.update_display()

        # Kolom ke-5 = plus
        elif column == "#5":
            coffee = self.order.items[coffee_name]["coffee"]
            self.order.add_item(coffee)
            self.update_display()

    def delete_order(self):

        selected = self.order_table.selection()

        if not selected:
            messagebox.showwarning("Warning", "Pilih pesanan yang ingin dihapus.")
            return

        item_id = selected[0]
        item = self.order_table.item(item_id)

        coffee_name = item["values"][0]

        # hapus seluruh pesanan
        if coffee_name in self.order.items:
            del self.order.items[coffee_name]

        self.update_display()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        main_frame.columnconfigure(0, weight=0)  # LEFT tetap
        main_frame.columnconfigure(1, weight=1)  # RIGHT fleksibel
        main_frame.rowconfigure(0, weight=1)

        # LEFT SIDE - MENU

        menu_frame = ttk.LabelFrame(main_frame, text="Menu", padding=10)
        menu_frame.grid(row=0, column=0, sticky="ns", padx=10)

        menu_frame.config(width=220)
        menu_frame.grid_propagate(False)

# ======================
# MODERN POS MENU BUTTON
# ======================

        menu_frame.columnconfigure(0, weight=1)
        menu_frame.columnconfigure(1, weight=1)

        btn_style = {
            "font": ("Arial", 12, "bold"),
            "height": 3,
            "bd": 0,
            "relief": "flat",
            "bg": "#34495e",
            "fg": "white",
            "activebackground": "#2c3e50",
            "activeforeground": "white"
        }

        for index, coffee in enumerate(self.menu):
            row = index // 2
            col = index % 2

            btn = tk.Button(
                menu_frame,
                text=f"{coffee.name}\nRp. {coffee.price}",
                command=lambda c=coffee: self.add_to_order(c),
                **btn_style
            )

            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # RIGHT SIDE - ORDER
        order_frame = ttk.LabelFrame(main_frame, text="Pesanan", padding=10)
        order_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        # order_frame.pack(side="right", fill="both", expand=True, padx=10)

        columns = ("Nama", "Harga", "Minus", "Qty", "Plus", "Total")

        self.order_table = ttk.Treeview(
            order_frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.order_table.heading("Nama", text="Nama")
        self.order_table.heading("Harga", text="Harga")
        self.order_table.heading("Minus", text="-")
        self.order_table.heading("Qty", text="Qty")
        self.order_table.heading("Plus", text="+")
        self.order_table.heading("Total", text="Total")

        self.order_table.column("Nama", anchor="center", width=120)
        self.order_table.column("Harga", anchor="center", width=120)
        self.order_table.column("Minus", anchor="center", width=10)
        self.order_table.column("Qty", anchor="center", width=40)
        self.order_table.column("Plus", anchor="center", width=10)
        self.order_table.column("Total", anchor="center", width=120)

        # for col in columns:
        #     self.order_table.heading(col, text=col)
        #     self.order_table.column(col, anchor="center")

        self.order_table.pack(fill="both", expand=True)
        self.order_table.bind("<Button-1>", self.table_click)

        # ttk.Button(order_frame, text="Hapus Item", command=self.remove_item).pack(pady=5)
        # ======================
        # MODERN POS BUTTON AREA
        # ======================
        button_frame = tk.Frame(order_frame)
        button_frame.pack(fill="x", pady=15)

        # Konfigurasi grid agar fleksibel
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.rowconfigure(0, weight=1)
        button_frame.rowconfigure(1, weight=1)

        btn_style = {
            "font": ("Arial", 12, "bold"),
            "height": 2,
            "bd": 0,
            "relief": "flat"
        }

        tk.Button(
            button_frame,
            text="🗑 Hapus Pesanan",
            command=self.delete_order,
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            **btn_style
        ).grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        tk.Button(
            button_frame,
            text="💳 Checkout",
            command=self.checkout,
            bg="#27ae60",
            fg="white",
            activebackground="#1e8449",
            **btn_style
        ).grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        tk.Button(
            button_frame,
            text="📊 Grafik Penjualan",
            command=self.show_sales_chart,
            bg="#2980b9",
            fg="white",
            activebackground="#1f618d",
            **btn_style
        ).grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        tk.Button(
            button_frame,
            text="❌ Exit",
            command=self.exit_app,
            bg="#2c3e50",
            fg="white",
            activebackground="#1b2631",
            **btn_style
        ).grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        # ======================

        self.total_label = ttk.Label(order_frame, text="Total: RP.0", font=("Arial", 15))
        self.total_label.pack(pady=10)

    def add_to_order(self, coffee):
        self.order.add_item(coffee)
        self.update_display()

    def remove_item(self):
        selected = self.order_table.selection()
        if selected:
            item = self.order_table.item(selected[0])
            coffee_name = item["values"][0]
            self.order.remove_item(coffee_name)
            self.update_display()
        else:
            messagebox.showwarning("Warning", "Pilih item yang ingin dihapus.")

    def update_display(self):
        # Hapus semua data lama
        for row in self.order_table.get_children():
            self.order_table.delete(row)

        # Masukkan data baru
        for name, data in self.order.items.items():
            coffee = data["coffee"]
            qty = data["qty"]
            total_price = coffee.price * qty

            self.order_table.insert(
                "",
                tk.END,
                values=(
                    coffee.name,
                    f"Rp {coffee.price:,.0f}",
                    "<",
                    qty,
                    ">",
                    f"Rp {total_price:,.0f}"
                )
            )

        total_text = (
            f"Subtotal: Rp.{self.order.subtotal():,.0f} | "
            f"Diskon: -Rp.{self.order.discount():,.0f} | "
            f"Pajak: Rp.{self.order.tax():,.0f} | "
            f"Total: Rp.{self.order.total():,.0f}"
        )

        self.total_label.config(text=total_text)

    def checkout(self):
        if not self.order.items:
            messagebox.showinfo("Info", "Pesanan kosong.")
            return

        total_amount = round(self.order.total())
        self.sales_history.append(total_amount)
        self.save_sales_data()

        filename = self.save_receipt()

        messagebox.showinfo(
            "Checkout Berhasil",
            f"Total pembayaran: Rp.{total_amount:,.0f}\nStruk disimpan di:\n{filename}"
        )

        self.order.clear()
        self.update_display()


    def save_receipt(self):

        if not os.path.exists(receipt_folder):
            os.makedirs(receipt_folder)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        filename = os.path.join(receipt_folder, f"receipt_{timestamp}.txt")

        with open(filename, "w", encoding="utf-8") as file:

            file.write("===== COFFEE SHOP RECEIPT =====\n")
            file.write(f"Tanggal: {datetime.datetime.now()}\n")
            file.write("-" * 30 + "\n")

            for name, data in self.order.items.items():
                coffee = data["coffee"]
                qty = data["qty"]
                total_price = coffee.price * qty

                file.write(f"{coffee.name} x{qty} - Rp {total_price:,.0f}\n")

            file.write("-" * 30 + "\n")
            file.write(f"Subtotal : Rp {self.order.subtotal():,.0f}\n")
            file.write(f"Diskon   : -Rp {self.order.discount():,.0f}\n")
            file.write(f"Pajak    : Rp {self.order.tax():,.0f}\n")
            file.write(f"Total    : Rp {self.order.total():,.0f}\n")
            file.write("=" * 30 + "\n")

        return filename

    def show_sales_chart(self):
        if not self.sales_history:
            messagebox.showinfo("Info", "Belum ada data penjualan hari ini.")
            return

        transactions = list(range(1, len(self.sales_history) + 1))
        totals = self.sales_history

        highest_value = max(totals)
        lowest_value = min(totals)

        plt.figure(figsize=(9, 5))

        colors = []
        for value in totals:
            if value == highest_value:
                colors.append("green")  # transaksi tertinggi
            elif value == lowest_value:
                colors.append("pink") # transaksi terendah
            else:
                colors.append("skyblue")

        bars = plt.bar(transactions, totals, color=colors)

        today = datetime.date.today().strftime("%d %B %Y")

        plt.title(f"Grafik Penjualan Harian\n{today}",
                fontsize=14,
                fontweight="bold")

        plt.xlabel("Transaksi Ke -")
        plt.ylabel("Total Penjualan (Rp)")
        plt.xticks(transactions)

        plt.grid(axis="y", linestyle="--", alpha=0.4)

        # Tampilkan nilai di atas batang
        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"Rp {height:,.0f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        # Statistik tambahan
        total_sales = sum(totals)
        avg_sales = total_sales / len(totals)

        plt.figtext(0.99, 0.01,
                    f"Total Hari Ini: Rp {total_sales:,.0f} | "
                    f"Rata-rata: Rp {avg_sales:,.0f}",
                    horizontalalignment="right")

        plt.tight_layout()
        plt.show()

    def load_sales_data(self):
        today = datetime.date.today().isoformat()

        if os.path.exists(sales_file):
            with open(sales_file, "r") as f:
                data = json.load(f)

            if data["date"] == today:
                self.sales_history = data["sales"]
            else:
                self.sales_history = []
                self.save_sales_data()
        else:
            self.sales_history = []
            self.save_sales_data()


    def save_sales_data(self):
        data = {
            "date": datetime.date.today().isoformat(),
            "sales": self.sales_history
        }

        with open(sales_file, "w") as f:
            json.dump(data, f)

    def exit_app(self):
        # Jika masih ada pesanan
        if self.order.items:
            confirm = messagebox.askyesno(
                "Konfirmasi Keluar",
                "Masih ada pesanan yang belum checkout.\nYakin ingin keluar?"
            )
        else:
            confirm = messagebox.askyesno(
                "Konfirmasi Keluar",
                "Yakin ingin keluar dari aplikasi?"
            )

        if confirm:
            self.root.destroy()

# =========================
# Jalankan Aplikasi
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = CoffeeApp(root)
    root.mainloop()
