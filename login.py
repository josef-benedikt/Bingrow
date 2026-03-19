import tkinter as tk
from tkinter import messagebox
import os

def login():
    username = entry_user.get()
    password = entry_pass.get()

    # 1. Check for empty fields
    if not username or not password:
        messagebox.showwarning("Input Error", "Fields cannot be empty!")
        return

    # 2. Validate credentials
    if username == "Akira" and password == "BGYO":
        messagebox.showinfo("Success", "Login Successful!")
        root.destroy()  # Close the login window
        os.system('python menu.py')  # Open the menu file
    else:
        messagebox.showerror("Error", "Incorrect Username or Password")


root = tk.Tk()
root.title("Login Window")
root.geometry("300x200")


tk.Label(root, text="Username:").pack(pady=5)
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password:").pack(pady=5)
entry_pass = tk.Entry(root, show="*")  # Masks password with asterisks
entry_pass.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()