from privreview import excess, review, unused

ALLOWED = {
    "support": {"read_tickets", "reply"},
    "admin": {"read_tickets", "reply", "db_admin", "manage_users"},
}


def test_excess_finds_extra_privilege():
    acct = {"role": "support", "privileges": ["read_tickets", "reply", "db_admin"]}
    assert excess(acct, ALLOWED) == ["db_admin"]


def test_excess_none_when_within_role():
    acct = {"role": "support", "privileges": ["read_tickets"]}
    assert excess(acct, ALLOWED) == []


def test_excess_admin_can_hold_more():
    acct = {"role": "admin", "privileges": ["db_admin", "manage_users"]}
    assert excess(acct, ALLOWED) == []


def test_excess_unknown_role_everything_is_excess():
    acct = {"role": "ghost", "privileges": ["read_tickets"]}
    assert excess(acct, ALLOWED) == ["read_tickets"]


def test_review_reports_only_offenders():
    accounts = {
        "alice": {"role": "support", "privileges": ["read_tickets", "reply", "db_admin"]},
        "bob": {"role": "admin", "privileges": ["read_tickets", "reply"]},
        "carol": {"role": "support", "privileges": ["read_tickets"]},
    }
    out = review(accounts, ALLOWED)
    assert out == {"alice": ["db_admin"]}


def test_review_empty_when_all_clean():
    accounts = {"bob": {"role": "support", "privileges": ["reply"]}}
    assert review(accounts, ALLOWED) == {}


def test_unused_finds_dormant_grants():
    acct = {"role": "admin", "privileges": ["read_tickets", "reply", "db_admin"]}
    assert unused(acct, {"read_tickets"}) == ["db_admin", "reply"]


def test_unused_none_when_all_used():
    acct = {"role": "support", "privileges": ["read_tickets", "reply"]}
    assert unused(acct, {"read_tickets", "reply"}) == []
