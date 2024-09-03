import tkinter as tk  # Import tkinter
import ttkbootstrap as ttk  # Import ttkbootstrap
from ttkbootstrap.constants import *
from tkinter import messagebox
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# File to store the data
DATA_FILE = 'expense_data.json'

# Load data from the file if it exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as file:
        category_dict = json.load(file)
else:
    category_dict = {
        'Food': [],
        'Transportation': [],
        'Subscriptions': [],
        'Household Items': [],
        'Entertainment': []
    }

# Function to save data to the file
def saveData():
    with open(DATA_FILE, 'w') as file:
        json.dump(category_dict, file)

# Function to calculate total expenses for the current month
def calculate_total_expenses():
    total = 0
    current_month = datetime.now().month
    current_year = datetime.now().year
    for entries in category_dict.values():
        for entry in entries:
            # Assuming entries are stored with a date key in the format 'YYYY-MM-DD'
            entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
            if entry_date.month == current_month and entry_date.year == current_year:
                total += entry['price']
    return total

# Function to update the total expenses label in real-time
def update_total_expenses_label():
    total_expenses = calculate_total_expenses()
    total_expenses_label.config(text=f"Total Expenses This Month: ${total_expenses:.2f}")
    root.after(1000, update_total_expenses_label)  # Update every 1 second

# Function to show the main menu
def show_main_menu():
    expense_menu_frame.pack_forget()
    main_menu_frame.pack(fill='both', expand=True)
    update_total_expenses_label()  # Start updating the total expenses label

# Function to show the expense management menu
def show_expense_menu():
    main_menu_frame.pack_forget()
    expense_menu_frame.pack(fill='both', expand=True)

# Function to create the pie chart on the main menu
def create_pie_chart():
    categories = list(category_dict.keys())
    amounts = [sum(entry['price'] for entry in entries) for entries in category_dict.values()]
    total = sum(amounts)  # Calculate total expenses for percentage calculation

    # Check if total is zero to avoid division by zero errors
    if total == 0:
        # Handle the case where there is no data
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, 'No data available to display', horizontalalignment='center', verticalalignment='center', fontsize=16)
        ax.axis('off')  # Hide the axis
    else:
        fig, ax = plt.subplots(figsize=(6, 6))  # Figure size

        # Create the pie chart without percentage labels
        wedges, texts = ax.pie(
            amounts, 
            labels=None,  # Disable default labels
            startangle=90, 
            labeldistance=1.2  # Increase distance for category labels
        )

        # Generate legend labels with percentages
        legend_labels = [f'{category} - {amount / total:.1%}' for category, amount in zip(categories, amounts)]

        # Add a legend with category labels and percentages in the center of the chart
        ax.legend(wedges, legend_labels, title="Categories", loc="center", bbox_to_anchor=(0.5, 0.5), fontsize=10)

        # Shrink the pie chart to make space for labels
        plt.setp(wedges, width=0.3)

        # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.axis('equal') 

    # Apply tight layout to reduce white space
    plt.tight_layout()

    chart = FigureCanvasTkAgg(fig, master=main_menu_frame)
    chart.get_tk_widget().pack(pady=20)

# Function to add a new category
def addCategory():
    newCategory = category_entry.get().strip()
    
    if newCategory:
        if newCategory not in category_dict:
            category_dict[newCategory] = []
            saveData()  # Save the data after adding a new category
            messagebox.showinfo("Success", f"Category '{newCategory}' added.")
            category_listbox.insert(tk.END, newCategory)
        else:
            messagebox.showwarning("Warning", "Category already exists.")
    else:
        messagebox.showwarning("Warning", "Please enter a valid category.")
    
    category_entry.delete(0, tk.END)

# Function to add a new entry to a category
def addEntry():
    newEntry = entry_entry.get().strip()
    price = price_entry.get().strip()
    description = description_entry.get().strip()
    selected_category_index = category_listbox.curselection()
    
    if newEntry and price and selected_category_index:
        selected_category = category_listbox.get(selected_category_index)
        entry_data = {
            'item': newEntry,
            'price': float(price),
            'description': description,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        category_dict[selected_category].append(entry_data)
        saveData()  # Save the data after adding a new entry
        messagebox.showinfo("Success", f"Entry '{newEntry}' added to category '{selected_category}'.")
    else:
        messagebox.showwarning("Warning", "Please enter a valid item, price, and select a category.")
    
    entry_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)

