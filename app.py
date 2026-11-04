
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from docx import Document
from crossword_engine import make_puzzle

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "development-only-change-this")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {"docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def clean(value):
    return " ".join((value or "").split()).strip()


def extract_docx(file_stream):
    doc = Document(file_stream)
    metadata = {}
    answer_table = None

    for table in doc.tables:
        if not table.rows:
            continue
        headers = [clean(c.text).casefold() for c in table.rows[0].cells]
        if headers[:2] == ["answer", "definition"]:
            answer_table = table
            continue
        for row in table.rows:
            if len(row.cells) >= 2:
                key = clean(row.cells[0].text).rstrip(":")
                value = clean(row.cells[1].text)
                if key in {"Subject", "Chapter", "Topic", "Difficulty"}:
                    metadata[key] = value

    if answer_table is None:
        raise ValueError(
            "I couldn't find the required Answer and Definition table. "
            "Please use the platform's teacher template."
        )

    required = ["Subject", "Chapter", "Topic", "Difficulty"]
    missing = [
        key for key in required
        if not metadata.get(key) or metadata[key].startswith("[")
    ]
    if missing:
        raise ValueError(
            "Please complete these subject details: " + ", ".join(missing)
        )

    if metadata["Difficulty"].casefold() not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be Easy, Medium, or Hard.")

    entries = []
    for row in answer_table.rows[1:]:
        if len(row.cells) < 2:
            continue
        answer = clean(row.cells[0].text)
        definition = clean(row.cells[1].text)

        if not answer or not definition:
            continue
        if answer.casefold() in {"[enter answer]", "enter answer"}:
            continue
        if definition.casefold() in {"[enter definition]", "enter definition"}:
            continue

        entries.append({
            "answer": answer,
            "definition": definition
        })

    if len(entries) < 2:
        raise ValueError("Please add at least two complete Answer and Definition rows.")

    return metadata, entries


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/generate")
def generate():
    uploaded = request.files.get("document")

    if not uploaded or not uploaded.filename:
        flash("Please choose a Word document (.docx).", "error")
        return redirect(url_for("home"))

    if not allowed_file(uploaded.filename):
        flash("Please upload a .docx Word document.", "error")
        return redirect(url_for("home"))

    try:
        metadata, source_entries = extract_docx(uploaded)
        puzzle = make_puzzle(source_entries)

        if not puzzle["entries"]:
            raise ValueError("The system could not place any answers.")

        return render_template(
            "puzzle.html",
            metadata=metadata,
            puzzle=puzzle
        )

    except Exception as exc:
        flash(str(exc), "error")
        return redirect(url_for("home"))


@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "Crossword Learning Platform",
        "version": "0.1"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )

