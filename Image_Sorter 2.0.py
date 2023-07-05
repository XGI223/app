import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import os
from PIL import Image, ImageTk
import shutil

window = tk.Tk()
window.title("Image Sorter")

# Add columnconfigure lines
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)

source_path = ""
destination_folders = []
image_files = []
destination_list = tk.Listbox(window, width=40)
destination_list.grid(row=1, column=3, sticky="nsew")

# Define colors for light mode and dark mode
light_colors = {
    'bg': 'white',
    'fg': 'black',
}
dark_colors = {
    'bg': 'black',
    'fg': 'white',
}

# Default mode is light mode
current_colors = light_colors

def toggle_mode():
    global current_colors
    if current_colors == light_colors:
        current_colors = dark_colors
    else:
        current_colors = light_colors
    update_colors()

def update_colors():
    for child in window.children.values():
        if isinstance(child, tk.Label):
            child.config(bg=current_colors['bg'], fg=current_colors['fg'])
        if isinstance(child, tk.Entry):
            child.config(bg=current_colors['bg'], fg=current_colors['fg'])
        if isinstance(child, tk.Button):
            child.config(bg=current_colors['bg'], fg=current_colors['fg'])
        if isinstance(child, tk.Listbox):
            child.config(bg=current_colors['bg'], fg=current_colors['fg'])
    window.config(bg=current_colors['bg'])
mode_btn = tk.Button(window, text="Toggle mode", command=toggle_mode)
mode_btn.grid(row=2,column=5)

# Initialize colors
update_colors()

def add_source_folder():
    try:
        folder = fd.askdirectory(title="Select a source folder")
        source_path.set(folder)
    except:
        print("Error: Unable to open folder.")
        
def remove_source_folder():
    source_path.set("")

source_remove_btn = tk.Button(window, text="Remove", command=remove_source_folder)
source_remove_btn.grid(row=0,column=5)


def add_destination_folder():
    try:
        folder = fd.askdirectory(title="Select a destination folder")
        destination_folders.append(folder)
        destination_list.insert(tk.END, folder)
    except:
        print("Error: Unable to open folder.")

def remove_destination_folder():
    selected = destination_list.curselection()
    if selected:
        destination_list.delete(selected[0])
        destination_folders.pop(selected[0])

destination_remove_btn = tk.Button(window, text="Remove", command=remove_destination_folder)
destination_remove_btn.grid(row=1,column=5)

def run():
    for root, dirs, files in os.walk(source_path.get()):
        for file in files:
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".gif") or file.endswith(".jpeg") or file.endswith(".webp"):
                image_files.append(os.path.join(root, file))

    global label
    def display_image(image_path, index):
        global label
        image = Image.open(image_path)
        image = image.resize((600, 600), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)
        label = tk.Label(window, image=image)
        label.image = image
        label.grid(row=0, column=0, columnspan=2)  # place the label in the top row, spanning both columns
        button_index = 0  # used to keep track of the current button position in the grid
        for folder in destination_folders:
            folder_name = os.path.basename(folder)
            button = tk.Button(window, text=folder_name, command=lambda f=folder: move_image(image_path, f, index), width=15, height=2)
            button.grid(row=button_index // 2 + 3, column=button_index % 2)  # place the button in the grid, starting from the first row
            button_index += 1

    def move_image(path, destination, index):
        global label
        if not os.path.exists(destination):
            os.makedirs(destination)
        destination_path = os.path.join(destination, os.path.basename(path))
        if os.path.exists(destination_path):
            result = mb.askyesno("File already exists", "The file '{}' already exists in the destination folder. Do you want to overwrite it?".format(os.path.basename(path)))
            if not result:
                return
        shutil.move(path, destination)
        label.pack_forget()
        for button in window.children.values():
            if isinstance(button, tk.Button):
                button.pack_forget()
        index += 1
        if index < len(image_files):
            display_image(image_files[index], index)
        else:
            mb.showinfo("No more images", "There are no more images to sort.")

    if image_files:
        display_image(image_files[0], 0)
    else:
        mb.showerror("No images found", "There are no image files in the selected folder.")

source_path = tk.StringVar()
source_path_entry = tk.Entry(window, textvariable=source_path)
source_path_entry.grid(row=0, column=3)
source_path_btn = tk.Button(window, text="Add", command=add_source_folder)
source_path_btn.grid(row=0,column=4)

destination_add_btn = tk.Button(window, text="Add Folder", command=add_destination_folder)
destination_add_btn.grid(row=1,column=4)

run_btn = tk.Button(window, text="Run", command=run)
run_btn.grid(row=2,column=3, columnspan=2)

window.mainloop()