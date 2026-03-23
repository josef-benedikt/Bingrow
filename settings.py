import tkinter as tk
import os
from PIL import Image, ImageTk

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1100, 620
ASSETS_DIR = ""

def _asset(filename):
    return os.path.join(ASSETS_DIR, filename) if ASSETS_DIR else filename

BG_IMAGE   = _asset("settingsbg.png")
MUSIC_FILE = _asset("Gameplay Music.mp3")

# Colors
CLR_GREEN_BTN   = "#5CB85C"
CLR_GREEN_DARK  = "#4A9C4A"
CLR_GREEN_TRACK = "#4A9C4A"
CLR_SLIDER_FILL = "#6DC95F"
CLR_SLIDER_KNOB = "#FFFFFF"
CLR_TEXT_YLW    = "#26A014"
CLR_TEXT_WHITE  = "#FFFFFF"
CLR_CHECK_BG    = "#5CB85C"
CLR_CHECK_TICK  = "#FFFFFF"

SLIDER_W_RATIO = 0.38
SLIDER_H       = 28
KNOB_R         = 16

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def _load_image(path, size=None):
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

# ─── DEFAULT AUDIO MANAGER ─────────────────────────────────────────────────────
class _DefaultAudioManager:
    def __init__(self):
        self.music_volume = 1.0
        self.sfx_volume   = 0.67
        self._mixer_ok    = False
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(MUSIC_FILE)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
            self._mixer_ok = True
        except Exception:
            pass

    def set_music_volume(self, v: float):
        self.music_volume = max(0.0, min(1.0, v))
        if self._mixer_ok:
            try:
                import pygame
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, v: float):
        self.sfx_volume = max(0.0, min(1.0, v))

# ─── CUSTOM SLIDER WIDGET ──────────────────────────────────────────────────────
class _Slider:
    def __init__(self, canvas, x, y, width, height, knob_r,
                 initial=1.0, on_change=None, tag_prefix="slider"):

        self.canvas    = canvas
        self.x, self.y = x, y
        self.width     = width
        self.height    = height
        self.knob_r    = knob_r
        self.value     = initial
        self.on_change = on_change
        self.tag       = tag_prefix
        self._dragging = False

        self._track_bg = canvas.create_rectangle(0,0,0,0, fill=CLR_GREEN_TRACK, outline="", tags=tag_prefix)
        self._track_fill = canvas.create_rectangle(0,0,0,0, fill=CLR_SLIDER_FILL, outline="", tags=tag_prefix)
        self._knob = canvas.create_oval(0,0,0,0, fill=CLR_SLIDER_KNOB, outline=CLR_SLIDER_FILL, width=3, tags=tag_prefix + "_knob")

        canvas.tag_bind(tag_prefix + "_knob", "<ButtonPress-1>", self._press)
        canvas.tag_bind(tag_prefix + "_knob", "<B1-Motion>", self._drag)
        canvas.tag_bind(tag_prefix + "_knob", "<ButtonRelease-1>", self._release)

    def update_position(self, x, y, width):
        self.x, self.y, self.width = x, y, width
        self._update_visuals(self.value)

    def _val_to_x(self, v):
        return self.x + v * self.width

    def _x_to_val(self, px):
        v = (px - self.x) / self.width
        return max(0.0, min(1.0, v))

    def _update_visuals(self, v):
        kx = self._val_to_x(v)
        ty = self.y + self.height // 2
        self.canvas.coords(self._track_bg, self.x, self.y, self.x + self.width, self.y + self.height)
        self.canvas.coords(self._track_fill, self.x, self.y, kx, self.y + self.height)
        self.canvas.coords(self._knob, kx - self.knob_r, ty - self.knob_r, kx + self.knob_r, ty + self.knob_r)

    def _press(self, event): self._dragging = True
    def _drag(self, event):
        if self._dragging:
            self.value = self._x_to_val(event.x)
            self._update_visuals(self.value)
            if self.on_change: self.on_change(self.value)
    def _release(self, event): self._dragging = False

