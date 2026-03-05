# books: (id, title, total_copies)
books = [
    ("b1", "Dune", 3),
    ("b2", "1984", 1),
    ("b3", "Sapiens", 2)
]

# loans: (book_id, user_id)
loans = [
    ("b1", "u1"),
    ("b1", "u2"),
    ("b2", "u1")
]

def total_copies(book_id):
    for bid, title, total in books:
        if bid == book_id:
            return total
    return 0  # not found

def loan_count(book_id):
    count = 0
    for bid, uid in loans:
        if bid == book_id:
            count += 1
    return count

def available_copies(book_id):
    return total_copies(book_id) - loan_count(book_id)

def show_avail_copies():
    for bid, title, total in books:
        print(bid, title, "available:", available_copies(bid))

def create_loan(book_id, user_id):
    if available_copies(book_id) > 0:
        loans.append((book_id, user_id))
        return {"msg": "loan created"}
    return {"msg": "error! book unavailable"}

def return_loan(book_id, user_id):
    if (book_id, user_id) in loans:
        loans.remove((book_id, user_id))
        return {"msg": "loan removed"}
    return {"msg": "loan doesnt exist"}

def show_overdue_users(user_id_to_days_late, threshold):
    overdue = []
    for uid, days in user_id_to_days_late.items():
        if days >= threshold:
            overdue.append(uid)
    return overdue

if __name__ == "__main__":
    overdue_map = {"u1": 5, "u2": 1, "u3": 7}

    while True:
        inp = input("> ").strip()
        if not inp:
            continue

        parts = inp.split()
        command = parts[0]

        if command == "show_avail_copies":
            show_avail_copies()

        elif command == "checkout":
            # usage: checkout b1 u3
            print(create_loan(parts[1], parts[2]))

        elif command == "return":
            # usage: return b1 u2
            print(return_loan(parts[1], parts[2]))

        elif command == "overdue":
            # usage: overdue 5
            threshold = int(parts[1]) if len(parts) > 1 else 5
            print(show_overdue_users(overdue_map, threshold))

        elif command in ("exit", "quit"):
            break

        else:
            print("Commands: show_avail_copies | checkout <book_id> <user_id> | return <book_id> <user_id> | overdue <threshold> | exit")