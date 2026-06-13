import mysql.connector as mys
import pandas as pd
import datetime
import sys
try:
    import bcrypt
except ImportError:
    print("ERROR: bcrypt is required. Run: pip install bcrypt")
    sys.exit(1)
from tkinter import *
from tkinter import messagebox
from pandastable import Table
from tkcalendar import DateEntry
import os
from dotenv import load_dotenv
load_dotenv()

BG      = "#F1F5F9"
CARD    = "#FFFFFF"
PRIMARY = "#2563EB"
P_ACT   = "#1D4ED8"
DANGER  = "#EF4444"
SUCCESS = "#10B981"
TEXT    = "#1E293B"
SUBTEXT = "#64748B"
BORDER  = "#CBD5E1"
LOGOUT  = "#E2E8F0"


class gui:
    def __init__(self):
        try:
            self.db = mys.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                passwd=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE")
            )
        except Exception:
            self.database_create()
        self.migrate_db()
        self.work = True
        self.window = Tk()
        self.window.protocol("WM_DELETE_WINDOW", lambda: exit(0))
        self.window.title("Inventory Management System")
        self.window.geometry("860x660")
        self.window.configure(bg=BG)
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after(100, self.loginscreen)
        self.window.mainloop()

    # ── helpers ──────────────────────────────────────────────

    def _btn(self, parent, text, command, bg=PRIMARY, fg="white", width=None, padx=24, pady=10):
        kw = dict(
            text=text, command=command, bg=bg, fg=fg,
            activebackground=P_ACT if bg == PRIMARY else BORDER,
            activeforeground=fg, font=("Arial", 11, "bold"),
            relief=FLAT, bd=0, cursor="hand2", padx=padx, pady=pady
        )
        if width:
            kw["width"] = width
        return Button(parent, **kw)

    def _lbl(self, parent, text, size=11, bold=False, color=TEXT, bg=None):
        return Label(parent, text=text,
                     font=("Arial", size, "bold" if bold else "normal"),
                     bg=bg or parent.cget("bg"), fg=color)

    def _entry(self, parent, var, show=None, width=32, **kw):
        kwargs = dict(textvariable=var, width=width,
                      font=("Arial", 12), relief=SOLID, bd=1,
                      bg="white", fg=TEXT, **kw)
        if show is not None:
            kwargs["show"] = show
        return Entry(parent, **kwargs)

    def _screen(self):
        self.window.configure(bg=BG)
        self.f2 = Frame(self.window, bg=BG, padx=50, pady=36)
        self.f2.place(relx=0.5, rely=0.5, anchor="center")
        return self.f2

    def _card(self, parent, padx=36, pady=28):
        return Frame(parent, bg=CARD, padx=padx, pady=pady,
                     highlightthickness=1, highlightbackground=BORDER)

    def _section_title(self, parent, text, row=0):
        self._lbl(parent, text, size=22, bold=True, bg=BG
                  ).grid(row=row, column=0, columnspan=4, sticky="W", pady=(0, 20))

    def _menu_btn(self, parent, text, row, command):
        b = Button(parent, text=text, command=command,
                   bg=PRIMARY, fg="white", activebackground=P_ACT, activeforeground="white",
                   font=("Arial", 12, "bold"), relief=FLAT, bd=0, cursor="hand2",
                   pady=14, width=38)
        b.grid(row=row, column=0, columnspan=2, pady=5, sticky="EW")
        return b

    def _logout_btn(self, parent, row, command):
        Button(parent, text="Log Out", command=command,
               bg=LOGOUT, fg=TEXT, activebackground=BORDER,
               font=("Arial", 12), relief=FLAT, bd=0, cursor="hand2",
               pady=14, width=38
               ).grid(row=row, column=0, columnspan=2, pady=5, sticky="EW")

    # ── DB ───────────────────────────────────────────────────

    def database_create(self):
        self.db = mys.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            passwd=os.getenv("DB_PASSWORD")
        )
        self.cu = self.db.cursor()
        self.cu.execute("create database inventory;")
        self.db = mys.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            passwd=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        self.cu = self.db.cursor()
        self.cu.execute("create table Users (IdNo int PRIMARY KEY AUTO_INCREMENT, Name varchar(20), UserType varchar(15), password varchar(300))")
        self.cu.execute("create table Products (P_Id int primary key, ProductName varchar(20), SalePrice int, SupplierName varchar(15))")
        self.cu.execute("create table Storage (P_Id int, ProductName varchar(20), PurchaseCost int, pqty int, Currentquantity int, Purchasedate date, FOREIGN KEY (P_Id) REFERENCES Products (P_Id) ON DELETE CASCADE)")
        self.cu.execute("create table CustomerOrder (P_Id int, ProductName varchar(20), Name varchar(20), BillNo int, Quantity int, SaleDate date, Total int, foreign key(P_Id) references Products(P_Id))")
        self.db.commit()

    def migrate_db(self):
        cu = self.db.cursor()
        try:
            cu.execute("""
                SELECT EXTRA FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'Users'
                AND COLUMN_NAME = 'IdNo'
            """)
            result = cu.fetchone()
            if result and 'auto_increment' not in result[0].lower():
                cu.execute("SET @r = 0")
                cu.execute("UPDATE Users SET IdNo = (@r := @r + 1) ORDER BY IdNo")
                self.db.commit()
                cu.execute("ALTER TABLE Users MODIFY COLUMN IdNo INT PRIMARY KEY AUTO_INCREMENT")
                self.db.commit()
        except Exception as e:
            print(f"Schema migration warning: {e}")

    # ── Login ────────────────────────────────────────────────

    def loginscreen(self):
        self.window.configure(bg="#1E293B")
        self.f = Frame(self.window, bg="#1E293B")
        self.f.place(relx=0.5, rely=0.5, anchor="center")

        Label(self.f, text="Inventory Management System",
              font=("Arial", 20, "bold"), bg="#1E293B", fg="white"
              ).grid(row=0, column=0, pady=(0, 24))

        card = self._card(self.f, padx=44, pady=30)
        card.grid(row=1, column=0)

        Label(card, text="Welcome back",
              font=("Arial", 16, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=0, columnspan=2, pady=(0, 2))
        Label(card, text="Sign in to your account",
              font=("Arial", 10), bg=CARD, fg=SUBTEXT
              ).grid(row=1, column=0, columnspan=2, pady=(0, 18))

        Label(card, text="Username", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=2, column=0, columnspan=2, sticky="W", pady=(0, 3))
        self.v = StringVar()
        self.e1 = self._entry(card, self.v)
        self.e1.grid(row=3, column=0, columnspan=2, sticky="EW", pady=(0, 12))

        Label(card, text="Password", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=4, column=0, columnspan=2, sticky="W", pady=(0, 3))
        self.v2 = StringVar()
        self.e2 = self._entry(card, self.v2, show="*")
        self.e2.grid(row=5, column=0, columnspan=2, sticky="EW", pady=(0, 18))

        Button(card, text="Login", command=self.users,
               bg=PRIMARY, fg="white", activebackground=P_ACT, activeforeground="white",
               font=("Arial", 12, "bold"), relief=FLAT, bd=0, cursor="hand2",
               pady=10, width=32
               ).grid(row=6, column=0, columnspan=2, sticky="EW")

        self.l4 = Label(card, text="", fg=DANGER, font=("Arial", 11), bg=CARD)
        self.l4.grid(row=7, column=0, columnspan=2, pady=(10, 0))

        self.e1.focus()
        self.window.bind("<Return>", lambda e: self.users())

    def users(self):
        username = self.e1.get()
        password = self.e2.get()
        cu = self.db.cursor()
        cu.execute("SELECT COUNT(*) FROM Users")
        count = cu.fetchone()[0]
        if count == 0:
            self.f.destroy()
            self.window.unbind("<Return>")
            self.window.configure(bg=BG)
            self.create_first_admin()
            return
        self.checklogin(username, password)

    def create_first_admin(self):
        self.window.configure(bg=BG)
        outer = Frame(self.window, bg=BG)
        outer.place(relx=0.5, rely=0.5, anchor="center")
        self.f_setup = outer

        Label(outer, text="Create Admin Account",
              font=("Arial", 22, "bold"), bg=BG, fg=TEXT
              ).grid(row=0, column=0, columnspan=2, pady=(0, 6))
        Label(outer, text="Set up your first administrator account",
              font=("Arial", 11), bg=BG, fg=SUBTEXT
              ).grid(row=1, column=0, columnspan=2, pady=(0, 24))

        card = self._card(outer, padx=50, pady=36)
        card.grid(row=2, column=0, columnspan=2)

        Label(card, text="Username", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v1 = StringVar()
        Entry(card, textvariable=v1, width=32, font=("Arial", 12),
              relief=SOLID, bd=1
              ).grid(row=1, column=0, columnspan=2, sticky="EW", pady=(0, 16))

        Label(card, text="Password", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=2, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v2 = StringVar()
        Entry(card, textvariable=v2, show="*", width=32, font=("Arial", 12),
              relief=SOLID, bd=1
              ).grid(row=3, column=0, columnspan=2, sticky="EW", pady=(0, 24))

        l_err = Label(card, text="", fg=DANGER, font=("Arial", 11), bg=CARD)
        l_err.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        def create():
            name = v1.get().strip()
            pwd = v2.get()
            if not name:
                l_err.config(text="Username required")
                return
            if not pwd:
                l_err.config(text="Password required")
                return
            hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
            cu = self.db.cursor()
            cu.execute(
                "INSERT INTO Users (Name, UserType, password) VALUES (%s, %s, %s)",
                (name, 'admin', hashed)
            )
            self.db.commit()
            self.f_setup.destroy()
            self.loginscreen()

        Button(card, text="Create Admin Account", command=create,
               bg=PRIMARY, fg="white", activebackground=P_ACT,
               font=("Arial", 12, "bold"), relief=FLAT, bd=0, cursor="hand2",
               pady=12, width=32
               ).grid(row=4, column=0, columnspan=2, sticky="EW")

    def checklogin(self, username, password):
        cu = self.db.cursor()
        cu.execute("SELECT Name, password, UserType FROM Users WHERE Name = %s", (username,))
        user = cu.fetchone()
        if user is None:
            self.l4.config(text="Invalid username or password")
            self.e1.delete(0, END)
            self.e2.delete(0, END)
            return
        stored_pwd = user[1]
        authenticated = False
        if stored_pwd.startswith('$2b$') or stored_pwd.startswith('$2a$'):
            authenticated = bcrypt.checkpw(password.encode(), stored_pwd.encode())
        else:
            if password == stored_pwd:
                authenticated = True
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                cu2 = self.db.cursor()
                cu2.execute("UPDATE Users SET password = %s WHERE Name = %s", (hashed, username))
                self.db.commit()
        if authenticated:
            self.f.destroy()
            self.window.unbind("<Return>")
            self.window.configure(bg=BG)
            if user[2] == "admin":
                self.adminscreen()
            else:
                self.employeescreen()
        else:
            self.l4.config(text="Invalid username or password")
            self.e1.delete(0, END)
            self.e2.delete(0, END)

    # ── Menus ─────────────────────────────────────────────────

    def adminscreen(self):
        f = self._screen()
        self._section_title(f, "Admin Dashboard")
        self._menu_btn(f, "View Reports",     1, lambda: [f.destroy(), self.view_stats(0)])
        self._menu_btn(f, "Remove Employee",  2, lambda: [f.destroy(), self.remove_employeescreen()])
        self._menu_btn(f, "Add User",         3, lambda: [f.destroy(), self.add_userscreen()])
        self._logout_btn(f,                   4, lambda: [f.destroy(), self.loginscreen()])

    def employeescreen(self):
        f = self._screen()
        self._section_title(f, "Employee Menu")
        self._menu_btn(f, "Add Product",    1, lambda: [f.destroy(), self.add_product()])
        self._menu_btn(f, "Edit Product",   2, lambda: [f.destroy(), self.edit_product()])
        self._menu_btn(f, "Customer Order", 3, lambda: [f.destroy(), self.customerorder()])
        self._menu_btn(f, "View Reports",   4, lambda: [f.destroy(), self.view_stats(1)])
        self._logout_btn(f,                 5, lambda: [f.destroy(), self.loginscreen()])

    def view_stats(self, p):
        f = self._screen()
        self._section_title(f, "Reports")
        self._menu_btn(f, "Product Report",        1, lambda: [f.destroy(), self.productreport(p)])
        self._menu_btn(f, "Staff Report",          2, lambda: [f.destroy(), self.staffreport(p)])
        self._menu_btn(f, "Storage Report",        3, lambda: [f.destroy(), self.storagereport(p)])
        self._menu_btn(f, "Customer Order Report", 4, lambda: [f.destroy(), self.customer_orderreport(p)])
        back = (lambda: [f.destroy(), self.employeescreen()]) if p == 1 else (lambda: [f.destroy(), self.adminscreen()])
        Button(f, text="Back", command=back,
               bg=LOGOUT, fg=TEXT, activebackground=BORDER,
               font=("Arial", 12), relief=FLAT, bd=0, cursor="hand2",
               pady=14, width=38
               ).grid(row=5, column=0, columnspan=2, pady=5, sticky="EW")

    # ── Reports ──────────────────────────────────────────────

    def _report_screen(self, query, p, back_fn=None):
        self.window.configure(bg=BG)
        self.f2 = Frame(self.window, bg=BG)
        self.f2.pack(fill=BOTH, expand=True, padx=30, pady=20)

        back = back_fn or (lambda: [self.f2.destroy(), self.view_stats(p)])
        self._btn(self.f2, "Back", back, bg=LOGOUT, fg=TEXT
                  ).pack(anchor="w", pady=(0, 12))

        cu = self.db.cursor()
        cu.execute(query)
        header = list(cu.column_names)
        rows = cu.fetchall()
        table = pd.DataFrame(rows, columns=header) if rows else pd.DataFrame(columns=header)
        pt = Table(self.f2, dataframe=table, showtoolbar=True, showstatusbar=True)
        pt.pack(fill=BOTH, expand=True)
        pt.show()

    def productreport(self, p):
        self._report_screen("select * from products", p)

    def staffreport(self, p):
        self._report_screen("select Idno, Name, usertype from users", p)

    def customer_orderreport(self, p):
        self._report_screen("select * from customerorder", p)

    def storagereport(self, p):
        back = (lambda: [self.f2.destroy(), self.edit_product()]) if p == 2 else None
        self._report_screen("select * from storage", p, back)

    # ── Validation ───────────────────────────────────────────

    def validate1(self, value):
        cu = self.db.cursor()
        if not value.isnumeric():
            self.l9.config(text="Product ID must be a number", fg=DANGER)
            self.work = False
            return False
        cu.execute("SELECT * FROM Products WHERE P_Id = %s", (int(value),))
        if cu.fetchone() is not None:
            self.l9.config(text="Product ID already exists", fg=DANGER)
            self.work = False
            return False
        self.l9.config(text="")
        self.work = True
        return True

    def validate2(self, value):
        cu = self.db.cursor()
        if not value.isnumeric():
            self.l10.config(text="Product ID must be a number", fg=DANGER)
            self.work = False
            return False
        cu.execute("SELECT * FROM Products WHERE P_Id = %s", (int(value),))
        if cu.fetchone() is None:
            self.l10.config(text="Product ID does not exist", fg=DANGER)
            self.work = False
            return False
        self.l10.config(text="")
        self.work = True
        return True

    # ── Add Product ──────────────────────────────────────────

    def add_product(self):
        self.f2 = self._screen()
        self._section_title(self.f2, "Add Product")
        valid1 = (self.window.register(self.validate1), "%P")

        card = self._card(self.f2)
        card.grid(row=1, column=0, sticky="EW")
        card.grid_columnconfigure((0, 1), weight=1)

        def row(parent, label, r, col=0, **kw):
            Label(parent, text=label, font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
                  ).grid(row=r*2, column=col, sticky="W", pady=(8, 2), padx=(0, 20))

        row(card, "Product ID",    0, 0); v1 = StringVar()
        self.e1 = Entry(card, textvariable=v1, width=24, font=("Arial", 12), relief=SOLID, bd=1, validate='focusout', validatecommand=valid1)
        self.e1.grid(row=1, column=0, sticky="EW", padx=(0, 20), pady=(0, 4))

        row(card, "Product Name",  1, 0); v2 = StringVar()
        self.e2 = Entry(card, textvariable=v2, width=24, font=("Arial", 12), relief=SOLID, bd=1)
        self.e2.grid(row=3, column=0, sticky="EW", padx=(0, 20), pady=(0, 4))

        row(card, "Supplier Name", 2, 0); v3 = StringVar()
        self.e3 = Entry(card, textvariable=v3, width=24, font=("Arial", 12), relief=SOLID, bd=1)
        self.e3.grid(row=5, column=0, sticky="EW", padx=(0, 20), pady=(0, 4))

        row(card, "Quantity",      0, 1); v4 = StringVar()
        self.e4 = Spinbox(card, from_=0, to=10000000, textvariable=v4, width=24, font=("Arial", 12), relief=SOLID, bd=1)
        self.e4.grid(row=1, column=1, sticky="EW", pady=(0, 4))

        row(card, "Purchase Cost", 1, 1); v5 = StringVar()
        self.e5 = Entry(card, textvariable=v5, width=24, font=("Arial", 12), relief=SOLID, bd=1)
        self.e5.grid(row=3, column=1, sticky="EW", pady=(0, 4))

        row(card, "MRP (Sale Price)", 2, 1); v6 = StringVar()
        self.e6 = Entry(card, textvariable=v6, width=24, font=("Arial", 12), relief=SOLID, bd=1)
        self.e6.grid(row=5, column=1, sticky="EW", pady=(0, 4))

        Label(card, text="Purchase Date", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=6, column=0, sticky="W", pady=(8, 2))
        v7 = StringVar()
        cal = DateEntry(card, selectmode='day', textvariable=v7, font=("Arial", 11))
        cal.grid(row=7, column=0, sticky="W", pady=(0, 8))

        self.l9 = Label(card, text="", fg=DANGER, font=("Arial", 11), bg=CARD)
        self.l9.grid(row=9, column=0, columnspan=2, pady=(4, 0))

        bf = Frame(card, bg=CARD)
        bf.grid(row=8, column=0, columnspan=2, sticky="W", pady=(16, 0))
        self._btn(bf, "Add Product", lambda: self.addprod(v1, v2, v3, v4, v5, v6, cal)
                  ).pack(side=LEFT, padx=(0, 8))
        self._btn(bf, "Back", lambda: [self.f2.destroy(), self.employeescreen()],
                  bg=LOGOUT, fg=TEXT).pack(side=LEFT)

    def addprod(self, v1, v2, v3, v4, v5, v6, cal):
        if self.work:
            cu = self.db.cursor()
            cu.execute(
                "INSERT INTO Products VALUES (%s, %s, %s, %s)",
                (int(v1.get()), v2.get(), int(v6.get()), v3.get())
            )
            self.db.commit()
            self.storage(v1, v2, v4, v5, cal)
        else:
            self.l9.config(text="Invalid Product ID", fg=DANGER)

    def storage(self, v1, v2, v4, v5, cal):
        cu = self.db.cursor()
        purchase_date = "{0}".format(cal.get_date())
        year, month, day = map(int, purchase_date.split("-"))
        purchase_date = datetime.date(year, month, day)
        cu.execute(
            "INSERT INTO Storage VALUES (%s, %s, %s, %s, %s, %s)",
            (int(v1.get()), v2.get(), int(v5.get()), int(v4.get()), int(v4.get()), purchase_date)
        )
        self.db.commit()
        self.l9.config(text="Product added successfully", fg=SUCCESS)

    # ── Edit Product ─────────────────────────────────────────

    def edit_product(self):
        self.f2 = self._screen()
        self._section_title(self.f2, "Edit Product")
        valid1 = (self.window.register(self.validate2), "%P")

        card = self._card(self.f2)
        card.grid(row=1, column=0, sticky="EW")
        card.grid_columnconfigure(0, weight=1)

        Label(card, text="Product ID", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v1 = StringVar()
        self.e1 = Entry(card, validate='focusout', textvariable=v1, width=32,
                        font=("Arial", 12), relief=SOLID, bd=1,
                        validatecommand=valid1)
        self.e1.grid(row=1, column=0, columnspan=2, sticky="EW", pady=(0, 16))

        Label(card, text="New Quantity to Add", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=2, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v4 = StringVar()
        self.e4 = Spinbox(card, from_=0, to=10000000, textvariable=v4, width=32,
                          font=("Arial", 12), relief=SOLID, bd=1)
        self.e4.grid(row=3, column=0, columnspan=2, sticky="EW", pady=(0, 20))

        self.l10 = Label(card, text="", fg=DANGER, font=("Arial", 11), bg=CARD)
        self.l10.grid(row=6, column=0, columnspan=2, pady=(8, 0))

        bf1 = Frame(card, bg=CARD)
        bf1.grid(row=4, column=0, columnspan=2, sticky="W", pady=(0, 8))
        self._btn(bf1, "Update Quantity", lambda: self.edit(v1, v4)).pack(side=LEFT, padx=(0, 8))
        self._btn(bf1, "View Products",
                  lambda: [self.f2.destroy(), self.storagereport(2)],
                  bg=LOGOUT, fg=TEXT).pack(side=LEFT)

        bf2 = Frame(card, bg=CARD)
        bf2.grid(row=5, column=0, columnspan=2, sticky="W")
        self._btn(bf2, "Delete Product", lambda: self.deleteprod(v1),
                  bg=DANGER).pack(side=LEFT, padx=(0, 8))
        self._btn(bf2, "Back", lambda: [self.f2.destroy(), self.employeescreen()],
                  bg=LOGOUT, fg=TEXT).pack(side=LEFT)

    def edit(self, v1, v4):
        if self.work:
            cu = self.db.cursor()
            cu.execute(
                "UPDATE Storage SET CurrentQuantity = CurrentQuantity + %s WHERE P_Id = %s",
                (int(v4.get()), int(v1.get()))
            )
            self.db.commit()
            self.l10.config(text="Quantity updated successfully", fg=SUCCESS)
        else:
            self.l10.config(text="Invalid Product ID", fg=DANGER)

    def deleteprod(self, v1):
        if self.work:
            cu = self.db.cursor()
            cu.execute("DELETE FROM Products WHERE P_Id = %s", (int(v1.get()),))
            self.db.commit()
            self.l10.config(text="Product deleted", fg=SUCCESS)
        else:
            self.l10.config(text="Invalid Product ID", fg=DANGER)

    # ── Add User ─────────────────────────────────────────────

    def add_userscreen(self):
        self.f2 = self._screen()
        self._section_title(self.f2, "Add User")

        card = self._card(self.f2)
        card.grid(row=1, column=0, sticky="EW")
        card.grid_columnconfigure(0, weight=1)

        Label(card, text="Username", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v1 = StringVar()
        e1 = Entry(card, textvariable=v1, width=32, font=("Arial", 12), relief=SOLID, bd=1)
        e1.grid(row=1, column=0, columnspan=2, sticky="EW", pady=(0, 16))

        Label(card, text="Password", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=2, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v2 = StringVar()
        e2 = Entry(card, textvariable=v2, show="*", width=32, font=("Arial", 12), relief=SOLID, bd=1)
        e2.grid(row=3, column=0, columnspan=2, sticky="EW", pady=(0, 16))

        Label(card, text="User Type", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=4, column=0, columnspan=2, sticky="W", pady=(0, 4))
        clicked = StringVar(value="")
        o = OptionMenu(card, clicked, "Admin", "Employee")
        o.config(font=("Arial", 12), bg="white", relief=SOLID, width=30)
        o.grid(row=5, column=0, columnspan=2, sticky="W", pady=(0, 20))

        l5 = Label(card, text="", fg=DANGER, font=("Arial", 11), bg=CARD)
        l5.grid(row=7, column=0, columnspan=2, pady=(8, 0))

        bf = Frame(card, bg=CARD)
        bf.grid(row=6, column=0, columnspan=2, sticky="W")
        self._btn(bf, "Add User", lambda: self.add_user(e1, e2, clicked, l5)
                  ).pack(side=LEFT, padx=(0, 8))
        self._btn(bf, "Back", lambda: [self.f2.destroy(), self.adminscreen()],
                  bg=LOGOUT, fg=TEXT).pack(side=LEFT)

    def add_user(self, e1, e2, clicked, l5):
        name = e1.get()
        password = e2.get()
        cu = self.db.cursor()
        t = clicked.get().strip()
        if not name:
            l5.config(text="Username required", fg=DANGER)
        elif not t:
            l5.config(text="User type not selected", fg=DANGER)
        else:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cu.execute(
                "INSERT INTO Users (Name, UserType, password) VALUES (%s, %s, %s)",
                (name, t, hashed)
            )
            self.db.commit()
            l5.config(text="User added successfully", fg=SUCCESS)
        e1.delete(0, END)
        e2.delete(0, END)
        clicked.set("")

    # ── Remove Employee ──────────────────────────────────────

    def remove_employeescreen(self):
        self.f2 = self._screen()
        self._section_title(self.f2, "Remove Employee")

        card = self._card(self.f2)
        card.grid(row=1, column=0, sticky="EW")
        card.grid_columnconfigure(0, weight=1)

        Label(card, text="Employee Name", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v = StringVar()
        e1 = Entry(card, textvariable=v, width=32, font=("Arial", 12), relief=SOLID, bd=1)
        e1.grid(row=1, column=0, columnspan=2, sticky="EW", pady=(0, 20))

        l4 = Label(card, text="", fg=DANGER, font=("Arial", 11), bg=CARD)
        l4.grid(row=3, column=0, columnspan=2, pady=(8, 0))

        bf = Frame(card, bg=CARD)
        bf.grid(row=2, column=0, columnspan=2, sticky="W")
        self._btn(bf, "Remove Employee", lambda: self.remove_employee(e1, l4),
                  bg=DANGER).pack(side=LEFT, padx=(0, 8))
        self._btn(bf, "Back", lambda: [self.f2.destroy(), self.adminscreen()],
                  bg=LOGOUT, fg=TEXT).pack(side=LEFT)

    def remove_employee(self, e1, l4):
        name = e1.get()
        cu = self.db.cursor()
        cu.execute("SELECT * FROM Users WHERE Name = %s", (name,))
        result = cu.fetchall()
        if result == []:
            l4.config(text="No user exists", fg=DANGER)
        else:
            r = messagebox.askquestion("Confirm", "Remove this employee?", icon="warning")
            if r == "yes":
                cu.execute("DELETE FROM Users WHERE Name = %s", (name,))
                self.db.commit()
                l4.config(text="User removed", fg=SUCCESS)
        e1.delete(0, END)

    # ── Customer Order ───────────────────────────────────────

    def customerorder(self):
        self.f2 = self._screen()
        self._section_title(self.f2, "Customer Order")

        card = self._card(self.f2)
        card.grid(row=1, column=0, sticky="EW")
        card.grid_columnconfigure(0, weight=1)

        Label(card, text="Customer Name", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v6 = StringVar()
        self.e3 = Entry(card, textvariable=v6, width=32, font=("Arial", 12), relief=SOLID, bd=1)
        self.e3.grid(row=1, column=0, columnspan=2, sticky="EW", pady=(0, 16))

        Label(card, text="Number of Products", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=2, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v4 = StringVar()
        self.e4 = Spinbox(card, from_=1, to=100, textvariable=v4, width=32,
                          font=("Arial", 12), relief=SOLID, bd=1)
        self.e4.grid(row=3, column=0, columnspan=2, sticky="EW", pady=(0, 16))

        Label(card, text="Sale Date", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=4, column=0, columnspan=2, sticky="W", pady=(0, 4))
        v5 = StringVar()
        cal = DateEntry(card, selectmode='day', textvariable=v5, font=("Arial", 11))
        cal.grid(row=5, column=0, columnspan=2, sticky="W", pady=(0, 20))

        self.l9 = Label(card, text="", fg=DANGER, font=("Arial", 11), bg=CARD)
        self.l9.grid(row=7, column=0, columnspan=2, pady=(8, 0))

        bf = Frame(card, bg=CARD)
        bf.grid(row=6, column=0, columnspan=2, sticky="W")
        self._btn(bf, "Next", lambda: self.order(v6, v4, cal)).pack(side=LEFT, padx=(0, 8))
        self._btn(bf, "Back", lambda: [self.f2.destroy(), self.employeescreen()],
                  bg=LOGOUT, fg=TEXT).pack(side=LEFT)

    def order(self, v6, v4, cal):
        cal = cal.get_date()
        n = int(v4.get())
        self.f2.destroy()
        self.f2 = self._screen()
        self._section_title(self.f2, "Order Items")

        card = self._card(self.f2)
        card.grid(row=1, column=0, sticky="EW")

        Label(card, text="Product ID", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=0, padx=(0, 30), pady=(0, 6), sticky="W")
        Label(card, text="Quantity", font=("Arial", 11, "bold"), bg=CARD, fg=TEXT
              ).grid(row=0, column=1, pady=(0, 6), sticky="W")

        v1 = [StringVar() for _ in range(n)]
        v3 = [StringVar() for _ in range(n)]
        valid1 = (self.window.register(self.validate2), "%P")
        for i in range(n):
            Entry(card, validate='focusout', textvariable=v1[i], width=20,
                  font=("Arial", 12), relief=SOLID, bd=1,
                  validatecommand=valid1
                  ).grid(row=i + 1, column=0, padx=(0, 30), pady=4, sticky="EW")
            Spinbox(card, from_=0, to=10000000, textvariable=v3[i], width=20,
                    font=("Arial", 12), relief=SOLID, bd=1
                    ).grid(row=i + 1, column=1, pady=4, sticky="EW")

        self.l10 = Label(self.f2, text="", fg=DANGER, font=("Arial", 11), bg=BG)
        self.l10.grid(row=3, column=0, columnspan=2, pady=(8, 0))

        bf = Frame(self.f2, bg=BG)
        bf.grid(row=2, column=0, columnspan=2, sticky="W", pady=(16, 0))
        self._btn(bf, "Place Order", lambda: self.addbill(v1, v3, n, cal, v6)
                  ).pack(side=LEFT, padx=(0, 8))
        self._btn(bf, "Back", lambda: [self.f2.destroy(), self.employeescreen()],
                  bg=LOGOUT, fg=TEXT).pack(side=LEFT)

    def addbill(self, v1, v3, n, cal, v6):
        cu = self.db.cursor()
        cu.execute("SELECT MAX(BillNo) FROM CustomerOrder")
        r_count = cu.fetchone()[0]
        billno = 1 if r_count is None else r_count + 1
        total1 = 0
        for i in range(n):
            quantity = int(v3[i].get())
            productid = int(v1[i].get())
            user_id = v6.get()
            saledate = "{0}".format(cal)
            year, month, day = map(int, saledate.split("-"))
            saledate = datetime.date(year, month, day)

            cu = self.db.cursor()
            cu.execute("SELECT CurrentQuantity FROM Storage WHERE P_Id = %s", (productid,))
            row = cu.fetchone()
            if row is None or row[0] < quantity:
                self.l10.config(text=f"Insufficient stock for product {productid}", fg=DANGER)
                return

            cu.execute("SELECT ProductName FROM Products WHERE P_Id = %s", (productid,))
            pname = cu.fetchone()[0]
            cu.execute("SELECT SalePrice FROM Products WHERE P_Id = %s", (productid,))
            total = cu.fetchone()[0] * quantity
            total1 += total
            cu.execute(
                "INSERT INTO CustomerOrder VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (productid, pname, user_id, billno, quantity, saledate, total)
            )
            cu.execute(
                "UPDATE Storage SET CurrentQuantity = CurrentQuantity - %s WHERE P_Id = %s",
                (quantity, productid)
            )
            self.db.commit()
        self.l10.config(text=f"Order placed!  Total: {total1:,}", fg=SUCCESS)


print("INVENTORY MANAGEMENT SYSTEM")
g = gui()
