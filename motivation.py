"""
motivate.py

Usage:
    from motivate import launch_motivate
    # in your main.py, call launch_motivate(main_area)
"""

import json
import random
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

BASE_DIR = Path(__file__).parent
QUOTES_FILE = BASE_DIR / "motivate_quotes.json"

_SAMPLE_QUOTES = [
    "Success is not final; failure is not fatal: It is the courage to continue that counts.",
    "Don’t watch the clock; do what it does. Keep going.",
    "The secret of getting ahead is getting started.",
    "Believe you can and you're halfway there.",
    "Your limitation—it’s only your imagination.",
    "Push yourself, because no one else is going to do it for you."
]


def load_quotes():
    try:
        if not QUOTES_FILE.exists():
            with QUOTES_FILE.open("w", encoding="utf-8") as fh:
                json.dump(_SAMPLE_QUOTES, fh, indent=2, ensure_ascii=False)
        with QUOTES_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            if not isinstance(data, list):
                raise ValueError("Quotes file malformed (expected list).")
            return [str(q) for q in data if str(q).strip()]
    except Exception as e:
        messagebox.showerror("Quotes Load Error", f"Could not load quotes:\n{e}")
        return _SAMPLE_QUOTES.copy()


def save_quotes(quotes):
    try:
        with QUOTES_FILE.open("w", encoding="utf-8") as fh:
            json.dump(quotes, fh, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Quotes Save Error", str(e))


def _clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()


def launch_motivate(parent_frame):
    """
    Render the motivation UI inside parent_frame. Call as:
        launch_motivate(main_area)
    """
    quotes = load_quotes()
    if not quotes:
        quotes = _SAMPLE_QUOTES.copy()

    _clear_frame(parent_frame)

    # Title
    title = tk.Label(parent_frame, text="Motivate Me", font=("Comic Sans MS", 24, "bold"),
                     bg=parent_frame.cget("bg"), fg="#F28C28")
    title.place(relx=0.5, y=20, anchor="center")

    # Quote display
    quote_var = tk.StringVar(master=parent_frame, value=random.choice(quotes))
    quote_lbl = tk.Label(parent_frame, textvariable=quote_var, font=("Segoe UI", 16, "italic"),
                         wraplength=700, justify="center", bg=parent_frame.cget("bg"), fg="#FFF6E0")
    quote_lbl.place(relx=0.5, rely=0.35, anchor="center")

    # Inspire button
    def inspire():
        if not quotes:
            quote_var.set("Add some quotes below to get started!")
            return
        quote_var.set(random.choice(quotes))

    insp_btn = tk.Button(parent_frame, text="Inspire Me", command=inspire,
                         bg="#F28C28", fg="white", font=("Segoe UI", 12, "bold"), width=16)
    insp_btn.place(relx=0.5, rely=0.55, anchor="center")

    # Editor frame
    editor_fr = tk.Frame(parent_frame, bg=parent_frame.cget("bg"))
    editor_fr.place(x=40, y=380)

    tk.Label(editor_fr, text="Add a new quote:", font=("Segoe UI", 10),
             bg=parent_frame.cget("bg"), fg="#FFF6E0").grid(row=0, column=0, sticky="w")
    new_quote_entry = tk.Entry(editor_fr, width=60, font=("Segoe UI", 11))
    new_quote_entry.grid(row=1, column=0, pady=6, padx=(0, 10))

    def add_quote():
        q = new_quote_entry.get().strip()
        if not q:
            messagebox.showwarning("Empty", "Please enter a quote to add.")
            return
        quotes.append(q)
        save_quotes(quotes)
        refresh_list()
        new_quote_entry.delete(0, tk.END)
        quote_var.set(q)

    add_btn = tk.Button(editor_fr, text="Add Quote", command=add_quote,
                        bg="#FFD580", fg="#333", font=("Segoe UI", 10, "bold"))
    add_btn.grid(row=1, column=1)

    # Quotes list and delete
    list_fr = tk.Frame(parent_frame, bg=parent_frame.cget("bg"))
    list_fr.place(x=40, y=470)

    tk.Label(list_fr, text="Saved quotes:", font=("Segoe UI", 11, "bold"),
             bg=parent_frame.cget("bg"), fg="#FFF6E0").pack(anchor="w")

    quotes_listbox = tk.Listbox(list_fr, width=90, height=6, bg="#222", fg="#FFD580",
                                selectbackground="#F28C28", activestyle="none")
    quotes_listbox.pack(pady=6)

    def refresh_list():
        quotes_listbox.delete(0, tk.END)
        for q in quotes:
            display = q if len(q) <= 120 else q[:117] + "..."
            quotes_listbox.insert(tk.END, display)

    def delete_selected():
        sel = quotes_listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a quote to delete.")
            return
        idx = sel[0]
        confirmed = messagebox.askyesno("Delete", "Delete selected quote?")
        if not confirmed:
            return
        try:
            removed = quotes.pop(idx)
            save_quotes(quotes)
            refresh_list()
            # if the displayed quote was the removed one, replace
            if quote_var.get() == removed:
                quote_var.set(random.choice(quotes) if quotes else "Add some quotes below to get started!")
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))

    del_btn = tk.Button(list_fr, text="Delete Selected", command=delete_selected,
                        bg="#6c757d", fg="white", font=("Segoe UI", 10, "bold"))
    del_btn.pack(pady=(6, 0), anchor="e")

    refresh_list()
