# main.py
# Updated Study Assistant main GUI with lazy-loading for quiz, motivate, qa and voice modules,
# safe working directory, and improved tkinter usage.

import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from PIL import Image, ImageTk, ImageEnhance
import itertools
import time
import random
import datetime
import os
from pathlib import Path
import speech_recognition as sr
import importlib
import importlib.util
import traceback
import sys

# Ensure working directory is the script's directory so relative imports/files work
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

# --- User Settings ---
USER_NAME = "Anjali"

# --- Motivational Quotes (fallback) ---
QUOTES = [
    "Success is not the key to happiness. Happiness is the key to success.",
    "Don’t watch the clock; do what it does. Keep going.",
    "The secret of getting ahead is getting started.",
    "Believe you can and you're halfway there.",
    "Your limitation—it’s only your imagination.",
    "Push yourself, because no one else is going to do it for you."
]

# --- Theme and Style ---
style = Style(theme="flatly")
bg_gradient_top = "#232526"
accent = "#F28C28"
sidebar_bg = "#1c232b"
card_bg = "#FFF6E0"
card_fg = "#333"
active_card_bg = "#FFD580"

# --- Tk root ---
root = tk.Tk()
root.title("🐾 Study Assistant")
root.geometry("1000x650")
root.resizable(False, False)
root.configure(bg=bg_gradient_top)

# --- Gradient Background ---
canvas = tk.Canvas(root, width=1000, height=650, highlightthickness=0)
canvas.pack(fill="both", expand=True)
for i in range(0, 650):
    # simple linear interpolation for a gradient effect
    r = int(35 + (255 - 35) * i / 650)
    g = int(37 + (204 - 37) * i / 650)
    b = int(38 + (128 - 38) * i / 650)
    color = f"#{r:02x}{g:02x}{b:02x}"
    canvas.create_line(0, i, 1000, i, fill=color)

# --- Sidebar Navigation ---
sidebar = tk.Frame(root, width=180, height=650, bg=sidebar_bg)
sidebar.place(x=0, y=0)

# --- User Profile / Avatar ---
profile_img_path = BASE_DIR / "cat_assistant.png"
avatar_img_raw = None
avatar_photo = None
try:
    avatar_img_raw = Image.open(profile_img_path).resize((80, 80))
    enhancer = ImageEnhance.Brightness(avatar_img_raw)
    avatar_img_proc = enhancer.enhance(1.15)
    avatar_photo = ImageTk.PhotoImage(avatar_img_proc)
except Exception:
    avatar_photo = None

profile_frame = tk.Frame(sidebar, bg=sidebar_bg)
profile_frame.place(x=40, y=30)
if avatar_photo:
    avatar_label = tk.Label(profile_frame, image=avatar_photo, bg=sidebar_bg)
    avatar_label.image = avatar_photo
    avatar_label.pack()
else:
    avatar_label = tk.Label(profile_frame, text="🐱", font=("Arial", 40), bg=sidebar_bg, fg="white")
    avatar_label.pack()

tk.Label(profile_frame, text=USER_NAME, font=("Segoe UI", 14), bg=sidebar_bg, fg="white").pack()
tk.Label(profile_frame, text="Study Assistant", font=("Segoe UI", 10), bg=sidebar_bg, fg="#FFCC80").pack()

# --- Main Area Frame ---
main_area = tk.Frame(root, bg="", width=800, height=650)
main_area.place(x=180, y=0)

# allow modules to return to home by generating this virtual event
main_area.bind("<<SHOW_HOME>>", lambda e: show_home() if "show_home" in globals() else None)

# --- Avatar pulse animation using after (main-thread safe) ---
pulse_alphas = list(range(100, 130, 2)) + list(range(130, 100, -2))
_pulse_index = 0


def avatar_pulse_step():
    global _pulse_index
    if avatar_img_raw:
        alpha = pulse_alphas[_pulse_index % len(pulse_alphas)] / 100.0
        faded = ImageEnhance.Brightness(avatar_img_raw).enhance(alpha)
        faded_img = ImageTk.PhotoImage(faded)
        avatar_label.configure(image=faded_img)
        avatar_label.image = faded_img
    _pulse_index += 1
    root.after(60, avatar_pulse_step)


