"""
qa.py

Usage:
    from qa import launch_qa
    # in your main.py, call launch_qa(main_area)

Features:
- Loads QA pairs from qa_questions.json (creates with samples if missing).
- Lets the user ask a question, searches the local QA database for best matches,
  shows answers, and allows adding a new Q&A pair when an answer isn't found.
- Simple, dependency-free fuzzy match (word overlap / substring scoring).
- All tkinter variables/widgets are created with parent_frame as master so it's safe
  to lazy-import and use inside your existing main GUI.
"""

import json
import math
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, simpledialog

BASE_DIR = Path(__file__).parent
QA_FILE = BASE_DIR / "qa_questions.json"

_SAMPLE_QA = [
    {
        "question": "What is Python?",
        "answer": "Python is a high-level, interpreted programming language known for readability and ease of use.",
        "tags": ["python", "programming", "language"]
    },
    {
        "question": "How do I install a package with pip?",
        "answer": "Use pip install <package-name> from the command line, e.g. `pip install requests`.",
        "tags": ["pip", "install", "package"]
    },
    {
        "question": "What is Tkinter?",
        "answer": "Tkinter is Python's standard GUI toolkit for creating desktop applications.",
        "tags": ["tkinter", "gui", "python"]
    }
]


def load_qa():
    try:
        if not QA_FILE.exists():
            with QA_FILE.open("w", encoding="utf-8") as fh:
                json.dump(_SAMPLE_QA, fh, indent=2, ensure_ascii=False)
        with QA_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            # Normalize shape
            qa = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                q = str(item.get("question", "")).strip()
                a = str(item.get("answer", "")).strip()
                tags = item.get("tags", [])
                if not isinstance(tags, list):
                    tags = []
                tags = [str(t).strip().lower() for t in tags if str(t).strip()]
                if q and a:
                    qa.append({"question": q, "answer": a, "tags": tags})
            return qa
    except Exception as e:
        messagebox.showerror("QA Load Error", f"Could not load QA file:\n{e}")
        return _SAMPLE_QA.copy()


