from transformers import pipeline

# Load the summarization pipeline once at import
summarizer = pipeline("summarization", model="t5-small")

def summarize_notes(notes_text):
    # HuggingFace models work best with < 2000 chars
    if len(notes_text) > 2000:
        notes_text = notes_text[:2000]
    result = summarizer(notes_text, max_length=80, min_length=25, do_sample=False)
    return result[0]['summary_text']
