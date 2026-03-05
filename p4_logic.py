# -------- Mini logic engine (tiny Prolog-ish) --------

class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Var({self.name})"

def is_var(x):
    return isinstance(x, Var)

def walk(x, subst):
    # follow bindings until fixed point
    while is_var(x) and x in subst:
        x = subst[x]
    return x

def unify(a, b, subst):
    a = walk(a, subst)
    b = walk(b, subst)

    if a == b:
        return subst

    if is_var(a):
        new = dict(subst)
        new[a] = b
        return new

    if is_var(b):
        new = dict(subst)
        new[b] = a
        return new

    # unify tuples (structures)
    if isinstance(a, tuple) and isinstance(b, tuple) and len(a) == len(b):
        s = subst
        for ai, bi in zip(a, b):
            s = unify(ai, bi, s)
            if s is None:
                return None
        return s

    return None

def run_query(goal, subst=None):
    if subst is None:
        subst = {}
    yield from goal(subst)

def fact(db, pred, *args):
    # returns a goal (a function subst -> generator[substs])
    def goal(subst):
        for row in db.get(pred, []):
            s2 = unify(args, row, subst)
            if s2 is not None:
                yield s2
    return goal

def conj(g1, g2):
    def goal(subst):
        for s1 in run_query(g1, subst):
            yield from run_query(g2, s1)
    return goal

def disj(g1, g2):
    def goal(subst):
        yield from run_query(g1, subst)
        yield from run_query(g2, subst)
    return goal


# -------- Domain facts: books + loans --------

DB = {
    "book": [
        ("b1", "Dune", 3),
        ("b2", "1984", 1),
        ("b3", "Sapiens", 2),
    ],
    "loan": [
        ("b1", "u1"),
        ("b1", "u2"),
        ("b2", "u1"),
    ]
}

# -------- Domain "rules" in Python --------

def all_loans_for_book(book_id):
    U = Var("U")
    results = []
    for s in run_query(fact(DB, "loan", book_id, U)):
        results.append(walk(U, s))
    return results

def available_copies(book_id):
    Title = Var("Title")
    Total = Var("Total")
    sols = list(run_query(fact(DB, "book", book_id, Title, Total)))
    if not sols:
        return 0
    total = walk(Total, sols[0])
    return total - len(all_loans_for_book(book_id))

def can_checkout(book_id):
    return available_copies(book_id) > 0

def checkout(book_id, user_id):
    # "assert" a new fact (loan) if allowed
    if can_checkout(book_id):
        DB["loan"].append((book_id, user_id))
        return True
    return False

def return_book(book_id, user_id):
    # retract one matching fact if present
    try:
        DB["loan"].remove((book_id, user_id))
        return True
    except ValueError:
        return False

def overdue_users(days_map, threshold):
    # This part isn't naturally logic-y, but we can treat it as a derived query
    return [uid for uid, days in days_map.items() if days >= threshold]


# -------- Example "queries" --------

if __name__ == "__main__":
    # Query like: ?- loan(b1, U).
    U = Var("U")
    print("Query: loan(b1, U)")
    for s in run_query(fact(DB, "loan", "b1", U)):
        print("  U =", walk(U, s))

    print("available_copies(b1) =", available_copies("b1"))  # 3 - 2 = 1

    print("checkout(b1, u3) =", checkout("b1", "u3"))        # True
    print("checkout(b2, u2) =", checkout("b2", "u2"))        # False (no copies)

    print("return_book(b1, u2) =", return_book("b1", "u2"))  # True
    print("available_copies(b1) =", available_copies("b1"))  # should increase

    days = {"u1": 5, "u2": 1, "u3": 7}
    print("overdue_users(days, 5) =", overdue_users(days, 5))  # ['u1', 'u3']