avatar_pulse_step()

# --- Utilities ---
feature_cards = []


def clear_main_area():
    for widget in main_area.winfo_children():
        widget.destroy()
    feature_cards.clear()


# --- Home Screen ---
def show_home():
    clear_main_area()
    hour = datetime.datetime.now().hour
    if hour < 12:
        greet = "Good morning"
    elif hour < 18:
        greet = "Good afternoon"
    else:
        greet = "Good evening"

    greet_lbl = tk.Label(main_area, text=f"{greet}, people! 👋", font=("Comic Sans MS", 28, "bold"),
                        bg=bg_gradient_top, fg=accent)
    greet_lbl.place(relx=0.5, y=60, anchor="center")

    quote_var = tk.StringVar(value=random.choice(QUOTES))
    quote_lbl = tk.Label(main_area, textvariable=quote_var, font=("Segoe UI", 16, "italic"),
                         bg=bg_gradient_top, fg="#FFF6E0", wraplength=700, padx=20)
    quote_lbl.place(relx=0.5, y=120, anchor="center")

    def rotate_quote():
        quote_var.set(random.choice(QUOTES))
        root.after(5000, rotate_quote)

    rotate_quote()

    card_titles = ["Q&A", "Notes", "Planner", "Quiz", "Motivate Me"]
    card_icons = ["🧠", "📝", "📅", "🎮", "💡"]
    for idx, (title, icon) in enumerate(zip(card_titles, card_icons)):
        x_pos = 160 + idx * 125
        card = tk.Frame(main_area, bg=card_bg, width=110, height=150, highlightthickness=2,
                        highlightbackground=active_card_bg)
        card.place(x=x_pos, y=220)
        tk.Label(card, text=icon, font=("Arial", 38), bg=card_bg).pack(pady=10)
        tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), bg=card_bg, fg=card_fg).pack()

        def on_enter(event, c=card):
            c.config(bg=active_card_bg)

        def on_leave(event, c=card):
            c.config(bg=card_bg)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        feature_cards.append(card)

    progress_label = tk.Label(main_area, text="Today's Progress", font=("Segoe UI", 14),
                             bg=bg_gradient_top, fg="#FFF6E0")
    progress_label.place(x=350, y=420)
    progress_canvas = tk.Canvas(main_area, width=300, height=18, bg="#444", highlightthickness=0)
    progress_canvas.place(x=340, y=450)
    progress_fill = progress_canvas.create_rectangle(0, 0, 0, 18, fill=accent, outline="")

    def animate_progress(curr=0, target=180):
        if curr <= target:
            progress_canvas.coords(progress_fill, 0, 0, curr, 18)
            root.after(20, lambda: animate_progress(curr + 4, target))

    animate_progress()


# --- Generic placeholder feature ---
def show_feature(name):
    clear_main_area()
    tk.Label(main_area, text=f"{name} Module Coming Soon!", font=("Segoe UI", 24, "bold"),
             bg=bg_gradient_top, fg=accent).place(relx=0.5, y=100, anchor="center")


# --- Notes Summarizer UI (imports summarizer lazily inside function) ---
def show_notes_summarizer():
    clear_main_area()
    tk.Label(main_area, text="Notes Summarizer", font=("Comic Sans MS", 24, "bold"),
             bg=bg_gradient_top, fg=accent).place(relx=0.5, y=40, anchor="center")

    tk.Label(main_area, text="Paste your notes below:", font=("Segoe UI", 12),
             bg=bg_gradient_top, fg="#FFF6E0").place(x=60, y=90)

    notes_entry = tk.Text(main_area, height=13, width=70, font=("Segoe UI", 11))
    notes_entry.place(x=60, y=120)

    summary_label = tk.Label(main_area, text="Summary will appear here.", font=("Segoe UI", 12, "italic"),
                             bg=bg_gradient_top, fg="#FFD580", wraplength=700, justify="left")
    summary_label.place(x=60, y=370)

    def do_summarize():
        notes = notes_entry.get("1.0", tk.END).strip()
        if notes:
            summary_label.config(text="Summarizing...", fg="grey")
            root.update_idletasks()
            try:
                from summarizer import summarize_notes
                summary = summarize_notes(notes)
                summary_label.config(text=summary, fg="#FFD580")
            except ModuleNotFoundError:
                summary_label.config(text="summarizer.py not found. Place it next to main.py", fg="red")
            except Exception as e:
                summary_label.config(text=f"Error: {e}", fg="red")
        else:
            summary_label.config(text="Please enter some notes!", fg="red")

    summarize_btn = tk.Button(main_area, text="Summarize Notes", command=do_summarize,
                              bg=accent, fg="white", font=("Segoe UI", 12, "bold"))
    summarize_btn.place(x=60, y=330)