# Function to display entries when a category is clicked
def display_entries(event):
    selected_category_index = category_listbox.curselection()
    
    if selected_category_index:
        selected_category = category_listbox.get(selected_category_index)
        entries = category_dict[selected_category]
        
        if entries:
            entries_text.delete(1.0, tk.END)
            
            for entry in entries:
                entry_display = f"Item: {entry['item']}\nPrice: ${entry['price']}\nDescription: {entry['description']}\n\n"
                entries_text.insert(tk.END, entry_display)
        else:
            entries_text.delete(1.0, tk.END)
            entries_text.insert(tk.END, f"No entries found for category '{selected_category}'.")
    else:
        messagebox.showwarning("Warning", "Please select a category.")

# Create the main window with ttkbootstrap
root = ttk.Window(themename="solar")  # You can replace "solar" with any other available theme
root.title("Expense Management App")
root.geometry("800x600")  # Increase the width to fit the new layout

# Create the main menu frame
main_menu_frame = ttk.Frame(root)

# Display total expenses for the current month
total_expenses_label = ttk.Label(main_menu_frame, text="", font=("Arial", 16))
total_expenses_label.pack(pady=20)

create_pie_chart()

# Button to navigate to the expense management menu
go_to_expense_menu_button = ttk.Button(main_menu_frame, text="Manage Expenses", bootstyle=PRIMARY, command=show_expense_menu)
go_to_expense_menu_button.pack(pady=20)

# Create the expense management menu frame
expense_menu_frame = ttk.Frame(root)

# Create a frame to hold the category list and entries side by side
list_frame = ttk.Frame(expense_menu_frame)
list_frame.pack(fill=tk.BOTH, expand=True)

# Category input and button
category_label = ttk.Label(expense_menu_frame, text="Enter New Category:")
category_label.pack(pady=5)
category_entry = ttk.Entry(expense_menu_frame, width=30)
category_entry.pack(pady=5)
add_category_button = ttk.Button(expense_menu_frame, text="Add Category", bootstyle=SUCCESS, command=addCategory)
add_category_button.pack(pady=5)

# Entry input and button
entry_label = ttk.Label(expense_menu_frame, text="What did you buy today?")
entry_label.pack(pady=5)
entry_entry = ttk.Entry(expense_menu_frame, width=30)
entry_entry.pack(pady=5)

# Price input
price_label = ttk.Label(expense_menu_frame, text="Enter Price:")
price_label.pack(pady=5)
price_entry = ttk.Entry(expense_menu_frame, width=30)
price_entry.pack(pady=5)

# Description input
description_label = ttk.Label(expense_menu_frame, text="Enter Description (optional):")
description_label.pack(pady=5)
description_entry = ttk.Entry(expense_menu_frame, width=30)
description_entry.pack(pady=5)

# Button to add entry
add_entry_button = ttk.Button(expense_menu_frame, text="Add Entry", bootstyle=SUCCESS, command=addEntry)
add_entry_button.pack(pady=5)

# Listbox to display categories with increased text size and border
category_listbox = tk.Listbox(list_frame, height=15, selectmode=tk.SINGLE, exportselection=False, font=("Arial", 14), bd=2, relief="solid")
category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Text widget to display the entries of the selected category
entries_text = tk.Text(list_frame, height=15, wrap=tk.WORD, font=("Arial", 12), bd=2, relief="solid")
entries_text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Bind the display_entries function to the Listbox selection event
category_listbox.bind('<<ListboxSelect>>', display_entries)

# Populate the Listbox with existing categories
for category in category_dict.keys():
    category_listbox.insert(tk.END, category)

# Button to navigate back to the main menu
back_to_main_menu_button = ttk.Button(expense_menu_frame, text="Main Menu", bootstyle=INFO, command=show_main_menu)
back_to_main_menu_button.pack(pady=10)

# Start by displaying the main menu
main_menu_frame.pack(fill='both', expand=True)
update_total_expenses_label()  # Start updating the total expenses label immediately

# Run the main loop
root.mainloop()
