from tkinter import *
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from voice import Voice
from assistant_commands import process_command
import threading


# -----------------------------
# Initialize Voice Engine
# -----------------------------
assistant_voice = Voice()

# -----------------------------
# Create Main App Window
# -----------------------------
root = Tk()
root.title("AI Study Assistant")
root.geometry("900x600")
root.resizable(False, False)

# Apply modern theme
style = Style(theme="cosmo")  # You can also try: 'minty', 'flatly', 'solar'
root.configure(bg="#FFF6E0")  # Soft pastel yellow background

# -----------------------------
# Header
# -----------------------------
title_label = Label(
    root,
    text="🎓 Study Assistant",
    font=("Comic Sans MS", 26, "bold"),
    bg="#FFF6E0",
    fg="#F28C28"
)
title_label.pack(pady=20)

# -----------------------------
# Assistant Cartoon Area
# -----------------------------
try:
    # Optional: replace with your own cartoon image later
    img = Image.open("assistant.png")  # Add your cartoon image in same folder
    img = img.resize((150, 150))
    assistant_img = ImageTk.PhotoImage(img)
    img_label = Label(root, image=assistant_img, bg="#FFF6E0")
    img_label.pack(pady=10)
except:
    img_label = Label(
        root,
        text="🤖",
        font=("Arial", 80),
        bg="#FFF6E0"
    )
    img_label.pack(pady=10)

# -----------------------------
# Message Label
# -----------------------------
status_label = Label(
    root,
    text="Hey, I’m ready to help you!",
    font=("Segoe UI", 14, "italic"),
    bg="#FFF6E0",
    fg="#555"
)
status_label.pack(pady=10)

# -----------------------------
# Feature Buttons Area
# -----------------------------
button_frame = Frame(root, bg="#FFF6E0")
button_frame.pack(pady=20)

features = ["🧠 Q&A", "📝 Notes", "📅 Planner", "🎮 Quiz", "💡 Motivate Me"]
for f in features:
    Button(
        button_frame,
        text=f,
        font=("Segoe UI", 12, "bold"),
        width=15,
        relief="ridge",
        bg="#FFD580",
        fg="#333",
        activebackground="#F28C28",
        cursor="hand2"
    ).pack(side=LEFT, padx=8)

# -----------------------------
# Mic Button (Bottom Center)
# -----------------------------
def start_listening():
    status_label.config(text="Listening...")
    mic_button.config(state=DISABLED)
    threading.Thread(target=listen_and_process, daemon=True).start()

def listen_and_process():
    query = assistant_voice.listen_once()  # ✅ using Voice class
    if query:
        status_label.config(text=f"You said: {query}")
        assistant_voice.speak(f"You said {query}")
        process_command(query)
    else:
        assistant_voice.speak("I didn’t catch that, please try again!")
    status_label.config(text="Hey, I’m ready to help you!")
    mic_button.config(state=NORMAL)

mic_frame = Frame(root, bg="#FFF6E0")
mic_frame.pack(side=BOTTOM, pady=20)

mic_button = Button(
    mic_frame,
    text="🎤",
    font=("Segoe UI", 20),
    bg="#F28C28",
    fg="white",
    activebackground="#FFB347",
    width=4,
    height=1,
    relief="flat",
    command=start_listening,
    cursor="hand2"
)
mic_button.pack()

# -----------------------------
# Greet on startup (non-blocking)
# -----------------------------
def greet_user():
    assistant_voice.speak("Hello! I’m your Study Assistant. Click the mic to talk to me!", block=False)

root.after(1000, greet_user)

# -----------------------------
# Run App
# -----------------------------
root.mainloop()
