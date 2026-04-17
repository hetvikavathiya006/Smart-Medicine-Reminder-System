import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import time
import threading

# ---------------- Database Setup ----------------
conn = sqlite3.connect("medicines.db", check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS medicine_schedule(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        morning_dose TEXT,
        morning_time TEXT,
        night_dose TEXT,
        night_time TEXT
    )
''')
conn.commit()

# ---------------- Functions ----------------
def add_medicine():
    name = entry_name.get()
    m_dose = entry_m_dose.get()
    m_time = entry_m_time.get()
    n_dose = entry_n_dose.get()
    n_time = entry_n_time.get()

    if name == "":
        messagebox.showerror("Error", "Medicine Name is required!")
        return
        
    def is_empty(val): return val.strip() == "" or val.strip() == "-"

    if is_empty(m_dose) and is_empty(m_time) and is_empty(n_dose) and is_empty(n_time):
        messagebox.showerror("Error", "At least one dose/time (Morning or Night) is required!")
        return

    # Validate times if provided
    if not is_empty(m_time):
        try:
            time.strptime(m_time.strip(), '%H:%M')
        except ValueError:
            messagebox.showerror("Error", "Morning Time must be in HH:MM format (24-hour) or '-'!")
            return

    if not is_empty(n_time):
        try:
            time.strptime(n_time.strip(), '%H:%M')
        except ValueError:
            messagebox.showerror("Error", "Night Time must be in HH:MM format (24-hour) or '-'!")
            return

    c.execute("INSERT INTO medicine_schedule (name, morning_dose, morning_time, night_dose, night_time) VALUES (?, ?, ?, ?, ?)", 
              (name, m_dose, m_time, n_dose, n_time))
    conn.commit()
    messagebox.showinfo("Success", f"Medicine {name} added!")
    
    entry_name.delete(0, tk.END)
    entry_m_dose.delete(0, tk.END)
    entry_m_time.delete(0, tk.END)
    entry_n_dose.delete(0, tk.END)
    entry_n_time.delete(0, tk.END)
    
    load_medicines()

def delete_medicine():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Please select a medicine to delete")
        return
        
    item_details = tree.item(selected_item)
    med_name = item_details['values'][0]
    
    # Delete from DB
    c.execute("DELETE FROM medicine_schedule WHERE name=?", (med_name,))
    conn.commit()
    messagebox.showinfo("Success", f"Medicine {med_name} removed!")
    load_medicines()

def load_medicines():
    c.execute("SELECT * FROM medicine_schedule")
    records = c.fetchall()
    for item in tree.get_children():
        tree.delete(item)
    for record in records:
        # id=0, name=1, m_dose=2, m_time=3, n_dose=4, n_time=5
        tree.insert("", tk.END, values=(record[1], record[2], record[3], record[4], record[5]))

def check_reminder():
    while True:
        try:
            current_time = time.strftime("%H:%M")
            
            # Check morning times
            c.execute("SELECT name, morning_dose FROM medicine_schedule WHERE morning_time=?", (current_time,))
            for reminder in c.fetchall():
                messagebox.showinfo("🌅 Morning Reminder!", f"Time to take your morning medicine:\n\n{reminder[0]}\nDose: {reminder[1]}")
                
            # Check night times
            c.execute("SELECT name, night_dose FROM medicine_schedule WHERE night_time=?", (current_time,))
            for reminder in c.fetchall():
                messagebox.showinfo("🌙 Night Reminder!", f"Time to take your night medicine:\n\n{reminder[0]}\nDose: {reminder[1]}")
                
        except Exception as e:
            print("Error in reminder thread:", e)
        time.sleep(60)  # check every minute

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Smart Medicine Reminder - Day/Night Schedule")
root.geometry("680x750")
root.configure(bg="#F4F6F9")

# Styling using ttk
style = ttk.Style()
if 'vista' in style.theme_names():
    style.theme_use('vista')
else:
    style.theme_use('clam')
    
style.configure("Treeview", font=("Helvetica", 10), rowheight=30)
style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"))
style.configure("TButton", font=("Helvetica", 11, "bold"), padding=5)

# Modern Header
header_frame = tk.Frame(root, bg="#0052cc", pady=15)
header_frame.pack(fill=tk.X)
header_label = tk.Label(header_frame, text="⚕️ Smart Medicine Reminder", font=("Helvetica", 22, "bold"), bg="#0052cc", fg="white")
header_label.pack()

# Input section
input_frame = tk.Frame(root, bg="white", padx=20, pady=20, relief=tk.FLAT)
input_frame.pack(pady=15, padx=30, fill=tk.X)

tk.Label(input_frame, text="Medicine Name:", font=("Helvetica", 11, "bold"), bg="white", fg="#333").grid(row=0, column=0, sticky="w", pady=5)
entry_name = ttk.Entry(input_frame, width=25, font=("Helvetica", 11))
entry_name.grid(row=0, column=1, pady=5, padx=10, sticky="w", columnspan=3)

# Morning Inputs
tk.Label(input_frame, text="🌅 Morning Dose:", font=("Helvetica", 11, "bold"), bg="white", fg="#e67e22").grid(row=1, column=0, sticky="w", pady=(15, 5))
entry_m_dose = ttk.Entry(input_frame, width=15, font=("Helvetica", 11))
entry_m_dose.grid(row=1, column=1, pady=(15, 5), padx=10, sticky="w")

tk.Label(input_frame, text="Morning Time (HH:MM):", font=("Helvetica", 11, "bold"), bg="white", fg="#e67e22").grid(row=1, column=2, sticky="w", pady=(15, 5))
entry_m_time = ttk.Entry(input_frame, width=15, font=("Helvetica", 11))
entry_m_time.grid(row=1, column=3, pady=(15, 5), padx=10, sticky="w")

# Night Inputs
tk.Label(input_frame, text="🌙 Night Dose:", font=("Helvetica", 11, "bold"), bg="white", fg="#2c3e50").grid(row=2, column=0, sticky="w", pady=5)
entry_n_dose = ttk.Entry(input_frame, width=15, font=("Helvetica", 11))
entry_n_dose.grid(row=2, column=1, pady=5, padx=10, sticky="w")

tk.Label(input_frame, text="Night Time (HH:MM):", font=("Helvetica", 11, "bold"), bg="white", fg="#2c3e50").grid(row=2, column=2, sticky="w", pady=5)
entry_n_time = ttk.Entry(input_frame, width=15, font=("Helvetica", 11))
entry_n_time.grid(row=2, column=3, pady=5, padx=10, sticky="w")

# Button frame
btn_frame = tk.Frame(root, bg="#F4F6F9")
btn_frame.pack(pady=5)

btn_add = tk.Button(btn_frame, text="➕ Add Medicine Schedule", command=add_medicine, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"), relief=tk.FLAT, padx=15, pady=5)
btn_add.grid(row=0, column=0, padx=10)

btn_delete = tk.Button(btn_frame, text="🗑️ Delete Selected", command=delete_medicine, bg="#f44336", fg="white", font=("Helvetica", 12, "bold"), relief=tk.FLAT, padx=15, pady=5)
btn_delete.grid(row=0, column=1, padx=10)

# Medicine List with Treeview
list_frame = tk.Frame(root, bg="white", padx=10, pady=10)
list_frame.pack(pady=15, padx=30, fill=tk.BOTH, expand=True)

tk.Label(list_frame, text="Your Schedule Overview", font=("Helvetica", 14, "bold"), bg="white", fg="#0052cc").pack(anchor="w", pady=(0,10))

tree_scroll = ttk.Scrollbar(list_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree_scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

tree = ttk.Treeview(list_frame, columns=("Name", "MDose", "MTime", "NDose", "NTime"), show="headings", yscrollcommand=tree_scroll.set, xscrollcommand=tree_scroll_x.set)
tree.pack(fill=tk.BOTH, expand=True)

tree_scroll.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

tree.heading("Name", text="Medicine Name")
tree.heading("MDose", text="Morning Dose")
tree.heading("MTime", text="Morning Time")
tree.heading("NDose", text="Night Dose")
tree.heading("NTime", text="Night Time")

tree.column("Name", width=160, anchor=tk.W)
tree.column("MDose", width=100, anchor=tk.CENTER)
tree.column("MTime", width=100, anchor=tk.CENTER)
tree.column("NDose", width=100, anchor=tk.CENTER)
tree.column("NTime", width=100, anchor=tk.CENTER)

load_medicines()

# Start Reminder Thread
reminder_thread = threading.Thread(target=check_reminder, daemon=True)
reminder_thread.start()

root.mainloop()
