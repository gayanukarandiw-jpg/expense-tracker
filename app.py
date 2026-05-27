import customtkinter as ctk
from tkinter import messagebox, ttk
import pandas as ps
import sqlite3
from datetime import datetime

interface = ctk.CTk()
interface.title("Expense Tracker")
interface.geometry("500x700")
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("green")
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

############## Set app title ##############################################################
ctk.CTkLabel(interface, text = "Simple Expense Tracker").pack(pady=5)

############### Add data to pandas #######################################################
def load_data():
    conn = sqlite3.connect("expenses.db")
    df = ps.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return df

################### Dispplay Total #######################################################
def show_total():
    df = load_data()
    total = df["amount"].sum()
    messagebox.showinfo("Total Expense", f"Total: Rs. {total:.2f}")

################### Display Total according to category ###################################
def category_summary():
    df = load_data()
    summary = df.groupby("category")["amount"].sum()
    text =""
    for cat, amt in summary.items():
        text += f"{cat}: Rs.{amt:.2f}\n"

    messagebox.showinfo("Category Summary", text)
    
############# Configure Inputs ############################################################
ctk.CTkLabel(interface, text="Description").pack(pady=2)
title_entry = ctk.CTkEntry(interface)
title_entry.pack(pady=3)

ctk.CTkLabel(interface, text = "Amount (In Rs.)").pack(pady=2)
amount_entry = ctk.CTkEntry(interface)
amount_entry.pack(pady=3)

ctk.CTkLabel(interface, text ="Category").pack(pady=2)
category_entry = ctk.CTkEntry(interface)
category_entry.pack(pady=3)

################## Read submited data ########################################################
def read_response():
    for item in expense_list.get_children():
        expense_list.delete(item)
    query = """SELECT id, title, amount, category, date FROM expenses"""
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        expense_list.insert("", ctk.END, values=row)
        
############# Save User response to the database #############################################################
def submit_response():
    title = title_entry.get().strip()
    amount = amount_entry.get().strip()
    category = category_entry.get().strip()
    date = datetime.now().strftime("%Y-%m-%d")
    if not title or not amount or not category:
        messagebox.showwarning("Input Error", "All fields are required!")
        return
    try:
        amount = float(amount)
    except ValueError:
        messagebox.showwarning("Error", "Amount must be a number")
        return
    query = """
            INSERT INTO expenses (title, amount, category, date)
            VALUES (?, ?, ?, ?)
            """
    cursor.execute(query, (title, amount, category, date))
    conn.commit()
    read_response()
    print("Successfully added !")

    title_entry.delete(0, ctk.END)
    amount_entry.delete(0, ctk.END)
    category_entry.delete(0, ctk.END)

##################### Delete recorded response ############################################
def delete_expense():
    selected = expense_list.selection()
    if not selected:
        messagebox.showwarning("Error", "Please select an expense")
        return

    item = expense_list.item(selected[0])
    expense_id = item["values"][0] 
    query = "DELETE FROM expenses WHERE id=?"
    cursor.execute(query, (expense_id,))
    conn.commit()
    read_response()
    messagebox.showinfo("Deleted", "Expense deleted successfully") 
      
############## Create Submit Button #########################################################
ctk.CTkButton(interface, text = "Add Expense", command = submit_response, width=220, height=35).pack(pady=10)

ctk.CTkButton(interface, text="Total Expense", command=show_total, width=220, height=35).pack(pady=5)

ctk.CTkButton(interface, text="Category Summary", command=category_summary, width=220, height=35).pack(pady=5)

ctk.CTkButton(interface, text="Delete Expense", command=delete_expense, width=220, height=35).pack(pady=5)

################# Create Output Box #########################################################
table_frame = ctk.CTkFrame(interface)
table_frame.pack(pady=10, fill="both", expand=True)

# ===== Treeview =====
expense_list = ttk.Treeview(
    table_frame,
    columns=("ID", "Title", "Amount", "Category", "Date"),
    show="headings"
)

expense_list.heading("ID", text="ID")
expense_list.heading("Title", text="Title")
expense_list.heading("Amount", text="Amount")
expense_list.heading("Category", text="Category")
expense_list.heading("Date", text="Date")

expense_list.column("ID", width=50, anchor="center")
expense_list.column("Title", width=120)
expense_list.column("Amount", width=100, anchor="center")
expense_list.column("Category", width=120)
expense_list.column("Date", width=100, anchor="center")
##############################################################################################
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=expense_list.yview)
expense_list.configure(yscrollcommand=scrollbar.set)
######################## Improve table look ##################################################
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#3a3535",
    foreground="white",
    fieldbackground="#3a3535",
    rowheight=28
)

style.configure(
    "Treeview.Heading",
    background="#312f2f",
    foreground="white"
)
scrollbar.pack(side="right", fill="y")
expense_list.pack(side="left", fill="both", expand=True)

read_response()
interface.mainloop()
conn.close()
