import os

os.environ['TCL_LIBRARY'] = r"C:\Users\Gayanuka\AppData\Local\Programs\Python\Python314\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Users\Gayanuka\AppData\Local\Programs\Python\Python314\tcl\tk8.6"

import customtkinter as ctk
from tkinter import messagebox, ttk
import customtkinter as ctk
from tkinter import messagebox, ttk
import pandas as ps
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import pickle 

interface = ctk.CTk()
interface.title("🏦 Expense Tracker")
interface.geometry("500x600")
interface.configure(fg_color="#1e1e1e")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
conn = sqlite3.connect("expenses.db")
cursor = conn.cursor()

########## Load AI model ##################################################################
with open("expense_model.pkl", "rb") as f:
    MODEL = pickle.load(f)

with open("vectorizer.pkl", "rb") as v:
    VECTORIZER = pickle.load(v)
    
############## Set app title ##############################################################
ctk.CTkLabel(interface,text="🏦 Expense Tracker",font=("Open Sans", 28, "bold"),text_color="#00ff99").pack(pady=15)

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
    if df.empty:
        messagebox.showinfo("Total Expense", "No data !")
        return
    text =""
    for cat, amt in summary.items():
        text += f"{cat}: Rs.{amt:.2f}\n"

    messagebox.showinfo("Category Summary", text)

########################## Show bar chart #######################################
def show_bar_chart():
    df = load_data()
    if df.empty:
        messagebox.showinfo("Graph", "No data !")
        return
    summary = df.groupby("category")["amount"].sum()
    plt.style.use("dark_background")
    plt.figure(figsize=(6,4))
    plt.bar(summary.index, summary.values, color="#4CAF50")
    plt.title("Expense by Category", color="white")
    plt.xlabel("Category", color="white")
    plt.ylabel("Amount", color="white")
    plt.xticks(rotation=30, color="white")
    plt.yticks(color="white")
    plt.tight_layout()
    plt.show()
    
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
    for index, row in enumerate(rows, start=1):
        expense_list.insert("", ctk.END, values=(
            index,      # Fix index values 
            row[0],
            row[1],
            f"Rs.{row[2]:.2f}",
            row[3],
            row[4]
        ))
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
    expense_id = item["values"][1]  # DB_ID 
    query = "DELETE FROM expenses WHERE id=?"
    cursor.execute(query, (expense_id,))
    conn.commit()
    read_response()
    messagebox.showinfo("Deleted", "Expense deleted successfully") 
      
############## Create Buttons #########################################################
ctk.CTkButton(interface, text = "Add Expense", command = submit_response, width=220, height=35).pack(pady=10)

ctk.CTkButton(interface, text="Total Expense", command=show_total, width=220, height=35).pack(pady=5)

ctk.CTkButton(interface, text="Category Summary", command=category_summary, width=220, height=35).pack(pady=5)

ctk.CTkButton(interface, text="Delete Expense", command=delete_expense, width=220, height=35).pack(pady=5)

ctk.CTkButton(interface, text="Bar Chart", command=show_bar_chart, width=220, height=35).pack(pady=5)

################# AI Predict #################################################################
def Ai_predict(text):
    if not text.strip():
        return ""
    vector = VECTORIZER.transform([text])
    category = MODEL.predict(vector)[0]
    return category

################# Auto Suggest ###############################################################
def auto_fill_category(event=None):
    text = title_entry.get()
    if text:
        category_entry.delete(0, ctk.END)
        category_entry.insert(0, Ai_predict(text))
title_entry.bind("<KeyRelease>", auto_fill_category)

################# Create Output Box #########################################################
table_frame = ctk.CTkFrame(interface)
table_frame.pack(pady=10, fill="both", expand=True)

################## Treeview #################################################################
expense_list = ttk.Treeview(
    table_frame,
    columns=("Index", "DB_ID", "Title", "Amount", "Category", "Date"),
    
    show="headings"
    
)

expense_list.heading("Index", text="No")
expense_list.heading("DB_ID", text="DB_ID")  
expense_list.heading("Title", text="Title")
expense_list.heading("Amount", text="Amount")
expense_list.heading("Category", text="Category")
expense_list.heading("Date", text="Date")

expense_list.column("Index", width=50, anchor="w")
expense_list.column("DB_ID", width=0, stretch=False) 
expense_list.column("Title", width=120)
expense_list.column("Amount", width=100, anchor="w")
expense_list.column("Category", width=120)
expense_list.column("Date", width=100, anchor="w")

##############################################################################################
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=expense_list.yview)
expense_list.configure(yscrollcommand=scrollbar.set)

######################## Improve Treeview look ##################################################
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
