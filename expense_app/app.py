# app.py

from flask import Flask, render_template, request, redirect, url_for
from user import User
from split import Split
from expense import Expense, SplitType
from group import Group
from supabase_client import supabase

app = Flask(__name__)

users = {}
group = None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uid = request.form["user_id"]
        users[uid] = User(
            uid,
            request.form["name"],
            request.form["email"]
        )
        return redirect(url_for("index"))
    return render_template("index.html", users=users.values())


@app.route("/create-group", methods=["GET", "POST"])
def create_group():
    global group
    if request.method == "POST":
        group = Group(
            request.form["group_id"],
            request.form["group_name"]
        )
        creator = users[request.form["creator"]]
        group.add_member(creator)

        for uid in request.form.getlist("members"):
            group.add_member(users[uid])

        return redirect(url_for("add_expense"))

    return render_template("create_group.html", users=users.values())


@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if not group:
        return redirect(url_for("index"))

    if request.method == "POST":
        eid = request.form["expense_id"]
        desc = request.form["description"]
        amount = float(request.form["amount"])
        paid_by = users[request.form["paid_by"]]
        split_type = SplitType[request.form["split_type"]]

        splits = []
        if split_type == SplitType.EQUAL:
            splits = [Split(m, 0) for m in group.members]
        else:
            for m in group.members:
                splits.append(Split(m, float(request.form[m.user_id])))

        # Create Expense object
        expense = Expense(eid, desc, amount, paid_by, split_type, splits)
        group.add_expense(expense)

        # ---------------- Logging table ----------------
        rows = []
        for s in expense.splits:
            rows.append({
                "group_id": group.group_id,
                "group_name": group.name,
                "expense_id": eid,
                "description": desc,
                "total_amount": int(amount),
                "paid_by_user_id": paid_by.user_id,
                "paid_by_name": paid_by.name,
                "user_id": s.user.user_id,
                "user_name": s.user.name,
                "user_email": s.user.email,
                "amount_owed": int(s.amount),
                "split_type": split_type.value
            })
        supabase.table("expense_alerts").insert(rows).execute()

        # ---------------- New table: expense_settlements ----------------
        settlements = []
        for s in expense.splits:
            if s.user.user_id == paid_by.user_id:
                continue  # skip payer
            sentence = f"{s.user.name} owes {paid_by.name} ₹{int(s.amount)}"
            settlements.append({
                "user_name": s.user.name,
                "user_email": s.user.email,
                "sentence": sentence
            })
        if settlements:
            supabase.table("expense_settlements").insert(settlements).execute()

        return redirect(url_for("balances"))

    return render_template("add_expense.html", members=group.members)


@app.route("/balances")
def balances():
    if not group:
        return redirect(url_for("index"))

    sheet = group.balance_sheet
    members = group.members
    return render_template("balances.html",
                           members=members,
                           sheet=sheet)


if __name__ == "__main__":
    app.run(debug=True)
