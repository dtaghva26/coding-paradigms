from typing import Tuple, Dict

Book = Tuple[str, str, int]   # (id, title, total_copies)
Loan = Tuple[str, str]        # (book_id, user_id)

Books = Tuple[Book, ...]
Loans = Tuple[Loan, ...]

BOOKS: Books = (
    ("b1", "Dune", 3),
    ("b2", "1984", 1),
    ("b3", "Sapiens", 2),
)

LOANS: Loans = (
    ("b1", "u1"),
    ("b1", "u2"),
    ("b2", "u1"),
)


# ---------- Pure functions ----------

def total_copies(book_id: str, books: Books) -> int:
    return next((total for bid, _, total in books if bid == book_id), 0)


def loan_count(book_id: str, loans: Loans) -> int:
    return sum(1 for bid, _ in loans if bid == book_id)


def available_copies(book_id: str, books: Books, loans: Loans) -> int:
    return total_copies(book_id, books) - loan_count(book_id, loans)


def checkout(book_id: str, user_id: str, books: Books, loans: Loans):
    if available_copies(book_id, books, loans) > 0:
        new_loans = loans + ((book_id, user_id),)
        return new_loans, {"msg": "loan created"}
    return loans, {"msg": "error! book unavailable"}


def return_book(book_id: str, user_id: str, loans: Loans):
    if (book_id, user_id) in loans:
        new_loans = tuple(
            (bid, uid) for (bid, uid) in loans
            if not (bid == book_id and uid == user_id)
        )
        return new_loans, {"msg": "loan removed"}

    return loans, {"msg": "loan doesnt exist"}


def overdue_users(days_map: Dict[str, int], threshold: int):
    return tuple(uid for uid, days in days_map.items() if days >= threshold)


def show_avail_copies(books: Books, loans: Loans):
    return tuple(
        f"{bid} {title} available: {available_copies(bid, books, loans)}"
        for (bid, title, _) in books
    )


# ---------- State transition ----------

def step(state, raw_input, overdue_map):
    books, loans = state
    raw_input = raw_input.strip()

    if not raw_input:
        return state, (), False

    parts = raw_input.split()
    cmd = parts[0]

    if cmd in ("exit", "quit"):
        return state, ("bye!",), True

    if cmd == "show_avail_copies":
        return (books, loans), show_avail_copies(books, loans), False

    if cmd == "checkout":
        book_id, user_id = parts[1], parts[2]
        new_loans, msg = checkout(book_id, user_id, books, loans)
        return (books, new_loans), (str(msg),), False

    if cmd == "return":
        book_id, user_id = parts[1], parts[2]
        new_loans, msg = return_book(book_id, user_id, loans)
        return (books, new_loans), (str(msg),), False

    if cmd == "overdue":
        threshold = int(parts[1]) if len(parts) > 1 else 5
        return (books, loans), (str(overdue_users(overdue_map, threshold)),), False

    help_line = "Commands: show_avail_copies | checkout <book_id> <user_id> | return <book_id> <user_id> | overdue <threshold> | exit"
    return (books, loans), (help_line,), False


# ---------- Recursive REPL ----------

def repl(state, overdue_map):
    raw = input("> ")
    new_state, outputs, should_exit = step(state, raw, overdue_map)

    for line in outputs:
        print(line)

    if not should_exit:
        repl(new_state, overdue_map)


if __name__ == "__main__":
    initial_state = (BOOKS, LOANS)
    overdue_map = {"u1": 5, "u2": 1, "u3": 7}
    repl(initial_state, overdue_map)