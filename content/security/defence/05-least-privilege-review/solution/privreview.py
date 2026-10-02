def excess(account, allowed_by_role):
    # Anything the account holds beyond what its role permits is a grant to
    # question - the support account with db_admin is the classic finding.
    allowed = allowed_by_role.get(account["role"], set())
    return sorted(set(account["privileges"]) - set(allowed))


def review(accounts, allowed_by_role):
    # Only the accounts with something to fix; a clean account is not reported.
    out = {}
    for name, account in accounts.items():
        over = excess(account, allowed_by_role)
        if over:
            out[name] = over
    return out


def unused(account, used):
    # Granted but never exercised: pure risk, no benefit. Revoke it.
    return sorted(set(account["privileges"]) - set(used))


if __name__ == "__main__":
    allowed = {"support": {"read_tickets", "reply"}, "admin": {"read_tickets", "reply", "db_admin"}}
    accounts = {
        "alice": {"role": "support", "privileges": ["read_tickets", "reply", "db_admin"]},
        "bob": {"role": "admin", "privileges": ["read_tickets", "reply"]},
    }
    print("review:", review(accounts, allowed))
