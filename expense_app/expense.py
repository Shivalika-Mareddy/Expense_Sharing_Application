from enum import Enum
from split import Split

class SplitType(Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENT = "PERCENT"

class Expense:
    def __init__(self, expense_id, description, amount, paid_by, split_type: SplitType, splits):
        self.expense_id = expense_id
        self.description = description  # store description
        self.amount = amount
        self.paid_by = paid_by
        self.split_type = split_type
        self.splits = []

        if split_type == SplitType.EQUAL:
            self._equal_split(splits)
        elif split_type == SplitType.EXACT:
            self._exact_split(splits)
        elif split_type == SplitType.PERCENT:
            self._percent_split(splits)
        else:
            raise ValueError("Invalid split type")

    def _equal_split(self, splits):
        share = round(self.amount / len(splits), 2)
        for s in splits:
            self.splits.append(Split(s.user, share))

    def _exact_split(self, splits):
        total = sum(s.amount for s in splits)
        if round(total, 2) != round(self.amount, 2):
            raise ValueError("Exact split does not match total amount")
        self.splits = splits

    def _percent_split(self, splits):
        percent_total = sum(s.amount for s in splits)
        if percent_total != 100:
            raise ValueError("Percentage split must sum to 100")
        for s in splits:
            self.splits.append(
                Split(s.user, round((s.amount / 100) * self.amount, 2))
            )
