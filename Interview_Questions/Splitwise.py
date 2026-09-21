"""
================================================================================
LLD: Splitwise
================================================================================

What is Splitwise?

1. we create a group of users.
2. record each expenses done by the person- who paid, amount, all the users.
3. system calculates how much each person owes.
4. keeps track of balances and debts so that users dont have to manually calculates them.

Clarifying Questions:

1. Are we only tracking expenses/debts, or also processing payments?
→ For this design: expense/debt tracking only.

1. Functional Requirements:

- we should be able to create users and groups.
- Expenses are created within a group, and only group members can participate in the expense.
- System maintains users, groups, expenses, participants, and resulting balances.
- system calcuates the amount based on the record and splits the money.
- Amount can be split - equal split/ percentage split
- Keeps track of balances and expense history.
- Maintain the balances--> balance[A][B] = amount A owes B

2. Non - Functional Requirements:

- Thread safety
- Extensibility - split amount can be further extended like custom split, shares, etc...
- consistency - Expense and balance updates should remain consistent; a partial update should not leave balances incorrect.

3. Identify core entities:

User
    - user_id
    - user_name

Group
    - group_id
    - group_name
    - users = []
    - expenses = []

Expense
    - expense_id
    - users_participated = []
    - split_strategy
    - amount
    - paid_by

    + calculate_share()

Split
    - split_amount
    - paid_for

SplitStrategy
    - EqualSplit()
        + generate_split(expense)
    - PercentageSplit()
        + generate_split(expense)

BalanceManager
    + get_balance()
    + update_balance()

SplitWiseManager
    + create_user(user_id, user_name)
    + create_groups(group_id, group_name, users)
    + add_expenses(expense_id, users, paid_by, amount, split_strategy)
    + show_balance(user)

4. Identify relationships

Expense --belongs to a--> group

EqualSplit --is-a--> SplitStrategy
PercentageSplit --is-a--> SplitStrategy

SplitWiseManager --creates/manages--> user
SplitWiseManager --creates/manages--> group

Expense --has-many--> split (1:M)
Expense --has-many--> participants (1:M)

5. Coding

"""

from abc import ABC, abstractmethod
import threading


class User:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name


class Group:
    def __init__(self, group_id, group_name):
        self.group_id = group_id
        self.group_name = group_name
        self.users = []
        self.expenses = []


class Split:
    def __init__(self, split_amount, paid_for):
        self.split_amount = split_amount
        self.paid_for = paid_for


class SplitStrategy(ABC):
    """
    Strategy Pattern:  Different split rules can be added without changing Expense.
    """
    @abstractmethod
    def generate_split(self, expense):
        pass


class Expense:
    def __init__(self, expense_id, amount, paid_by, split_strategy, users_participated):
        self.expense_id = expense_id
        self.users_participated = users_participated
        self.amount = amount
        self.paid_by = paid_by
        self.split_strategy = split_strategy
        self.splits = []

    def calculate_share(self):
        # Expense delegates split calculation to the selected strategy.
        self.splits = self.split_strategy.generate_split(self)
        return self.splits


class InvalidPercentageError(RuntimeError):
    pass


class EqualSplits(SplitStrategy):
    def generate_split(self, expense):
        # Divide the total expense equally among all participants.

        splits = []

        if not expense.users_participated:
            return splits

        share = expense.amount / len(expense.users_participated)

        for user in expense.users_participated:
            splits.append(Split(share, user))

        return splits


class PercentageSplits(SplitStrategy):
    def __init__(self, percentages):
        self.percentages = percentages

    def generate_split(self, expense):
        # Calculate each participant's share based on their percentage.
        splits = []

        if not expense.users_participated:
            return splits

        if sum(self.percentages.values()) != 100:
            raise InvalidPercentageError("Percentages must sum to 100")

        for user in expense.users_participated:
            percentage = self.percentages.get(user.user_id)

            if percentage is None:
                raise InvalidPercentageError("Invalid percentage")

            share = expense.amount * percentage / 100.0
            splits.append(Split(share, user))

        return splits


# balances[X][Y] = amount X owes Y
# Store only one direction of debt between two users.
# If the opposite debt exists, cancel it first.

