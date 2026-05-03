from tkinter import *
from tkinter import ttk, messagebox, filedialog
import customtkinter 
import pandas as pd
import os

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

# Should probably read this from a file later.
INTRODUCTION = """Open a CSV file to load your data and get started.

Your data will be displayed in a table that you can sort by clicking any column header.

A summary of your data will be shown below the table so you can quickly understand the key statistics.
"""

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__() 
        self.title("CSV Explorer")
        # self.iconbitmap() - I'll use the image service for this!
        self.geometry("500x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._prepare_main()
        self._intro_frame()

    def _intro_frame(self):
        
        # Don't allow user to resize splash screen
        self.resizable(False, False)
        
        self.intro_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.intro_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=30)
        self.intro_frame.grid_columnconfigure(0, weight=1)
        self.intro_frame.grid_rowconfigure(0, weight=1)
        self.intro_frame.grid_rowconfigure(1, weight=1)
        
        self.open_button = customtkinter.CTkButton(
            self.intro_frame, text="Open CSV File", 
            hover_color="#333333", text_color="white", height=80, corner_radius=6, 
            font=("", 16, "bold"), command=self.close_splash)
        self.open_button.grid(row=0, column=0, sticky="sew")
        
        self.instructions = customtkinter.CTkLabel(
            self.intro_frame, text=INTRODUCTION, wraplength=450, anchor="w", justify="left", font=("", 14))
        self.instructions.grid(row=1, column=0, sticky="w", padx=5, pady=20)
    
    def _prepare_main(self):
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create the hamburger clickable 
        self.menu_card = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.menu_card.grid(row=0, column=0, sticky="ew")
        
        self.menu_button = customtkinter.CTkButton(
            self.menu_card, text="☰", width=30, height=30, fg_color="transparent",
            hover_color="#333333", text_color="white", font=("", 16, "bold"),
            corner_radius=6, command=self.menu_clicked
        )
        self.menu_button.grid(row=0, column=0, sticky="w")
        
        self.datatree_card = customtkinter.CTkFrame(self.main_frame)
        self.datatree_card.grid(row=1, column=0, sticky="nesw")
        self.datatree_card.grid_rowconfigure(0, weight=1)
        self.datatree_card.grid_columnconfigure(0, weight=1)
        
        self.status_bar = customtkinter.CTkLabel(
            self, text="No CSV file currently loaded.", corner_radius=0, padx=10, anchor="w"
        )
        self.status_bar.grid(row=1, column=0, sticky="ew")
        
        # Create the sidebar
        self.sidebar = customtkinter.CTkFrame(self, width=200)
        self.sidebar.grid_columnconfigure(0, weight=1)
        
        self.sidebar.place(x=-200, y=0, relheight=1)
        self.sidebar.grid_propagate(False)
        self.sidebar_open = False
        
        self.close_sidebar_button = customtkinter.CTkButton(
            self.sidebar, text="✕", width=30, height=30, fg_color="transparent",
            hover_color="#333333", text_color="white", command=self.menu_clicked
            )
        self.close_sidebar_button.grid(row=0, column=0, sticky="e", padx=10, pady=10)
        
        self.open_csv_button = customtkinter.CTkButton(
            self.sidebar, text="Open CSV File", fg_color="transparent",
            hover_color="#333333", text_color="white", anchor="w",
            height=40, corner_radius=6, command=self.open_csv
        )
        self.open_csv_button.grid(row=1, column=0, sticky="ew", padx=(5, 10))
        
        self.data_summary_button = customtkinter.CTkButton(
            self.sidebar, text="Data Summary", fg_color="transparent",
            hover_color="#333333", text_color="white", anchor="w",
            height=40, corner_radius=6, command=self.summarize_data
        )
        self.data_summary_button.grid(row=2, column=0, sticky="ew", padx=(5, 10))
        
        self.restore_button = customtkinter.CTkButton(
            self.sidebar, text="Restore Original State", fg_color="transparent",
            hover_color="#333333", text_color="white",
            anchor="w", height=40, corner_radius=6, command=self.restore_csv
        )
        self.restore_button.grid(row=3, column=0, sticky="ew", padx=(5, 10))
        
        self.status_bar.lift()
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )

        if file_path:
            self.filename = os.path.basename(file_path)
            self.df = pd.read_csv(file_path)
            self.original_df = self.df.copy()
            self.sort_order = {}
            self.summarize_data()
            return True
        
        return False
    
    def open_csv(self):
        confirm = messagebox.askyesno(
            title="Open CSV File",
            message="Opening a new CSV file will replace the current dataset. Your current dataset "
            "will not be changed. Continue?"
        )

        if not confirm:
            return
        
        if self.open_file():
            self.populate_dataframe()
            if self.sidebar_open:
                self.menu_clicked()
        
    def restore_csv(self):
        confirm = messagebox.askyesno(
        title="Restore Original State",
        message="Are you sure you want to restore the data to its original state?"
        )

        if not confirm:
            return

        self.df = self.original_df.copy()
        self.populate_dataframe(status_msg=f"Restored {self.filename} to its original state.")
        
        if self.sidebar_open:
            self.menu_clicked()
    
    def close_splash(self, event=None):
        if not self.open_file():
            return
        
        self.intro_frame.destroy()
        self.main_frame.grid(row=0, column=0, sticky="nesw")
        self.resizable(True, True)
        
        self.create_tree()
    
    def summarize_data(self):
        (rows, cols) = self.df.shape
        self.status_bar.configure(text=f"{self.filename}, Rows: {rows}, Columns: {cols}")
        
        if self.sidebar_open:
            self.menu_clicked()
        
    def menu_clicked(self):
        if self.sidebar_open:
            self._close_menu()
        else:
            self._open_menu()
        
        self.sidebar_open = not self.sidebar_open
        
    def _open_menu(self, x=-200):
        if x >= 0:
            self.sidebar.place(x=0, y=0, relheight=1)
            return

        self.sidebar.place(x=x, y=0, relheight=1)
        self.after(5, lambda: self._open_menu(x + 10))
            
    def _close_menu(self, x=0):
        if x <= -200:
            self.sidebar.place(x=-200, y=0, relheight=1)
            return

        self.sidebar.place(x=x, y=0, relheight=1)
        self.after(5, lambda: self._close_menu(x - 10))
            
    def create_tree(self):
        self.tree = ttk.Treeview(self.datatree_card, show="headings")
        
        y_scroll = customtkinter.CTkScrollbar(self.datatree_card, orientation="vertical", command=self.tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns", pady=(10, 0))

        x_scroll = customtkinter.CTkScrollbar(self.datatree_card, orientation="horizontal", command=self.tree.xview)
        x_scroll.grid(row=1, column=0, sticky="ew", padx=(10, 0))
        
        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )
        
        self.populate_dataframe()

    def populate_dataframe(self, status_msg=None):
        self.tree.delete(*self.tree.get_children())
        
        headings = tuple(self.df.columns)
        self.tree["columns"] = headings
        
        for heading in headings:
            self.tree.heading(heading, text=heading, anchor="w", command=lambda c=heading: self._sort_by_column(c))
            self.tree.column(heading, anchor="w", width=100, stretch=True)
           
            if heading not in self.sort_order:
                self.sort_order[heading] = "ascending"
            
        for row in self.df.values:
            self.tree.insert(parent="", index="end", values=list(row))
        self.tree.grid(row=0, column=0, sticky="nesw", padx=(10,0))
        
        if(status_msg):
            self.status_bar.configure(text=status_msg)
        else:
            self.summarize_data()
    
    def _sort_by_column(self, col):
        self.sort_order[col] = "ascending" if self.sort_order.get(col) == "descending" else "descending"
        ascending = self.sort_order[col] == "ascending"
        
        try:
            self.df = self.df.sort_values(
                by=col,
                key=lambda x: pd.to_numeric(x),
                ascending=ascending
            )
        except ValueError:
            self.df = self.df.sort_values(by=col, ascending=ascending)
        
        self.df = self.df.reset_index(drop=True)
        self.populate_dataframe(status_msg=f"Sorted by {col} in {self.sort_order.get(col)} order.")
    
app = App()
app.mainloop()