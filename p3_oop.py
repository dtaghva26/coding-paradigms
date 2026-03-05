class IdGen:
    bid = 0
    uid = 0

    @classmethod
    def generate_bid(cls):
        cls.bid += 1
        return cls.bid

    @classmethod
    def generate_uid(cls):
        cls.uid += 1
        return cls.uid


class Book:
    def __init__(self, title, total_copies):
        self.bid = f"b{IdGen.generate_bid()}"     # make IDs like b1, b2...
        self.title = title
        self.total_copies = total_copies


class User:
    def __init__(self, name=""):
        self.user_id = f"u{IdGen.generate_uid()}"  # make IDs like u1, u2...
        self.name = name


class Loan:
    def __init__(self, user_id, book_id):
        self.user_id = user_id
        self.book_id = book_id


class Library:
    def __init__(self):
        self.books = []   # list[Book]
        self.loans = []   # list[Loan]
        self.users = []   # list[User]
        self.overdue_map = {"u1": 5, "u2": 1, "u3": 7}  # demo data

    # ----- OOP methods -----

    def add_book(self, title, total_copies):
        b = Book(title, total_copies)
        self.books.append(b)
        return b

    def add_user(self, name=""):
        u = User(name)
        self.users.append(u)
        return u

    def _get_book(self, book_id):
        for b in self.books:
            if b.bid == book_id:
                return b
        return None

    def loan_count(self, book_id):
        return sum(1 for ln in self.loans if ln.book_id == book_id)

    def available_copies(self, book_id):
        book = self._get_book(book_id)
        if book is None:
            return 0
        return book.total_copies - self.loan_count(book_id)

    def show_avail_copies(self):
        for b in self.books:
            print(b.bid, b.title, "available:", self.available_copies(b.bid))

    def checkout(self, book_id, user_id):
        if self.available_copies(book_id) > 0:
            self.loans.append(Loan(user_id, book_id))
            return {"msg": "loan created"}
        return {"msg": "error! book unavailable"}

    def return_book(self, book_id, user_id):
        for i, ln in enumerate(self.loans):
            if ln.book_id == book_id and ln.user_id == user_id:
                self.loans.pop(i)
                return {"msg": "loan removed"}
        return {"msg": "loan doesnt exist"}

    def overdue_users(self, threshold):
        return [uid for uid, days in self.overdue_map.items() if days >= threshold]

    # ----- CLI -----

    def run(self):
        while True:
            inp = input("> ").strip()
            if not inp:
                continue

            parts = inp.split()
            command = parts[0]

            if command == "show_avail_copies":
                self.show_avail_copies()

            elif command == "checkout":
                # usage: checkout b1 u3
                print(self.checkout(parts[1], parts[2]))

            elif command == "return":
                # usage: return b1 u2
                print(self.return_book(parts[1], parts[2]))

            elif command == "overdue":
                # usage: overdue 5
                threshold = int(parts[1]) if len(parts) > 1 else 5
                print(self.overdue_users(threshold))

            elif command in ("exit", "quit"):
                break

            else:
                print("Commands: show_avail_copies | checkout <book_id> <user_id> | return <book_id> <user_id> | overdue <threshold> | exit")


if __name__ == "__main__":
    lib = Library()

    # seed books to match your earlier dataset
    b1 = lib.add_book("Dune", 3)     # b1
    b2 = lib.add_book("1984", 1)     # b2
    b3 = lib.add_book("Sapiens", 2)  # b3

    # seed loans to match earlier dataset (b1 u1, b1 u2, b2 u1)
    lib.loans.append(Loan("u1", b1.bid))
    lib.loans.append(Loan("u2", b1.bid))
    lib.loans.append(Loan("u1", b2.bid))

    lib.run()