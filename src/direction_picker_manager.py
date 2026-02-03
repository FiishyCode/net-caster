"""Direction picker manager - handles radial Q selection UI"""
import math
import sys
import os
import time
import tkinter as tk
from PIL import Image, ImageTk
from utils import pynput_keyboard, pynput_mouse


class DirectionPickerManager:
    """Manages the radial direction picker for Q selection"""
    
    def __init__(self, app_instance):
        self.app = app_instance
    
    def show_direction_picker(self):
        """Show radial compass popup with hover detection using images"""
        # Create dark overlay over app
        overlay = tk.Toplevel(self.app.root)
        overlay.overrideredirect(True)
        overlay.configure(bg='black')
        overlay.attributes('-alpha', 0.7)  # Semi-transparent
        overlay.geometry(f"{self.app.root.winfo_width()}x{self.app.root.winfo_height()}+{self.app.root.winfo_x()}+{self.app.root.winfo_y()}")

        # Create popup for direction picker
        popup = tk.Toplevel(self.app.root)
        popup.title("Select Direction")
        popup.overrideredirect(True)
        popup.configure(bg='black')
        popup.attributes('-transparentcolor', 'black')  # Make black corners transparent
        popup.attributes('-topmost', True)

        # Load direction images (handle PyInstaller bundle)
        if getattr(sys, 'frozen', False):
            script_dir = sys._MEIPASS
        else:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        img_files = {
            "NONE": "NONE.png", "N": "N.png", "NE": "NE.png",
            "E": "E.png", "SE": "SE.png", "S": "S.png", "SW": "SW.png"
        }
        images = {}
        scale = 1.1  # Scale up 10%
        for name, filename in img_files.items():
            # Images are in assets/screenshots/ directory
            img_dir = os.path.join(script_dir, "assets", "screenshots")
            path = os.path.join(img_dir, filename)
            if os.path.exists(path):
                img = Image.open(path)
                # Scale up by 10%
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                images[name] = ImageTk.PhotoImage(img)

        if not images or "NONE" not in images:
            popup.destroy()
            return

        # Get image size
        img_width = images["NONE"].width()
        img_height = images["NONE"].height()
        center_x = img_width // 2
        center_y = img_height // 2

        # Title label above canvas
        title_label = tk.Label(popup, text="Select Slot", bg='white', fg='black', font=('Arial', 12, 'bold'), padx=10, pady=5)
        title_label.pack(pady=(5, 10))

        # Create canvas
        canvas = tk.Canvas(popup, width=img_width, height=img_height, bg='black', highlightthickness=0)
        canvas.pack()
        canvas.create_image(0, 0, anchor='nw', image=images["NONE"], tags="radial")
        # White circle border (3px)
        canvas.create_oval(1, 1, img_width - 1, img_height - 1, outline='white', width=3, tags="border")
        # Show current selection in center (3px up from center)
        selected = self.app.mine_q_direction_var.get()
        canvas.create_text(center_x - 3, center_y - 3, text=selected, fill='black', font=('Arial', 10, 'bold'), tags="dirtext")

        # Store reference to prevent garbage collection
        popup.images = images
        current_dir = [None]

        def angle_to_direction(angle):
            """Convert angle (degrees, 0=right, counter-clockwise) to direction"""
            # Calibrated: N=67-113, NE=22-70, E=wraps 0, SE=290-338, S=247-295, SW=206-253
            # Ring: inner=92, outer=151
            angle = angle % 360
            if 68 <= angle < 113:       # N
                return "N"
            elif 22 <= angle < 68:      # NE
                return "NE"
            elif angle < 22 or angle >= 338:  # E (wraps around 0)
                return "E"
            elif 292 <= angle < 338:    # SE
                return "SE"
            elif 250 <= angle < 292:    # S
                return "S"
            elif 206 <= angle < 250:    # SW
                return "SW"
            # 113-206 is NW/W territory - not selectable
            return None

        def on_mouse_move(event):
            dx = event.x - center_x
            dy = center_y - event.y  # Flip Y for standard math coords
            dist = math.sqrt(dx*dx + dy*dy)

            # Only detect in the ring area (not too close to center, not outside)
            if dist < 101 or dist > 166:  # Scaled 10% (92*1.1, 151*1.1)
                new_dir = None
            else:
                angle = math.degrees(math.atan2(dy, dx))
                if angle < 0:
                    angle += 360
                new_dir = angle_to_direction(angle)

            if new_dir != current_dir[0]:
                current_dir[0] = new_dir
                img_key = new_dir if new_dir and new_dir in images else "NONE"
                canvas.delete("radial")
                canvas.create_image(0, 0, anchor='nw', image=images[img_key], tags="radial")
                # Redraw border on top
                canvas.delete("border")
                canvas.create_oval(1, 1, img_width - 1, img_height - 1, outline='white', width=3, tags="border")
                # Update center text
                canvas.delete("dirtext")
                display_text = new_dir if new_dir else self.app.mine_q_direction_var.get()
                canvas.create_text(center_x - 3, center_y - 3, text=display_text, fill='black', font=('Arial', 10, 'bold'), tags="dirtext")

        def close_picker():
            overlay.destroy()
            popup.destroy()

        def on_click(event):
            if current_dir[0]:
                self.app.mine_q_direction_var.set(current_dir[0])
                self.app.mine_q_dir_btn.configure(text=current_dir[0])
                self.app.save_settings()
            close_picker()

        def on_leave(event):
            # Reset to NONE when mouse leaves canvas
            if current_dir[0] is not None:
                current_dir[0] = None
                canvas.delete("radial")
                canvas.create_image(0, 0, anchor='nw', image=images["NONE"], tags="radial")
                canvas.delete("border")
                canvas.create_oval(1, 1, img_width - 1, img_height - 1, outline='white', width=3, tags="border")
                canvas.delete("dirtext")
                canvas.create_text(center_x - 3, center_y - 3, text=self.app.mine_q_direction_var.get(), fill='black', font=('Arial', 10, 'bold'), tags="dirtext")

        canvas.bind('<Motion>', on_mouse_move)
        canvas.bind('<Leave>', on_leave)
        canvas.bind('<Button-1>', on_click)
        popup.bind('<Button-1>', on_click)  # Click anywhere on popup closes
        overlay.bind('<Button-1>', lambda e: close_picker())  # Click overlay closes
        popup.bind('<Escape>', lambda e: close_picker())

        # Position centered over app window
        popup.update_idletasks()
        app_x = self.app.root.winfo_x()
        app_y = self.app.root.winfo_y()
        app_w = self.app.root.winfo_width()
        app_h = self.app.root.winfo_height()
        x = app_x + (app_w - img_width) // 2
        y = app_y + (app_h - img_height) // 2 - 60  # Move up 60px
        popup.geometry(f"+{x}+{y}")
        popup.focus_set()
    
    def play_mine_q_radial(self):
        """Play Q radial selection using compass direction"""
        # Direction to delta mapping (distance of 300 pixels)
        # W and NW not available in game
        dist = 300
        direction_deltas = {
            "N":  (0, -dist),
            "NE": (dist, -dist),
            "E":  (dist, 0),
            "SE": (dist, dist),
            "S":  (0, dist),
            "SW": (-dist, dist),
        }

        direction = self.app.mine_q_direction_var.get()
        dx, dy = direction_deltas.get(direction, (0, dist))  # Default to South

        print(f"[Q RADIAL] Direction: {direction}, delta: ({dx}, {dy})")

        # Press Q and wait for radial to open
        pynput_keyboard.press('q')
        time.sleep(0.3)

        # Move in steps for natural feel
        steps = 10
        for i in range(steps):
            pynput_mouse.move(dx // steps, dy // steps)
            time.sleep(0.015)

        time.sleep(0.1)
        pynput_keyboard.release('q')
        print(f"[Q RADIAL] Done - selected {direction}")