# --- Planner (tasks) UI ---
def show_planner():
    clear_main_area()
    tk.Label(main_area, text="Daily Planner", font=("Comic Sans MS", 24, "bold"),
             bg=bg_gradient_top, fg=accent).place(relx=0.5, y=40, anchor="center")

    tk.Label(main_area, text="Add a new task:", font=("Segoe UI", 12),
             bg=bg_gradient_top, fg="#FFF6E0").place(x=60, y=90)

    task_entry = tk.Entry(main_area, width=50, font=("Segoe UI", 12))
    task_entry.place(x=60, y=120)

    tasks_container = {"frame": None}
    tasks_file = BASE_DIR / "tasks.txt"

    def load_tasks():
        if tasks_container["frame"] is not None:
            tasks_container["frame"].destroy()
        new_frame = tk.Frame(main_area, bg=bg_gradient_top)
        new_frame.place(x=60, y=200)
        tasks_container["frame"] = new_frame
        try:
            if not tasks_file.exists():
                tasks_file.write_text("")
            with tasks_file.open("r", encoding="utf-8") as f:
                tasks = [line.strip() for line in f.readlines() if line.strip()]
            for idx, task in enumerate(tasks):
                tk.Label(new_frame, text=f"• {task}", font=("Segoe UI", 12),
                         bg=bg_gradient_top, fg="#FFD580", anchor="w").pack(anchor="w")
        except Exception as e:
            messagebox.showerror("Error loading tasks", str(e))

    load_tasks()

    def add_task():
        task = task_entry.get().strip()
        if task:
            try:
                with tasks_file.open("a", encoding="utf-8") as f:
                    f.write(task + "\n")
                task_entry.delete(0, tk.END)
                load_tasks()
            except Exception as e:
                messagebox.showerror("Error saving task", str(e))
        else:
            messagebox.showwarning("Empty Task", "Please enter a task first!")

    add_btn = tk.Button(main_area, text="Add Task", command=add_task,
                        bg=accent, fg="white", font=("Segoe UI", 12, "bold"))
    add_btn.place(x=60, y=150)


# --- Voice Command using speech_recognition (keeps simple) ---
def show_voice_command():
    clear_main_area()
    tk.Label(main_area, text="Voice Command", font=("Comic Sans MS", 24, "bold"),
             bg=bg_gradient_top, fg=accent).place(relx=0.5, y=40, anchor="center")

    output_label = tk.Label(main_area, text="Press 'Start Listening' to begin.",
                            font=("Segoe UI", 12), bg=bg_gradient_top, fg="#FFF6E0",
                            wraplength=700, justify="center")
    output_label.place(relx=0.5, rely=0.5, anchor="center")

    def listen_voice():
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                output_label.config(text="Listening...", fg="grey")
                root.update_idletasks()
                audio = r.listen(source, phrase_time_limit=5)
        except OSError:
            messagebox.showerror("Microphone Error", "No microphone found or it is in use.")
            return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        try:
            text = r.recognize_google(audio)
            output_label.config(text=f"You said: {text}", fg="#FFD580")
        except sr.UnknownValueError:
            output_label.config(text="Sorry, I couldn’t understand that.", fg="red")
        except Exception as e:
            output_label.config(text=f"Error: {e}", fg="red")

    tk.Button(main_area, text="🎙️ Start Listening", command=listen_voice,
              bg=accent, fg="white", font=("Segoe UI", 12, "bold")).place(relx=0.5, y=450, anchor="center")