# ─── SETTINGS SCREEN CLASS ─────────────────────────────────────────────────────
class SettingsScreen(tk.Frame):
    def __init__(self, parent, audio_manager=None, back_callback=None, root_window=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.audio_manager = audio_manager or _DefaultAudioManager()
        self.back_callback = back_callback
        self.root_window = root_window or parent.winfo_toplevel()
        
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self._bg_img_raw = Image.open(BG_IMAGE) if os.path.exists(BG_IMAGE) else None
        self._images = {}
        
        self._init_widgets()
        self.canvas.bind("<Configure>", self._on_resize)

    def _init_widgets(self):
        self.bg_id = self.canvas.create_image(0, 0, anchor="nw")
        self.ver_id = self.canvas.create_text(0, 0, anchor="ne", fill=CLR_TEXT_WHITE, font=("Arial", 8, "bold"), justify="right")
        
        # UI Elements
        self.music_lbl = self.canvas.create_text(0, 0, anchor="w", text="MUSIC", fill=CLR_TEXT_YLW, font=("Arial Black", 16, "bold"))
        self.music_pct = self.canvas.create_text(0, 0, anchor="e", fill=CLR_TEXT_YLW, font=("Arial Black", 16, "bold"))
        self.music_slider = _Slider(self.canvas, 0, 0, 0, SLIDER_H, KNOB_R, initial=self.audio_manager.music_volume, on_change=self._on_music_change, tag_prefix="ms")

        self.sfx_lbl = self.canvas.create_text(0, 0, anchor="w", text="SFX", fill=CLR_TEXT_YLW, font=("Arial Black", 16, "bold"))
        self.sfx_pct = self.canvas.create_text(0, 0, anchor="e", fill=CLR_TEXT_YLW, font=("Arial Black", 16, "bold"))
        self.sfx_slider = _Slider(self.canvas, 0, 0, 0, SLIDER_H, KNOB_R, initial=self.audio_manager.sfx_volume, on_change=self._on_sfx_change, tag_prefix="ss")

        self.fs_lbl = self.canvas.create_text(0, 0, anchor="e", text="FULLSCREEN MODE", fill=CLR_TEXT_YLW, font=("Arial Black", 16, "bold"))
        self.check_box = self.canvas.create_rectangle(0,0,0,0, fill=CLR_CHECK_BG, outline=CLR_GREEN_DARK, width=2, tags="fs_toggle")
        self.tick_id = self.canvas.create_text(0, 0, text="✓", fill=CLR_CHECK_TICK, font=("Arial Bold", 22, "bold"), tags="fs_toggle")
        
        # Back Button Group
        self.back_bg = self.canvas.create_rectangle(0,0,0,0, fill=CLR_GREEN_BTN, outline=CLR_GREEN_DARK, width=2, tags="back_btn")
        self.back_txt = self.canvas.create_text(0,0, text="<", fill="white", font=("Arial Black", 18, "bold"), tags="back_btn")

        # Bindings
        self.canvas.tag_bind("fs_toggle", "<Button-1>", self._toggle_fullscreen)
        self.canvas.tag_bind("back_btn", "<Button-1>", self._on_back)

    def _on_resize(self, event):
        w, h = event.width, event.height
        
        if self._bg_img_raw:
            resized = self._bg_img_raw.resize((w, h), Image.LANCZOS)
            self._images["bg"] = ImageTk.PhotoImage(resized)
            self.canvas.itemconfig(self.bg_id, image=self._images["bg"])

        mid_x = w // 2
        sw = int(w * SLIDER_W_RATIO)
        sx = mid_x - sw // 2

        self.canvas.coords(self.ver_id, w - 10, 10)
        self.canvas.itemconfig(self.ver_id, text=f"v.1.0.0\nA BONDOX STUDIOS GAME")

        # Back Button (Fixed top-left)
        self.canvas.coords(self.back_bg, 25, 25, 61, 61)
        self.canvas.coords(self.back_txt, 43, 43)

        # Sliders
        m_y = h * 0.50
        self.canvas.coords(self.music_lbl, sx, m_y - 20)
        self.canvas.coords(self.music_pct, sx + sw, m_y - 20)
        self.canvas.itemconfig(self.music_pct, text=f"{int(self.audio_manager.music_volume*100)}%")
        self.music_slider.update_position(sx, m_y, sw)

        s_y = h * 0.65
        self.canvas.coords(self.sfx_lbl, sx, s_y - 20)
        self.canvas.coords(self.sfx_pct, sx + sw, s_y - 20)
        self.canvas.itemconfig(self.sfx_pct, text=f"{int(self.audio_manager.sfx_volume*100)}%")
        self.sfx_slider.update_position(sx, s_y, sw)

        # Fullscreen
        f_y = h * 0.82
        self.canvas.coords(self.fs_lbl, mid_x - 20, f_y)
        bx = mid_x + 80
        self.canvas.coords(self.check_box, bx-22, f_y-22, bx+22, f_y+22)
        self.canvas.coords(self.tick_id, bx, f_y)
        
        is_fs = self.root_window.attributes("-fullscreen")
        self.canvas.itemconfig(self.tick_id, state="normal" if is_fs else "hidden")

    def _on_music_change(self, v):
        self.audio_manager.set_music_volume(v)
        self.canvas.itemconfig(self.music_pct, text=f"{int(v*100)}%")

    def _on_sfx_change(self, v):
        self.audio_manager.set_sfx_volume(v)
        self.canvas.itemconfig(self.sfx_pct, text=f"{int(v*100)}%")

    def _toggle_fullscreen(self, event=None):
        curr = self.root_window.attributes("-fullscreen")
        self.root_window.attributes("-fullscreen", not curr)

    def _on_back(self, event=None):
        if self.back_callback:
            self.back_callback()
        else:
            self.destroy()

# ─── INTEGRATION HELPER ────────────────────────────────────────────────────────
def show_settings_screen(parent, audio_manager=None, back_callback=None, root_window=None):
    for widget in parent.winfo_children():
        widget.destroy()
    screen = SettingsScreen(parent, audio_manager=audio_manager,
                            back_callback=back_callback, root_window=root_window)
    screen.pack(fill="both", expand=True)
    return screen

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry(f"{SCREEN_W}x{SCREEN_H}")
    # Example: back_callback=root.destroy will close the window
    app = SettingsScreen(root, back_callback=root.destroy)
    app.pack(fill="both", expand=True)
    root.mainloop()#SETTINGS HERE!
