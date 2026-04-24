import flet as ft
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import sys
from pathlib import Path

# --- Path Configuration ---
# This allows us to import from the parent directory without "module" errors
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # This is the 'src' folder
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Now we can import your functions from main.py
from main import run_search, run_drive_search
from utils.extract_id_from_link import extract_folder_id

def main(page: ft.Page):
    page.title = "FaceSearch Utility (Native-Pick)"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 450
    page.window.height = 650
    page.window.resizable = False

    # --- UI Refs & State ---
    target_path_val = ft.Image(src="", width=100, height=100, visible=False, fit="contain")
    search_path_val = ft.Text("None Selected", size=12, color="blue")
    output_path_val = ft.Text("data/found_images", size=12, color="blue") # Default value
    mode_selection = ft.RadioGroup(
        value="local",
        content=ft.Row([
            ft.Radio(value="local", label="Local"),
            ft.Radio(value="drive", label="Drive"),
        ]),
        on_change=lambda e: toggle_view(e.control.value)
    )
    drive_input = ft.TextField(label="Drive Link / ID", prefix_icon="link", visible=False)
    local_btn = ft.ElevatedButton("Select Search Folder", icon="folder_open", on_click=lambda _: pick_folder())
    
    # Progress visualization
    loading_ring = ft.ProgressRing(visible=False)
    status_msg = ft.Text("Ready", italic=True)
    open_folder_btn = ft.TextButton("Open Output Folder", icon="folder_open", visible=False, on_click=lambda _: os.startfile(output_path_val.value))

    # --- Helpers ---
    def pick_file():
        root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        root.destroy()
        if path: 
            target_path_val.src = path
            target_path_val.visible = True
            # We still need the path for the search logic, so we store it in data
            target_path_val.data = path 
            page.update()

    def pick_folder():
        root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
        path = filedialog.askdirectory()
        root.destroy()
        if path: search_path_val.value = path; page.update()

    def pick_output_folder():
        root = tk.Tk(); root.withdraw(); root.attributes('-topmost', True)
        path = filedialog.askdirectory()
        root.destroy()
        if path: output_path_val.value = path; page.update()

    def toggle_view(val):
        local_btn.visible = (val == "local")
        search_path_val.visible = (val == "local")
        drive_input.visible = (val == "drive")
        page.update()

    # --- Execution ---
    def start_process(e):
        t_img = getattr(target_path_val, "data", None) # Access the stored path
        out_dir = output_path_val.value # Dynamic output path 

        if not t_img:
            messagebox.showwarning("Input Missing", "Please select your face first.")
            return

        # Prepare for background work
        btn_start.disabled = True
        loading_ring.visible = True
        open_folder_btn.visible = False # Hide button when a new search starts
        status_msg.value = "AI Scanning in progress..."
        page.update()

        def worker():
            try:
                if mode_selection.value == "local":
                    s_dir = search_path_val.value
                    if s_dir != "None Selected":
                        run_search(t_img, s_dir, out_dir)
                else:
                    d_link = drive_input.value
                    if d_link:
                        folder_id = extract_folder_id(d_link)
                        run_drive_search(t_img, folder_id, out_dir)
                
                # Success
                def success_ui():
                    open_folder_btn.visible = True
                    page.update()
                    messagebox.showinfo("Done", f"Scan Complete! Files saved to: {out_dir}")

                page.run_thread(success_ui)
            except Exception as ex:
                page.run_thread(lambda: messagebox.showerror("Error", f"An error occurred: {str(ex)}"))
            finally:
                btn_start.disabled = False
                loading_ring.visible = False
                status_msg.value = "Ready"
                page.update()

        threading.Thread(target=worker, daemon=True).start()

    btn_start = ft.FilledButton("START SEARCH", icon="search", width=400, on_click=start_process)

    page.add(
        ft.Column([
            ft.Text("1. Target Selection", weight="bold"),
            ft.ElevatedButton("Pick Target Image", icon="person", on_click=lambda _: pick_file()),
            target_path_val,
            ft.Divider(),
            ft.Text("2. Mode & Path", weight="bold"),
            mode_selection,
            local_btn,
            search_path_val,
            drive_input,
            ft.Divider(),
            ft.Text("3. Output Destination", weight="bold"),
            ft.ElevatedButton("Select Output Folder", icon="folder_special", on_click=lambda _: pick_output_folder()),
            output_path_val,
            ft.Divider(),
            ft.Row([loading_ring, status_msg], alignment=ft.MainAxisAlignment.CENTER),
            open_folder_btn,
            btn_start,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    ft.app(main)