# --- Lazy import launcher for Quiz ---
def open_quiz_lazy():
    clear_main_area()
    print("Quiz button clicked: attempting lazy import of quiz.py", file=sys.stderr)
    try:
        importlib.invalidate_caches()
        import quiz
        importlib.reload(quiz)
        if hasattr(quiz, "launch_quiz"):
            quiz.launch_quiz(main_area)
        else:
            messagebox.showerror("Quiz Error", "quiz.py does not provide launch_quiz(parent_frame).")
    except Exception as e:
        tb = traceback.format_exc()
        print("Error importing/launching quiz.py:\n", tb, file=sys.stderr)
        messagebox.showerror("Quiz Import Error", f"Could not import or start quiz.py:\n{e}\n\nSee console for details.")


# --- Robust lazy import launcher for Motivate (tries multiple candidate filenames) ---
def open_motivate_lazy():
    clear_main_area()
    print("Motivate button clicked: attempting lazy import of motivate.py/motivation.py", file=sys.stderr)
    try:
        candidates = ["motivate.py", "motivation.py", "motivate_me.py"]
        found = None
        for name in candidates:
            target = BASE_DIR / name
            if target.exists():
                found = target
                break

        # if not found in the candidates, try to find any file that starts with "motivat"
        if found is None:
            for f in os.listdir(BASE_DIR):
                if f.lower().startswith("motivat") and f.lower().endswith(".py"):
                    found = BASE_DIR / f
                    break

        if found is None:
            files = "\n".join(sorted(os.listdir(BASE_DIR)))
            messagebox.showerror(
                "Motivate Import Error",
                f"motivate.py (or equivalent) not found in:\n{BASE_DIR}\n\nFiles in folder:\n{files}"
            )
            return

        # Load module directly from file to avoid sys.path/module name issues
        spec = importlib.util.spec_from_file_location("studyassistant_motivate", str(found))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create import spec for {found}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "launch_motivate"):
            module.launch_motivate(main_area)
        else:
            messagebox.showerror("Motivate Error", f"{found.name} does not provide launch_motivate(parent_frame).")
    except Exception as e:
        tb = traceback.format_exc()
        print("Error importing/launching motivate module:\n", tb, file=sys.stderr)
        messagebox.showerror("Motivate Import Error", f"Could not import or start motivate module:\n{e}\n\nSee console for details.")


# --- Robust lazy import launcher for Q&A (loads by file path) ---
def open_qa_lazy():
    clear_main_area()
    print("Q&A button clicked: attempting lazy import of qa.py", file=sys.stderr)
    try:
        # common names to try
        candidates = ["qa.py", "qa_module.py", "questions_qa.py"]
        found = None
        for name in candidates:
            target = BASE_DIR / name
            if target.exists():
                found = target
                break

        # fallback: find any file starting with "qa" or "qa_" or containing "qa"
        if found is None:
            for f in os.listdir(BASE_DIR):
                low = f.lower()
                if (low.startswith("qa") or low.startswith("q_a") or "qa" in low) and low.endswith(".py"):
                    found = BASE_DIR / f
                    break

        if found is None:
            files = "\n".join(sorted(os.listdir(BASE_DIR)))
            messagebox.showerror(
                "Q&A Import Error",
                f"qa.py (or equivalent) not found in:\n{BASE_DIR}\n\nFiles in folder:\n{files}"
            )
            return

        # Load module directly from file to avoid sys.path/module name issues
        spec = importlib.util.spec_from_file_location("studyassistant_qa", str(found))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create import spec for {found}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "launch_qa"):
            module.launch_qa(main_area)
        else:
            messagebox.showerror("Q&A Error", f"{found.name} does not provide launch_qa(parent_frame).")
    except Exception as e:
        tb = traceback.format_exc()
        print("Error importing/launching qa module:\n", tb, file=sys.stderr)
        messagebox.showerror("Q&A Import Error", f"Could not import or start qa module:\n{e}\n\nSee console for details.")


