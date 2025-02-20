import os
import re
import shutil
import logging
from tkinter import filedialog, messagebox
from ttkbootstrap import Window, Label, Button, Checkbutton, IntVar, Progressbar, Style

# Configure logging
logging.basicConfig(filename='temp_cleaner.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class TempCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Temporary File Cleaner")
        self.root.geometry("500x400")
        self.style = Style(theme="cosmo")  # Choose a theme: cosmo, flatly, etc.

        # Variables for checkboxes
        self.cache_var = IntVar()
        self.downloads_var = IntVar()
        self.logs_var = IntVar()

        # GUI Elements
        Label(root, text="Temporary File Cleaner", font=("Arial", 18, "bold")).pack(pady=10)

        Label(root, text="Select the types of files to delete:", font=("Arial", 12)).pack(pady=5)

        Checkbutton(root, text="Cache Files", variable=self.cache_var, style="info.TCheckbutton").pack(anchor='w', padx=50, pady=5)
        Checkbutton(root, text="Downloaded Files", variable=self.downloads_var, style="info.TCheckbutton").pack(anchor='w', padx=50, pady=5)
        Checkbutton(root, text="Old Log Files", variable=self.logs_var, style="info.TCheckbutton").pack(anchor='w', padx=50, pady=5)

        Button(root, text="Select Folder", command=self.select_folder, style="primary.TButton").pack(pady=20)
        Button(root, text="Clean Files", command=self.clean_files, style="success.TButton").pack(pady=10)

        # Progress Bar
        self.progress = Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)

        # Status Label
        self.status_label = Label(root, text="", font=("Arial", 10))
        self.status_label.pack(pady=10)

    def select_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Folder to Clean")
        if self.folder_path:
            self.status_label.config(text=f"Selected Folder: {self.folder_path}", foreground="green")

    def clean_files(self):
        if not hasattr(self, 'folder_path'):
            messagebox.showwarning("No Folder Selected", "Please select a folder first.")
            return

        # Define patterns for temporary files
        patterns = {
            'cache': r'.*\.cache$|.*\.tmp$',
            'downloads': r'.*\.download$|.*\.part$',
            'logs': r'.*\.log$|.*\.old$|.*\.bak$'
        }

        # Determine which patterns to use based on user selection
        selected_patterns = []
        if self.cache_var.get():
            selected_patterns.append(patterns['cache'])
        if self.downloads_var.get():
            selected_patterns.append(patterns['downloads'])
        if self.logs_var.get():
            selected_patterns.append(patterns['logs'])

        if not selected_patterns:
            messagebox.showwarning("No Selection", "Please select at least one type of file to delete.")
            return

        # Combine patterns into a single regex
        combined_pattern = '|'.join(selected_patterns)
        regex = re.compile(combined_pattern, re.IGNORECASE)

        # Walk through the directory and delete matching files
        deleted_files = []
        total_files = 0
        for root_dir, _, files in os.walk(self.folder_path):
            total_files += len(files)

        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        for root_dir, _, files in os.walk(self.folder_path):
            for file in files:
                if regex.match(file):
                    file_path = os.path.join(root_dir, file)
                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logging.info(f"Deleted: {file_path}")
                    except Exception as e:
                        logging.error(f"Failed to delete {file_path}: {e}")
                self.progress["value"] += 1
                self.root.update_idletasks()  # Update the GUI

        # Show results
        if deleted_files:
            self.status_label.config(text=f"{len(deleted_files)} files were deleted.", foreground="blue")
            messagebox.showinfo("Cleanup Complete", f"{len(deleted_files)} files were deleted.\nSee log for details.")
        else:
            self.status_label.config(text="No files were deleted.", foreground="red")
            messagebox.showinfo("Cleanup Complete", "No files were deleted.")

        # Reset progress bar
        self.progress["value"] = 0

if __name__ == "__main__":
    root = Window()
    app = TempCleanerApp(root)
    root.mainloop()