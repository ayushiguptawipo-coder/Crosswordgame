
import re
import random


def normalize_answer(answer):
    return re.sub(r"[^A-Z]", "", answer.upper())


def make_puzzle(source_entries):
    entries = []
    seen = set()

    for item in source_entries:
        answer = normalize_answer(item["answer"])

        if len(answer) < 2:
            continue

        if answer in seen:
            continue

        seen.add(answer)
        entries.append({
            "answer": answer,
            "original": item["answer"],
            "clue": item["definition"]
        })

    entries.sort(key=lambda item: len(item["answer"]), reverse=True)

    if not entries:
        return {"grid": [], "entries": [], "across": [], "down": []}

    best_result = None

    # Try different word orders to improve the number of intersections.
    for attempt in range(30):
        ordered = entries[:]

        if attempt:
            random.shuffle(ordered)
            ordered.sort(
                key=lambda item: len(item["answer"]) + random.random() * 4,
                reverse=True
            )

        result = build_grid(ordered)

        if best_result is None or len(result["entries"]) > len(best_result["entries"]):
            best_result = result

        if len(best_result["entries"]) == len(entries):
            break

    return best_result


def build_grid(entries):
    size = 60
    board = {}
    placed = []
    directions = ["across", "down"]

    first = entries[0]
    start_row = size // 2
    start_col = (size - len(first["answer"])) // 2

    place_word(board, first["answer"], start_row, start_col, "across")
    placed.append({
        **first,
        "row": start_row,
        "col": start_col,
        "direction": "across"
    })

    for entry in entries[1:]:
        answer = entry["answer"]
        candidates = []

        for existing in placed:
            for i, letter in enumerate(answer):
                for j, existing_letter in enumerate(existing["answer"]):
                    if letter != existing_letter:
                        continue

                    direction = (
                        "down" if existing["direction"] == "across"
                        else "across"
                    )

                    if direction == "across":
                        row = existing["row"] + j
                        col = existing["col"] + i
                    else:
                        row = existing["row"] + i
                        col = existing["col"] + j

                    if can_place(board, answer, row, col, direction):
                        candidates.append((row, col, direction))

        if candidates:
            row, col, direction = random.choice(candidates)
            place_word(board, answer, row, col, direction)
            placed.append({
                **entry,
                "row": row,
                "col": col,
                "direction": direction
            })

    if not placed:
        return {"grid": [], "entries": [], "across": [], "down": []}

    min_row = min(
        p["row"] for p in placed
    )
    min_col = min(
        p["col"] for p in placed
    )

    max_row = max(
        p["row"] + (len(p["answer"]) if p["direction"] == "down" else 1)
        for p in placed
    )
    max_col = max(
        p["col"] + (len(p["answer"]) if p["direction"] == "across" else 1)
        for p in placed
    )

    grid = []
    for row in range(min_row, max_row):
        grid_row = []
        for col in range(min_col, max_col):
            grid_row.append(board.get((row, col), ""))
        grid.append(grid_row)

    for item in placed:
        item["row"] -= min_row
        item["col"] -= min_col

    numbered = sorted(placed, key=lambda p: (p["row"], p["col"]))
    number = 0
    starts = {}

    for item in numbered:
        key = (item["row"], item["col"])
        if key not in starts:
            number += 1
            starts[key] = number
        item["number"] = starts[key]

    across = [
        item for item in numbered if item["direction"] == "across"
    ]
    down = [
        item for item in numbered if item["direction"] == "down"
    ]

    return {
        "grid": grid,
        "entries": numbered,
        "across": across,
        "down": down
    }


def place_word(board, word, row, col, direction):
    for index, letter in enumerate(word):
        position = (
            (row, col + index)
            if direction == "across"
            else (row + index, col)
        )
        board[position] = letter


def can_place(board, word, row, col, direction):
    # Prevent words from touching along their sides.
    if direction == "across":
        if (row, col - 1) in board or (row, col + len(word)) in board:
            return False
    else:
        if (row - 1, col) in board or (row + len(word), col) in board:
            return False

    intersections = 0

    for index, letter in enumerate(word):
        r = row + (index if direction == "down" else 0)
        c = col + (index if direction == "across" else 0)

        existing = board.get((r, c))

        if existing and existing != letter:
            return False

        if existing == letter:
            intersections += 1
            continue

        if direction == "across":
            if (r - 1, c) in board or (r + 1, c) in board:
                return False
        else:
            if (r, c - 1) in board or (r, c + 1) in board:
                return False

    return intersections > 0

