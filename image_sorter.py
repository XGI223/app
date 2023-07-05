import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import os
from PIL import Image, ImageTk
import shutil

window = tk.Tk()
window.title("Image Sorter")

source_path = fd.askdirectory(title="Select the source folder")

destination_folders = []
while True:
    destination = fd.askdirectory(title="Select a destination folder (click 'Cancel' when finished)")
    if not destination:
        break
    destination_folders.append(destination)

image_files = []
for root, dirs, files in os.walk(source_path):
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
        button = tk.Button(window, text=folder_name, command=lambda f=folder: move_image(image_path, f, index))
        button.grid(row=button_index // 2 + 1, column=button_index % 2)  # place the button in the grid, starting from the first row
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
        mb.showinfo("No more images", "There are no more images to sort")

if image_files:
    display_image(image_files[0], 0)
else:
    mb.showerror("No images found", "There are no image files in the selected folder")

window.mainloop()