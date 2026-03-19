import tkinter as tk

menu_root = tk.Tk()
menu_root.title("Main Menu")
menu_root.geometry("400x300")

tk.Label(menu_root, text="Welcome, Akira!", font=("Arial", 16)).pack(pady=50)

menu_root.mainloop()