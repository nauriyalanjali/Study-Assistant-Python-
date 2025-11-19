"""
quiz.py

Usage:
    from quiz import launch_quiz
    # in your main.py, call launch_quiz(main_area)
"""

import json
import random
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

BASE_DIR = Path(__file__).parent
QUESTIONS_FILE = BASE_DIR / "quiz_questions.json"

# Sample questions (used to bootstrap quiz_questions.json if missing)
_SAMPLE_QUESTIONS = [
    {
        "question": "Which data type is immutable in Python?",
        "options": ["list", "dict", "set", "tuple"],
        "answer": 3
    },
    {
        "question": "What does HTML stand for?",
        "options": [
            "Hyperlinks and Text Markup Language",
            "Hyper Text Markup Language",
            "Home Tool Markup Language",
            "Hyperlinking Text Markup Language"
        ],
        "answer": 1
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Venus", "Mars", "Jupiter"],
        "answer": 2
    }
]


def load_questions():
    """
    Load questions from quiz_questions.json. If not present, create it with sample questions.
    Returns a list of question dicts having keys: question, options, answer (index).
    """
    try:
        if not QUESTIONS_FILE.exists():
            with QUESTIONS_FILE.open("w", encoding="utf-8") as f:
                json.dump(_SAMPLE_QUESTIONS, f, indent=2, ensure_ascii=False)
        with QUESTIONS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
            questions = []
            for q in data:
                if not isinstance(q, dict):
                    continue
                if "question" not in q or "options" not in q or "answer" not in q:
                    continue
                questions.append({
                    "question": str(q["question"]),
                    "options": [str(opt) for opt in q["options"]],
                    "answer": int(q["answer"])
                })
            if not questions:
                raise ValueError("No valid questions found in quiz_questions.json")
            return questions
    except Exception as e:
        messagebox.showerror("Quiz Load Error", f"Could not load quiz questions:\n{e}")
        return []


def _clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()


