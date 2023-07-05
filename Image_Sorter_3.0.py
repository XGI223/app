import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import os
from PIL import Image, ImageTk
import shutil
import cv2
import time

window = tk.Tk()
window.title("Media Sorter")

# Set the default window size
window.geometry("800x900")

source_path = ""
destination_folders = []
media_files = []

def add_source_folder():
    try:
        folder = fd.askdirectory(title="Select a source folder")
        source_path_entry.delete(0, tk.END)
        source_path_entry.insert(tk.END, folder)
    except:
        print("Error: Unable to open folder.")

def remove_source_folder():
    source_path_entry.delete(0, tk.END)

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

def run():
    global media_files
    media_files = []

    if not source_path_entry.get():
        mb.showerror("Source folder not selected", "Please select a source folder.")
        return

    source_folder = source_path_entry.get()
    for file in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file)
        if os.path.isfile(file_path) and (file.lower().endswith(('.jpg', '.png', '.gif', '.jpeg', '.webp', '.mp4'))):
            media_files.append(file_path)

    if media_files:
        display_media(media_files[0], 0, 0)
    else:
        mb.showinfo("No media found", "There are no media files in the selected folder.")

def display_media(media_path, index, button_index):
    global label, button_frame
    if label is not None:
        label.grid_forget()
    if button_frame is not None:
        button_frame.destroy()

    if media_path.endswith((".jpg", ".png", ".gif", ".jpeg", ".webp")):
        media = Image.open(media_path)
        media = media.resize((600, 600), Image.LANCZOS)
        media = ImageTk.PhotoImage(media)
        label = tk.Label(left_frame, image=media)
        label.image = media
        label.grid(row=0, column=0, columnspan=2, sticky="nsew")

        button_frame = tk.Frame(left_frame)  # Create a new button frame in the left frame
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="se")

        button_index = 0
        for folder in destination_folders:
            folder_name = os.path.basename(folder)
            button = tk.Button(button_frame, text=folder_name, command=lambda f=folder, m=media_path, i=index, bi=button_index: move_media(m, f, i, bi), width=15, height=2)
            button.grid(row=button_index // 2, column=button_index % 2, padx=5, pady=5, sticky="nsew")
            button_index += 1
    elif media_path.endswith(".mp4"):
        display_video(media_path, index)  # Pass the index as an argument

...

def display_video(video_path, index):  # Add index as a parameter
    global label, button_frame, width, height, video
    if label is not None:
        label.grid_forget()
    if button_frame is not None:
        button_frame.destroy()

    video = cv2.VideoCapture(video_path)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    button_frame = tk.Frame(left_frame)  # Create a new button frame in the left frame
    button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="se")

    label = tk.Label(left_frame)
    label.grid(row=0, column=0, columnspan=2, sticky="nsew")

    button_index = 0
    for folder in destination_folders:
        folder_name = os.path.basename(folder)
        button = tk.Button(
            button_frame,
            text=folder_name,
            command=lambda f=folder, m=video_path, i=index, bi=button_index: move_media(m, f, i, bi),
            width=15,
            height=2,
        )
        button.grid(row=button_index // 2, column=button_index % 2, padx=5, pady=5, sticky="nsew")
        button_index += 1
    

    def update_frame():
        if not paused:
            ret, frame = video.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (600, 600))
                image = Image.fromarray(frame)
                image = ImageTk.PhotoImage(image)
                label.configure(image=image)
                label.image = image
            else:
                video.release()
        window.after(33, update_frame)  # Schedule the next frame update

    def toggle_play():
        nonlocal paused
        paused = not paused

    paused = False

    play_pause_btn = tk.Button(right_frame, text="Play/Pause", command=toggle_play)
    play_pause_btn.grid(row=3, column=0, padx=2, pady=2, sticky="e")
    

    # Open the video file
    video = cv2.VideoCapture(video_path)

    update_frame()

def move_media(media_path, destination_folder, index, button_index):
    global video
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    destination_path = os.path.join(destination_folder, os.path.basename(media_path))
    if os.path.exists(destination_path):
        result = mb.askyesno(
            "File already exists",
            "The file '{}' already exists in the destination folder. Do you want to overwrite it?".format(
                os.path.basename(media_path)
            ),
        )
        if not result:
            return

    # Stop video playback (if applicable)
    if media_path.endswith(".mp4"):
        video.release()

    time.sleep(0.1)  # Add a small delay before moving the file

    try:
        shutil.move(media_path, destination_folder)
        label.grid_forget()
        for widget in left_frame.grid_slaves():
            widget.grid_forget()
        index += 1
        if index < len(media_files):
            display_media(media_files[index], index, button_index)
        else:
            mb.showinfo("No more media", "There is no more media to sort.")
    except Exception as e:
        mb.showerror("Error", str(e))

# Create frames for left and right sections
left_frame = tk.Frame(window)
left_frame.grid(row=0, column=0, sticky="nsew")

right_frame = tk.Frame(window)
right_frame.grid(row=0, column=1, sticky="nsew")

# Configure grid for the left frame
left_frame.grid_columnconfigure(0, weight=1)
left_frame.grid_rowconfigure(0, weight=1)

# Configure grid for the right frame
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_rowconfigure(0, weight=1)
right_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_rowconfigure(2, weight=1)
right_frame.grid_rowconfigure(3, weight=1)
right_frame.grid_rowconfigure(4, weight=1)

# Configure the grid to make widgets resize with the window
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)

source_path_label = tk.Label(right_frame, text="Source Folder:")
source_path_label.grid(row=0, column=0, padx=1, pady=1, sticky="e")

source_path_entry = tk.Entry(right_frame)
source_path_entry.grid(row=0, column=1, columnspan=2, padx=1, pady=1, sticky="ew")

source_path_btn = tk.Button(right_frame, text="Browse", command=add_source_folder)
source_path_btn.grid(row=0, column=3, padx=2, pady=2, sticky="e")

destination_label = tk.Label(right_frame, text="Destination Folders:")
destination_label.grid(row=1, column=0, padx=1, pady=1, sticky="w")

destination_list_scrollbar = tk.Scrollbar(right_frame)
destination_list_scrollbar.grid(row=2, column=3, padx=1, pady=1, sticky="nsw")

destination_list = tk.Listbox(right_frame, width=40, yscrollcommand=destination_list_scrollbar.set)
destination_list.grid(row=2, column=0, columnspan=3, padx=1, pady=1, sticky="nsew")

destination_list_scrollbar.config(command=destination_list.yview)

destination_add_btn = tk.Button(right_frame, text="Add Folder", command=add_destination_folder)
destination_add_btn.grid(row=3, column=1, padx=2, pady=2, sticky="e")

destination_remove_btn = tk.Button(right_frame, text="Remove Folder", command=remove_destination_folder)
destination_remove_btn.grid(row=3, column=2, padx=2, pady=2, sticky="e")

run_btn = tk.Button(right_frame, text="Run", command=run)
run_btn.grid(row=3, column=3, padx=2, pady=2, sticky="e")

# Configure the grid to make widgets resize with the window
right_frame.grid_columnconfigure(0, weight=1)
right_frame.grid_columnconfigure(1, weight=1)
right_frame.grid_rowconfigure(2, weight=1)
right_frame.grid_rowconfigure(3, weight=1)
right_frame.grid_rowconfigure(4, weight=1)
right_frame.grid_rowconfigure(5, weight=1)

# Configure the grid to make the left frame resize with the window
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(0, weight=1)

label = None
button_frame = None
#beans

window.mainloop()
