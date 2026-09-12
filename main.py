from clients import list_clients
from projects import list_projects
from workers import list_workers
from wage_entries import list_wage_entries
from expenses import list_expenses
from income import list_income
from taxes import list_taxes

if __name__ == "__main__":
    print("Πελάτες:")
    for row in list_clients():
        print(row)

    print("\nΈργα:")
    for row in list_projects():
        print(row)

    print("\nΠροσωπικό:")
    for row in list_workers():
        print(row)

    print("\nΗμερομίσθια:")
    for row in list_wage_entries():
        print(row)

    print("\nΈξοδα:")
    for row in list_expenses():
        print(row)

    print("\nΈσοδα:")
    for row in list_income():
        print(row)

    print("\nΦορολογίες:")
    for row in list_taxes():
        print(row)
