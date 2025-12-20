from user import User
from split import Split
from expense import Expense, SplitType
from group import Group

# ---- USERS ----
users = {}
n = int(input("How many users? "))
for _ in range(n):
    uid = input("User ID: ")
    name = input("User Name: ")
    users[uid] = User(uid, name)

# ---- GROUP ----
gid = input("Group ID: ")
gname = input("Group Name: ")
creator_id = input("Creator User ID: ")

group = Group(gid, gname)
group.add_member(users[creator_id])

print("\nAdd members to the group:")
for uid, user in users.items():
    if uid != creator_id:
        choice = input(f"Add {user.name}? (y/n): ")
        if choice.lower() == "y":
            group.add_member(user)

# ---- EXPENSES ----
e_count = int(input("\nHow many expenses? "))
for _ in range(e_count):
    eid = input("Expense ID: ")
    desc = input("Description: ")
    amount = float(input("Total Amount: "))
    split_type = SplitType[input("Split Type (EQUAL/EXACT/PERCENT): ")]
    paid_by = users[input("Paid by (User ID): ")]

    splits = []
    print("Enter split details:")
    for user in group.members:
        if split_type == SplitType.EQUAL:
            splits.append(Split(user, 0))
        else:
            val = float(input(f"{user.name}'s share: "))
            splits.append(Split(user, val))

    expense = Expense(eid, amount, paid_by, splits, split_type)
    group.add_expense(expense)

# ---- BALANCES ----
print("\n---------------------------------------")
for user in group.members:
    print(f"\nBalance sheet of user : {user.user_id}")
    result = group.balance_sheet.show_user_balance(user)
    if not result:
        print("No dues")
    else:
        for line in result:
            print(line)