def save_qa(qa_list):
    try:
        with QA_FILE.open("w", encoding="utf-8") as fh:
            json.dump(qa_list, fh, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("QA Save Error", str(e))


def _clear_frame(frame):
    for w in frame.winfo_children():
        w.destroy()


def _tokenize(text):
    # simple whitespace + punctuation split; lowercased
    return [t for t in "".join((c if c.isalnum() else " ") for c in text.lower()).split() if t]


def _score_query_against_text(query_tokens, text_tokens):
    # Score based on overlap ratio and substring presence
    if not query_tokens or not text_tokens:
        return 0.0
    set_q = set(query_tokens)
    set_t = set(text_tokens)
    overlap = len(set_q & set_t)
    # basic overlap score normalized
    overlap_score = overlap / max(len(set_q), 1)
    # substring bonus: if full query appears in text (as substring)
    substring_bonus = 0.5 if " ".join(query_tokens) in " ".join(text_tokens) else 0.0
    return overlap_score + substring_bonus


def launch_qa(parent_frame):
    """
    Render the Q&A UI inside parent_frame. Call as:
        launch_qa(main_area)
    """
    qa_list = load_qa()

    _clear_frame(parent_frame)

    title = tk.Label(parent_frame, text="Q & A", font=("Comic Sans MS", 24, "bold"),
                     bg=parent_frame.cget("bg"), fg="#F28C28")
    title.place(relx=0.5, y=20, anchor="center")

    instr = tk.Label(parent_frame, text="Ask a question (type here) and press Search:",
                     font=("Segoe UI", 11), bg=parent_frame.cget("bg"), fg="#FFF6E0")
    instr.place(x=40, y=70)

    query_entry = tk.Entry(parent_frame, width=70, font=("Segoe UI", 12), bd=2)
    query_entry.place(x=40, y=100)

    result_frame = tk.Frame(parent_frame, bg=parent_frame.cget("bg"))
    result_frame.place(x=40, y=160, width=700, height=360)

    answer_title = tk.Label(result_frame, text="Answer:", font=("Segoe UI", 12, "bold"),
                            bg=parent_frame.cget("bg"), fg="#FFD580")
    answer_title.pack(anchor="nw")

    answer_text = tk.Text(result_frame, height=10, width=80, wrap="word", font=("Segoe UI", 11),
                          bg="#222", fg="#FFF6E0")
    answer_text.pack(fill="both", expand=False, pady=(6, 10))

    matches_label = tk.Label(result_frame, text="Best matches:", font=("Segoe UI", 11),
                             bg=parent_frame.cget("bg"), fg="#FFF6E0")
    matches_label.pack(anchor="nw")

    matches_list_frame = tk.Frame(result_frame, bg=parent_frame.cget("bg"))
    matches_list_frame.pack(fill="both", expand=True, pady=(6, 0))

    status_var = tk.StringVar(master=parent_frame, value="")
    status_lbl = tk.Label(parent_frame, textvariable=status_var, font=("Segoe UI", 10),
                          bg=parent_frame.cget("bg"), fg="#FFD580")
    status_lbl.place(relx=0.5, y=540, anchor="center")

    def render_matches(matches):
        # matches: list of (score, qa_index)
        for w in matches_list_frame.winfo_children():
            w.destroy()

        if not matches:
            tk.Label(matches_list_frame, text="No matches found. You can add this question to the database.",
                     bg=parent_frame.cget("bg"), fg="#FF6E6B", font=("Segoe UI", 11)).pack(anchor="w")
            return

        for score, idx in matches:
            qobj = qa_list[idx]
            row = tk.Frame(matches_list_frame, bg=parent_frame.cget("bg"))
            row.pack(fill="x", pady=4, anchor="w")

            q_label = tk.Label(row, text=f"Q: {qobj['question']}", font=("Segoe UI", 11, "bold"),
                               bg=parent_frame.cget("bg"), fg="#FFF6E0", anchor="w", justify="left", wraplength=560)
            q_label.pack(side="left", padx=(0,8))

            btn = tk.Button(row, text="View Answer", width=12,
                            command=lambda i=idx: show_answer(i),
                            bg="#FFD580", fg="#333", font=("Segoe UI", 10, "bold"))
            btn.pack(side="left", padx=(8,0))

            sc_lbl = tk.Label(row, text=f"{score:.2f}", font=("Segoe UI", 10),
                              bg=parent_frame.cget("bg"), fg="#AAA")
            sc_lbl.pack(side="right")

    def show_answer(idx):
        answer_text.delete("1.0", tk.END)
        answer_text.insert(tk.END, qa_list[idx]["answer"])
        status_var.set(f"Showing answer for: {qa_list[idx]['question']}")

    def on_search():
        q = query_entry.get().strip()
        if not q:
            messagebox.showwarning("Empty", "Please type a question first.")
            return
        status_var.set("Searching...")
        parent_frame.update_idletasks()

        q_toks = _tokenize(q)
        scored = []
        for i, item in enumerate(qa_list):
            text_toks = _tokenize(item["question"] + " " + " ".join(item.get("tags", [])))
            score = _score_query_against_text(q_toks, text_toks)
            # small boost if any tag equals a query token
            if any(t in q_toks for t in item.get("tags", [])):
                score += 0.25
            if score > 0:
                scored.append((score, i))
        # also include substring matches in answers (lower priority)
        for i, item in enumerate(qa_list):
            if q.lower() in item["answer"].lower():
                scored.append((0.15, i))

        # deduplicate by taking max score per index
        best = {}
        for sc, idx in scored:
            best[idx] = max(best.get(idx, 0.0), sc)
        scored_list = sorted(((s, i) for i, s in best.items()), key=lambda x: x[0], reverse=True)

        if scored_list:
            # show top 5
            render_matches(scored_list[:5])
            status_var.set(f"Found {len(scored_list)} match(es). Showing top {min(5, len(scored_list))}.")
            # auto-show top answer
            show_answer(scored_list[0][1])
        else:
            render_matches([])
            status_var.set("No good match found.")

    def add_current_as_pair():
        q = query_entry.get().strip()
        if not q:
            messagebox.showwarning("Empty", "Please type the question you want to add.")
            return
        # ask user for the answer
        ans = simpledialog.askstring("Provide Answer", "Enter the answer for this question:", parent=parent_frame)
        if not ans:
            return
        tags_input = simpledialog.askstring("Tags (optional)", "Enter comma-separated tags (optional):", parent=parent_frame)
        tags = []
        if tags_input:
            tags = [t.strip().lower() for t in tags_input.split(",") if t.strip()]
        qa_list.append({"question": q, "answer": ans.strip(), "tags": tags})
        save_qa(qa_list)
        messagebox.showinfo("Saved", "New Q&A pair has been saved.")
        status_var.set("Saved new Q&A pair.")
        # refresh search results by re-running search
        on_search()

    def show_all_entries():
        # simple viewer of all QA pairs
        popup = tk.Toplevel(master=parent_frame)
        popup.title("All Q&A")
        popup.geometry("700x500")
        listbox = tk.Listbox(popup, width=100, height=25)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        for i, item in enumerate(qa_list):
            display = f"{i+1}. Q: {item['question']}  —  A: {item['answer'][:120]}{'...' if len(item['answer'])>120 else ''}"
            listbox.insert(tk.END, display)

    # Buttons
    search_btn = tk.Button(parent_frame, text="Search", command=on_search,
                           bg="#F28C28", fg="white", font=("Segoe UI", 11, "bold"), width=12)
    search_btn.place(x=640, y=95)

    add_btn = tk.Button(parent_frame, text="Add / Teach", command=add_current_as_pair,
                        bg="#FFD580", fg="#333", font=("Segoe UI", 11, "bold"), width=12)
    add_btn.place(x=520, y=95)

    view_all_btn = tk.Button(parent_frame, text="View All", command=show_all_entries,
                             bg="#6c757d", fg="white", font=("Segoe UI", 11, "bold"), width=12)
    view_all_btn.place(x=400, y=95)

    # Help text
    help_lbl = tk.Label(parent_frame, text="Tip: If no answer is found, use 'Add / Teach' to save this Q&A for future.",
                        font=("Segoe UI", 10), bg=parent_frame.cget("bg"), fg="#AAA")
    help_lbl.place(x=40, y=520)