# --- NEW: Robust lazy import launcher for Voice (looks in root and assistant/) ---
def open_voice_lazy():
    clear_main_area()
    print("Voice button clicked: attempting lazy import of voice.py (root or assistant/)", file=sys.stderr)
    try:
        # candidate locations
        candidates = [
            BASE_DIR / "voice.py",
            BASE_DIR / "assistant" / "voice.py",
            BASE_DIR / "assistant" / "voice_module.py",
            BASE_DIR / "assistant" / "voice_command.py"
        ]
        found = None
        for p in candidates:
            if p.exists():
                found = p
                break

        # fallback: search for any file starting with "voice" in root or assistant folder
        if found is None:
            for folder in (BASE_DIR, BASE_DIR / "assistant"):
                if folder.exists():
                    for f in os.listdir(folder):
                        low = f.lower()
                        if low.startswith("voice") and low.endswith(".py"):
                            found = folder / f
                            break
                    if found:
                        break

        if found is None:
            files = "\n".join(sorted(os.listdir(BASE_DIR)))
            assistant_files = ""
            assistant_dir = BASE_DIR / "assistant"
            if assistant_dir.exists():
                assistant_files = "\n".join(sorted(os.listdir(assistant_dir)))
            messagebox.showerror(
                "Voice Import Error",
                f"voice.py not found in:\n{BASE_DIR}\n\nFiles in folder:\n{files}\n\nassistant/ contents:\n{assistant_files}"
            )
            return

        # load module by file path
        spec = importlib.util.spec_from_file_location("studyassistant_voice", str(found))
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create import spec for {found}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # helper to append a task (used by voice commands)
        def __add_task_quick(task_text):
            tasks_file = BASE_DIR / "tasks.txt"
            try:
                with tasks_file.open("a", encoding="utf-8") as fh:
                    fh.write(task_text + "\n")
            except Exception as ex:
                messagebox.showerror("Add Task Error", str(ex))
            try:
                show_planner()
            except Exception:
                pass

        def __time_callback():
            now = datetime.datetime.now()
            return now.strftime("It's %I:%M %p")

        callbacks = {
            "open_quiz": lambda: open_quiz_lazy(),
            "open_planner": lambda: show_planner(),
            "open_notes": lambda: show_notes_summarizer(),
            "open_qa": lambda: open_qa_lazy(),
            "open_motivate": lambda: open_motivate_lazy(),
            "add_task": lambda t: __add_task_quick(t),
            "summarize": lambda: show_notes_summarizer(),
            "time": lambda: __time_callback()
        }

        # verify and launch
        if hasattr(module, "launch_voice"):
            module.launch_voice(main_area, command_callbacks=callbacks)
        else:
            messagebox.showerror("Voice Error", f"{found.name} does not provide launch_voice(parent_frame, command_callbacks).")
    except Exception as e:
        tb = traceback.format_exc()
        print("Error importing/launching voice module:\n", tb, file=sys.stderr)
        messagebox.showerror("Voice Import Error", f"Could not import or start voice module:\n{e}\n\nSee console for details.")


# --- Sidebar buttons (wiring quiz, motivate, qa & voice lazily) ---
sidebar_features = [
    ("🏠 Home", lambda: show_home()),
    ("🧠 Q&A", open_qa_lazy),
    ("📝 Notes", show_notes_summarizer),
    ("📅 Planner", show_planner),
    ("🎮 Quiz", open_quiz_lazy),
    ("🎤 Voice Command", open_voice_lazy),
    ("💡 Motivate Me", open_motivate_lazy)
]

sidebar_btns = []
for idx, (txt, cmd) in enumerate(sidebar_features):
    btn = tk.Button(sidebar, text=txt, font=("Segoe UI", 12, "bold"),
                    width=15, relief="flat", bg=sidebar_bg, fg="#FFCC80",
                    activebackground=accent, activeforeground="white",
                    cursor="hand2", anchor="w", command=cmd)
    btn.place(x=10, y=150 + idx * 50)
    sidebar_btns.append(btn)

# --- Start with Home Screen ---
show_home()

# Bind event for other modules to return home (safe: show_home exists now)
main_area.bind("<<SHOW_HOME>>", lambda e: show_home())

# --- Mainloop ---
root.mainloop()
