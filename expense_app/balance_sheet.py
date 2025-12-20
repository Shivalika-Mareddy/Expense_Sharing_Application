class BalanceSheet:
    def __init__(self):
        # key: (debtor_id, creditor_id), value: amount owed
        self.net = {}

    def add_expense(self, expense):
        for s in expense.splits:
            if s.user.user_id == expense.paid_by.user_id:
                continue
            key = (s.user.user_id, expense.paid_by.user_id)
            self.net.setdefault(key, 0)
            self.net[key] += s.amount

    def show_user_balance(self, user, members):
        output = []
        for (debtor_id, creditor_id), amt in self.net.items():
            if debtor_id == user.user_id and amt > 0:
                creditor = next(m for m in members if m.user_id == creditor_id)
                output.append(f"You owe {creditor.name} ₹{int(amt)}")
            elif creditor_id == user.user_id and amt > 0:
                debtor = next(m for m in members if m.user_id == debtor_id)
                output.append(f"{debtor.name} owes you ₹{int(amt)}")
        if not output:
            output.append("No dues")
        return output