def launch_quiz(parent_frame):
    """
    Render the quiz UI inside parent_frame. This function clears parent_frame contents.
    Call it from main.py as: launch_quiz(main_area)
    """
    questions = load_questions()
    if not questions:
        return

    # UI state
    state = {
        "questions": questions.copy(),
        "order": list(range(len(questions))),
        "index": 0,
        "score": 0,
        "selected": None,  # IntVar for selected option (created per-question with explicit master)
        "user_answers": {},  # idx -> selected_index
        # create BooleanVar with explicit master to avoid "no default root" errors
        "shuffle": tk.BooleanVar(master=parent_frame, value=False)
    }

    def start_quiz():
        state["order"] = list(range(len(state["questions"])))
        if state["shuffle"].get():
            random.shuffle(state["order"])
        state["index"] = 0
        state["score"] = 0
        state["user_answers"].clear()
        show_question()

    def show_question():
        _clear_frame(parent_frame)
        qidx = state["order"][state["index"]]
        qobj = state["questions"][qidx]

        title = tk.Label(parent_frame, text="Quiz", font=("Comic Sans MS", 22, "bold"),
                         bg=parent_frame.cget("bg"), fg="#F28C28")
        title.place(relx=0.5, y=20, anchor="center")

        progress = tk.Label(parent_frame, text=f"Question {state['index']+1} of {len(state['questions'])}",
                            font=("Segoe UI", 11), bg=parent_frame.cget("bg"), fg="#FFF6E0")
        progress.place(relx=0.5, y=60, anchor="center")

        q_label = tk.Label(parent_frame, text=qobj["question"], font=("Segoe UI", 14),
                           bg=parent_frame.cget("bg"), fg="#FFF6E0", wraplength=680, justify="left")
        q_label.place(x=40, y=100)

        # create IntVar with explicit master (parent_frame) so it doesn't try to use a default root
        state["selected"] = tk.IntVar(master=parent_frame, value=-1)
        options_frame = tk.Frame(parent_frame, bg=parent_frame.cget("bg"))
        options_frame.place(x=40, y=160)

        for opt_i, opt_text in enumerate(qobj["options"]):
            rb = tk.Radiobutton(
                options_frame,
                text=opt_text,
                variable=state["selected"],
                value=opt_i,
                font=("Segoe UI", 12),
                bg=parent_frame.cget("bg"),
                fg="#FFD580",
                selectcolor=parent_frame.cget("bg"),
                activebackground=parent_frame.cget("bg"),
                anchor="w",
                justify="left"
            )
            rb.pack(anchor="w", pady=6)

        btn_frame = tk.Frame(parent_frame, bg=parent_frame.cget("bg"))
        btn_frame.place(relx=0.5, y=420, anchor="center")

        def on_next():
            sel = state["selected"].get()
            if sel == -1:
                messagebox.showwarning("No answer", "Please select an answer before continuing.")
                return
            q_real_idx = state["order"][state["index"]]
            state["user_answers"][q_real_idx] = sel
            if sel == state["questions"][q_real_idx]["answer"]:
                state["score"] += 1
            state["index"] += 1
            if state["index"] >= len(state["questions"]):
                show_results()
            else:
                show_question()

        next_text = "Finish" if state["index"] == len(state["questions"]) - 1 else "Next"
        next_btn = tk.Button(btn_frame, text=next_text, command=on_next, bg="#F28C28", fg="white",
                             font=("Segoe UI", 12, "bold"), width=12)
        next_btn.pack(side="left", padx=8)

        quit_btn = tk.Button(btn_frame, text="Quit", command=lambda: show_start(), bg="#6c757d", fg="white",
                             font=("Segoe UI", 12), width=10)
        quit_btn.pack(side="left", padx=8)

    def show_results():
        _clear_frame(parent_frame)
        total = len(state["questions"])
        score = state["score"]

        title = tk.Label(parent_frame, text="Quiz Results", font=("Comic Sans MS", 22, "bold"),
                         bg=parent_frame.cget("bg"), fg="#F28C28")
        title.place(relx=0.5, y=20, anchor="center")

        score_lbl = tk.Label(parent_frame, text=f"You scored {score} out of {total}", font=("Segoe UI", 16),
                             bg=parent_frame.cget("bg"), fg="#FFF6E0")
        score_lbl.place(relx=0.5, y=70, anchor="center")

        review_btn = tk.Button(parent_frame, text="Review Answers", command=show_review,
                               bg="#FFD580", fg="#333", font=("Segoe UI", 12, "bold"), width=16)
        review_btn.place(relx=0.5, y=120, anchor="center")

        restart_btn = tk.Button(parent_frame, text="Restart Quiz", command=start_quiz,
                                bg="#F28C28", fg="white", font=("Segoe UI", 12, "bold"), width=16)
        restart_btn.place(relx=0.5, y=170, anchor="center")

        done_btn = tk.Button(parent_frame, text="Back to Home", command=lambda: parent_frame.event_generate("<<SHOW_HOME>>"),
                             bg="#6c757d", fg="white", font=("Segoe UI", 12, "bold"), width=16)
        done_btn.place(relx=0.5, y=220, anchor="center")

    def show_review():
        _clear_frame(parent_frame)
        title = tk.Label(parent_frame, text="Review", font=("Comic Sans MS", 20, "bold"),
                         bg=parent_frame.cget("bg"), fg="#F28C28")
        title.place(relx=0.5, y=14, anchor="center")

        canvas = tk.Canvas(parent_frame, bg=parent_frame.cget("bg"), highlightthickness=0)
        canvas.place(relx=0.5, rely=0.06, relwidth=0.92, relheight=0.84, anchor="n")

        inner = tk.Frame(canvas, bg=parent_frame.cget("bg"))
        canvas.create_window((0, 0), window=inner, anchor="nw")

        for i, q in enumerate(state["questions"]):
            q_frame = tk.Frame(inner, bg=parent_frame.cget("bg"))
            q_frame.pack(fill="x", pady=8, padx=4, anchor="w")
            q_lbl = tk.Label(q_frame, text=f"{i+1}. {q['question']}", font=("Segoe UI", 12, "bold"),
                             bg=parent_frame.cget("bg"), fg="#FFF6E0", wraplength=700, justify="left")
            q_lbl.pack(anchor="w")
            ua = state["user_answers"].get(i, None)
            for opt_idx, opt in enumerate(q["options"]):
                txt = opt
                if opt_idx == q["answer"]:
                    txt = f"✔ {txt}"
                    fg = "#A6E22E"
                elif ua == opt_idx:
                    txt = f"✖ {txt}"
                    fg = "#FF6B6B"
                else:
                    fg = "#FFD580"
                opt_lbl = tk.Label(q_frame, text=f"    {txt}", font=("Segoe UI", 11),
                                   bg=parent_frame.cget("bg"), fg=fg, anchor="w", justify="left")
                opt_lbl.pack(anchor="w", padx=6)

        inner.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        back_btn = tk.Button(parent_frame, text="Back to Results", command=show_results,
                             bg="#F28C28", fg="white", font=("Segoe UI", 12, "bold"), width=16)
        back_btn.place(relx=0.5, y=570, anchor="center")

    def show_start():
        _clear_frame(parent_frame)
        title = tk.Label(parent_frame, text="Quiz", font=("Comic Sans MS", 26, "bold"),
                         bg=parent_frame.cget("bg"), fg="#F28C28")
        title.place(relx=0.5, y=40, anchor="center")

        info = tk.Label(parent_frame, text=f"Questions: {len(state['questions'])}", font=("Segoe UI", 12),
                        bg=parent_frame.cget("bg"), fg="#FFF6E0")
        info.place(relx=0.5, y=90, anchor="center")

        shuffle_cb = tk.Checkbutton(parent_frame, text="Shuffle Questions", variable=state["shuffle"],
                                    font=("Segoe UI", 11), bg=parent_frame.cget("bg"), fg="#FFD580",
                                    selectcolor=parent_frame.cget("bg"), activebackground=parent_frame.cget("bg"))
        shuffle_cb.place(relx=0.5, y=130, anchor="center")

        start_btn = tk.Button(parent_frame, text="Start Quiz", command=start_quiz,
                              bg="#F28C28", fg="white", font=("Segoe UI", 14, "bold"), width=16)
        start_btn.place(relx=0.5, y=180, anchor="center")

        def open_questions_file():
            try:
                import os, sys
                messagebox.showinfo("Edit Questions", f"Edit {QUESTIONS_FILE.name} to add/remove questions.\nFile path:\n{QUESTIONS_FILE}")
                if sys.platform.startswith("win"):
                    os.startfile(QUESTIONS_FILE)
                elif sys.platform == "darwin":
                    os.system(f"open {QUESTIONS_FILE!s}")
                else:
                    os.system(f"xdg-open {QUESTIONS_FILE!s}")
            except Exception as e:
                messagebox.showerror("Open File Error", str(e))

        edit_btn = tk.Button(parent_frame, text="Edit Questions", command=open_questions_file,
                             bg="#FFD580", fg="#333", font=("Segoe UI", 11, "bold"))
        edit_btn.place(relx=0.5, y=230, anchor="center")

    show_start()
