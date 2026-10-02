def excess(account, allowed_by_role):
    pass


def review(accounts, allowed_by_role):
    pass


def unused(account, used):
    pass


if __name__ == "__main__":
    allowed = {"support": {"read_tickets", "reply"}, "admin": {"read_tickets", "reply", "db_admin"}}
    accounts = {
        "alice": {"role": "support", "privileges": ["read_tickets", "reply", "db_admin"]},
        "bob": {"role": "admin", "privileges": ["read_tickets", "reply"]},
    }
    print("review:", review(accounts, allowed))
