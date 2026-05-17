import tkinter as tk
from tkinter import messagebox
import json
from abc import ABC, abstractmethod


class LibraryItem:
    def __init__(self, title, unique_id):
        self._title = title
        self._item_id = unique_id

    def get_info(self):
        return f"ID: {self._item_id}, Title: {self._title}"

    def get_id(self):
        return self._item_id

class Book(LibraryItem):
    def __init__(self, title, unique_id, author):
        super().__init__(title, unique_id)
        self.author = author 

    def get_info(self):
        return f"Book: {self._title} by {self.author} ({self._item_id})"

class Magazine(LibraryItem):
    def __init__(self, title, unique_id, issue_number):
        super().__init__(title, unique_id)
        self.issue_number = issue_number 

    def get_info(self):
        return f"Magazine: {self._title} (Issue #{self.issue_number}) ({self._item_id})"

class CatalogEntry:
    def __init__(self, item_id, added_date):
        self._item_id = item_id
        self.added_date = added_date
        self.is_available = True

class IDGenerator:
    def __init__(self):
        self._current_id = 1000

    def get_next_id(self):
        self._current_id += 1
        return f"ITEM-{self._current_id}"

class AbstractLogger(ABC):
    @abstractmethod
    def log_event(self, message):
        pass

class SimpleConsoleLogger(AbstractLogger):
    def log_event(self, message):
        print(f"[LOG]: {message}")

class DataManager:
    def __init__(self, filename="library_data.json"):
        self.filename = filename

    def save_data(self, items):
        data_to_save = [i.__dict__ for i in items]

    def load_data(self):
        """Loads data from the file and reconstructs objects"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            reconstructed_items = []
            for item_data in data:
                #reconstruct objects
                if 'author' in item_data:
                    item = Book(item_data['_title'], item_data['_item_id'], item_data['author'])
                elif 'issue_number' in item_data:
                    item = Magazine(item_data['_title'], item_data['_item_id'], item_data['issue_number'])
                else:
                    item = LibraryItem(item_data['_title'], item_data['_item_id'])
                reconstructed_items.append(item)
            return reconstructed_items
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

class LogicController:
    def __init__(self):
        self.data_manager = DataManager()
        self.id_gen = IDGenerator()
        self.logger = SimpleConsoleLogger()
        self.items = self.data_manager.load_data()

    def add_new_item(self, item_type, title, detail):
        new_id = self.id_gen.get_next_id()
        item = None
        
        if item_type == "Book":
            item = Book(title, new_id, detail)
            
        elif item_type == "Magazine":
            try:
                item = Magazine(title, new_id, int(detail))
            except ValueError:
                return False

        if item:
            self.items.append(item)
            self.data_manager.save_data(self.items)
            self.logger.log_event(f"Added new item: {item.get_info()}")
            return True
        return False
    
    def get_all_items(self):
        return self.items

#UI

class ButtonFactory:
    """Utility class for generating consistent UI elements"""
    @staticmethod
    def create_nav_button(master, text, command):
        """A standardized button style."""
        return tk.Button(master, text=text, command=command,
                         bg="#4CAF50", fg="white", font=('Arial', 10, 'bold'), 
                         relief=tk.RAISED, bd=3)

class BaseFrame(tk.Frame):
    """Base class for all specific UI views."""
    def __init__(self, master, controller):
        super().__init__(master, padx=20, pady=20)
        self.controller = controller
        self.master = master
        
    def clear_view(self):
        """Common method to destroy all widgets before drawing a new view."""
        for widget in self.winfo_children():
            widget.destroy()

    def draw_widgets(self):
        """Abstract method for UI components"""
        self.clear_view()
        tk.Label(self, text="Base View", font=('Arial', 16, 'bold')).pack()

class AddItemFrame(BaseFrame):
    """
    UI for adding new items (Book/Magazine).
    """
    def draw_widgets(self):
        self.clear_view()
        tk.Label(self, text="➕ Add New Item to Catalog", font=('Arial', 16, 'bold')).pack(pady=10)

        # Dropdown for item type
        tk.Label(self, text="Item Type:").pack(pady=5)
        self.item_type = tk.StringVar(self, "Book")
        tk.OptionMenu(self, self.item_type, "Book", "Magazine").pack(pady=5)

        # Title Entry
        tk.Label(self, text="Title:").pack(pady=5)
        self.title_entry = tk.Entry(self, width=40)
        self.title_entry.pack(pady=5)

        # Detail Entry Author and Issue
        tk.Label(self, text="Author / Issue Number:").pack(pady=5)
        self.detail_entry = tk.Entry(self, width=40)
        self.detail_entry.pack(pady=5)

        # Submit Button
        submit_btn = ButtonFactory.create_nav_button(self, "Submit Item", self._submit_item)
        submit_btn.pack(pady=15)

    def _submit_item(self):
        item_type = self.item_type.get()
        title = self.title_entry.get().strip()
        detail = self.detail_entry.get().strip()
        
        if not title or not detail:
            messagebox.showerror("Error", "Title and Detail cannot be empty.")
            return

        success = self.controller.add_new_item(item_type, title, detail)
        
        if success:
            messagebox.showinfo("Success", f"{item_type} '{title}' added successfully!")
            self.title_entry.delete(0, tk.END)
            self.detail_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Failed to add {item_type}. Check format (e.g., Issue Number must be an integer).")

class ViewItemFrame(BaseFrame):
    """
    UI for viewing all items in the library.
    """
    def draw_widgets(self):
        self.clear_view()
        tk.Label(self, text="📚 Catalog View", font=('Arial', 16, 'bold')).pack(pady=10)

        items = self.controller.get_all_items()
        
        if not items:
            tk.Label(self, text="The catalog is empty.", fg="red").pack(pady=20)
            return

        # Use a Listbox to display items cleanly
        listbox_frame = tk.Frame(self)
        listbox_frame.pack(fill='both', expand=True, pady=10)

        listbox = tk.Listbox(listbox_frame, height=15, width=60, font=('Courier', 10))
        listbox.pack(side="left", fill="y")
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        
        for item in items:
            listbox.insert(tk.END, item.get_info())


class App(tk.Tk):
    """
    The main Tkinter application window.
    """
    def __init__(self, controller):
        super().__init__()
        self.title("Simple OOP Library Tracker")
        self.controller = controller
        self._current_view = None

        self._setup_navigation()
        self.show_view(ViewItemFrame) 

    def _setup_navigation(self):
        """Sets up the navigation bar at the top."""
        nav_frame = tk.Frame(self, bg="#333", padx=5, pady=5)
        nav_frame.pack(side="top", fill="x")

        ButtonFactory.create_nav_button(nav_frame, "View Catalog", 
                                        lambda: self.show_view(ViewItemFrame)).pack(side="left", padx=10)
        
        ButtonFactory.create_nav_button(nav_frame, "Add New Item", 
                                        lambda: self.show_view(AddItemFrame)).pack(side="left", padx=10)

    def show_view(self, ViewClass):
        """Switches the current main view."""
        if self._current_view:
            self._current_view.pack_forget() 

        self._current_view = ViewClass(self, self.controller)
        self._current_view.draw_widgets()
        self._current_view.pack(fill="both", expand=True)

# EXECUTION

if __name__ == "__main__":
    # To run backend
    controller = LogicController()
    
    # To run UI
    app = App(controller)
    app.mainloop()