class BalanceManager:
    def __init__(self):
        self.balances = {}
        self.lock = threading.Lock()

    def ensure_user(self, user_id):
        self.balances.setdefault(user_id, {})

    def update_balance(self, expense: Expense, splits):
        with self.lock:
            payer_id = expense.paid_by.user_id

            for split in splits:
                debtor_id = split.paid_for.user_id
                amount = split.split_amount

                if payer_id == debtor_id:
                    continue

                self.ensure_user(payer_id)
                self.ensure_user(debtor_id)

                # Check if payer already owes this debtor
                opposite_amount = self.balances[payer_id].get(debtor_id, 0.0)

                if opposite_amount > 0:
                    if opposite_amount > amount:
                        # Reduce existing debt
                        self.balances[payer_id][debtor_id] = opposite_amount - amount
                    elif opposite_amount == amount:
                        # Debt is completely settled
                        self.balances[payer_id].pop(debtor_id, None)
                    else:
                        # Existing debt is cancelled,
                        # remaining amount is owed in the opposite direction
                        remaining = amount - opposite_amount

                        self.balances[payer_id].pop(debtor_id, None)

                        self.balances[debtor_id][payer_id] = (self.balances[debtor_id].get(payer_id, 0.0) + remaining )

                else:
                    # No opposite debt.
                    # Debtor owes payer.
                    self.balances[debtor_id][payer_id] = (self.balances[debtor_id].get(payer_id, 0.0) + amount )

    def get_balance(self, user_id):
        # balances[debtor][creditor] = amount debtor owes creditor
        with self.lock:

            # "owes" -> people this user owes
            # "owed_by" -> people who owe this user
            result = {"owes": {}, "owed_by": {}}

            # user owes these people
            for person_id, amount in self.balances.get(user_id, {}).items():
                result["owes"][person_id] = round(amount, 2)

            # these people owe user
            for debtor_id, creditors in self.balances.items():
                if user_id in creditors:
                    result["owed_by"][debtor_id] = round(creditors[user_id], 2)

            return result


class SplitwiseManager:
    """
    Main entry point of the system. Coordinates users, groups, expenses and balances.
    """
    def __init__(self):
        self.users = {}
        self.groups = {}
        self.balance_manager = BalanceManager()

    def create_user(self, user_id, user_name):
        user = User(user_id, user_name)
        self.users[user_id] = user
        return user

    def create_groups(self, group_id, group_name, users):

        for user in users:
            if user.user_id not in self.users:
                print("Invalid user")
                return

        group = Group(group_id, group_name)

        group.users = users
        self.groups[group_id] = group
        return group

    def add_expense(self, expense_id, paid_by, amount, split_strategy: SplitStrategy, group_id, users_participated):
        if group_id not in self.groups:
            print("Invalid group")
            return

        group = self.groups[group_id]

        if paid_by not in group.users:
            return

        if not users_participated:
            print("Expense must have at least one participant")
            return

        for participant in users_participated:
            if participant not in group.users:
                print(f"{participant}:user not in this group")
                return

        expense = Expense(expense_id, amount, paid_by, split_strategy, users_participated)

        splits = expense.calculate_share()

        self.balance_manager.update_balance(expense, splits)

        group.expenses.append(expense)

        return expense

    def show_balance(self, user: User):
        balance = self.balance_manager.get_balance(user.user_id)

        if balance["owes"]:
            for person_id, amount in balance["owes"].items():
                person = self.users[person_id]
                print(f"{user.user_name} owes {person.user_name}: {amount} ")

        if balance["owed_by"]:
            for person_id, amount in balance["owed_by"].items():
                person =  self.users[person_id]
                print(f"{person.user_name} owes {user.user_name}: {amount}")


def main():
    splitwise = SplitwiseManager()

    sanjana = splitwise.create_user("U1", "Sanjana")
    alice = splitwise.create_user("U2", "Alice")
    bob = splitwise.create_user("U3", "Bob")

    splitwise.create_groups("G1", "Trip Varkala", [sanjana, alice, bob])

    print("Equal split: Sanjana pays 500 for all three")
    splitwise.add_expense("E1", sanjana, 500, EqualSplits(), "G1", [sanjana, alice, bob])

    print("Percentage split: Bob pays 200; Sanjana 30%, Alice 40%, Bob 30%")
    percentages = {"U1": 30.0, "U2": 40.0, "U3": 30.0}
    splitwise.add_expense("E2", bob, 200, PercentageSplits(percentages), "G1", [sanjana, alice, bob])

    for user in [sanjana, alice, bob]:
        print(f"\nBalance for {user.user_name}:")
        splitwise.show_balance(user)


if __name__ == "__main__":
    main()
