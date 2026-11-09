import pytest

from awslab import lab


@pytest.fixture(scope="module")
def acct():
    with lab("setup.sh") as a:
        yield a


def db(acct, name="app-db"):
    rds = acct.client("rds")
    try:
        return rds.describe_db_instances(DBInstanceIdentifier=name)["DBInstances"][0]
    except rds.exceptions.ClientError:
        pytest.fail(f"there is no DB instance called {name}")


def group(acct, name):
    found = acct.client("ec2").describe_security_groups(Filters=[{"Name": "group-name", "Values": [name]}])["SecurityGroups"]
    assert found, f"there is no security group called {name}"
    return found[0]


def test_the_script_runs_without_errors(acct):
    assert acct.ok, acct.failure()


def test_db_group_allows_postgres_from_app_only(acct):
    app, dbsg = group(acct, "app"), group(acct, "db")
    got = {(p.get("FromPort"), g["GroupId"]) for p in dbsg["IpPermissions"] for g in p.get("UserIdGroupPairs", [])}
    cidrs = [r["CidrIp"] for p in dbsg["IpPermissions"] for r in p.get("IpRanges", [])]
    assert got == {(5432, app["GroupId"])} and not cidrs, "db should allow exactly 5432 from the app group, and no address ranges"


def test_in_the_private_subnets(acct):
    d = db(acct)
    sg = d.get("DBSubnetGroup") or {}
    assert sg.get("DBSubnetGroupName") == "app-db", "app-db should use the subnet group app-db"
    ids = [s["SubnetIdentifier"] for s in sg.get("Subnets", [])]
    names = acct.by_name(acct.client("ec2").describe_subnets(SubnetIds=ids)["Subnets"]) if ids else {}
    assert set(names) == {"private-a", "private-b"}, f"the subnet group should be private-a and private-b; it is {sorted(names)}"
    assert not d.get("PubliclyAccessible"), "app-db is publicly accessible"
    assert [g["VpcSecurityGroupId"] for g in d.get("VpcSecurityGroups", [])] == [group(acct, "db")["GroupId"]], "app-db should use the db security group"


def test_engine_and_size(acct):
    d = db(acct)
    assert d["Engine"] == "postgres", f"app-db runs {d['Engine']}, not postgres"
    assert d["DBInstanceClass"] == "db.t3.micro", f"app-db is a {d['DBInstanceClass']}"
    assert d["AllocatedStorage"] == 20 and d.get("StorageType") == "gp3", "app-db should have 20 GiB of gp3"


def test_resilience_settings(acct):
    d = db(acct)
    assert d.get("MultiAZ"), "app-db is not Multi-AZ"
    assert d.get("StorageEncrypted"), "app-db's storage is not encrypted (and that can only be set at creation)"
    assert d.get("BackupRetentionPeriod") == 7, f"backups are kept {d.get('BackupRetentionPeriod')} days, not 7"
    assert d.get("DeletionProtection"), "deletion protection is off"


def test_password_is_managed_by_secrets_manager(acct):
    secret = (db(acct).get("MasterUserSecret") or {}).get("SecretArn")
    assert secret and ":secretsmanager:" in secret, "the master password is not managed in Secrets Manager (--manage-master-user-password)"


def test_read_replica(acct):
    r = db(acct, "app-db-reports")
    assert r.get("ReadReplicaSourceDBInstanceIdentifier") in ("app-db", db(acct)["DBInstanceArn"]), "app-db-reports is not a read replica of app-db"
