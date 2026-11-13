---
title: RDS done right
summary: A PostgreSQL database in private subnets - Multi-AZ, encrypted, backed up, protected from deletion, its password kept by Secrets Manager - plus a read replica for the reports.
order: 1
files: [setup.sh]
run: awslab run setup.sh
hints:
  - "A DB subnet group names the subnets the database may use: `aws rds create-db-subnet-group --db-subnet-group-name app-db --db-subnet-group-description \"app database\" --subnet-ids \"$PRIVATE_A\" \"$PRIVATE_B\"`."
  - "`aws rds create-db-instance --db-instance-identifier app-db --engine postgres --db-instance-class db.t3.micro --allocated-storage 20 --storage-type gp3 --master-username app --manage-master-user-password --multi-az --storage-encrypted --backup-retention-period 7 --deletion-protection --no-publicly-accessible --db-subnet-group-name app-db --vpc-security-group-ids \"$DB_SG\"`."
  - "`--manage-master-user-password` asks RDS to generate the password and keep it in Secrets Manager. Never pass `--master-user-password` with a literal in a script."
  - "`aws rds create-db-instance-read-replica --db-instance-identifier app-db-reports --source-db-instance-identifier app-db --db-instance-class db.t3.micro`."
---

Running a database yourself on a server means installing it, patching it,
taking backups, testing that the backups restore, and being woken up when
the disk fills or the server dies. **Amazon RDS** (Relational Database
Service) runs a relational database engine for you (PostgreSQL, MySQL,
MariaDB, Oracle, SQL Server or Db2) and does those chores: it provisions the
server, patches it, backs it up, and fails over to a standby.

What it does **not** do is choose your settings. You still own them, and
several of the defaults are not the ones you want in production. Some, like
encryption, can only be chosen when the database is created. This lesson
creates one database with every setting that matters, and a copy of it for
the reporting team.

```text
 app (security group app) ──5432──> [ db ] app-db primary, private-a ──sync──> standby, private-b
                                                    │                            (Multi-AZ, takes no traffic)
                                                    └──async──> app-db-reports (read replica, for reports)
 password: kept in Secrets Manager by RDS      storage: encrypted      backups: 7 days
```

## The settings that matter

| Setting | Why |
|---|---|
| **Private subnets**, through a **DB subnet group**, and **not publicly accessible** | the database is reached by the app, never by the internet |
| A **security group** allowing the port **only from the app's group** | the same chaining as the web tier (Foundations lesson 8) |
| **Multi-AZ** | a synchronous standby copy in another AZ, and automatic failover to it in a minute or two |
| **Storage encryption** | KMS encryption at rest, covering backups, snapshots and replicas too. It can **only** be chosen at creation: an unencrypted database stays unencrypted |
| **Backup retention**, 1 to 35 days | automated daily backups, plus **point-in-time restore** to any second within the window |
| **Deletion protection** | a delete call fails until someone deliberately turns it off |
| **Managed master password** | RDS generates the password, stores it in Secrets Manager, and can rotate it; it never appears in a script |

A **DB subnet group** is a named list of subnets the database may be placed
in; it must cover at least two AZs, so that Multi-AZ has somewhere to put the
standby. The database's own subnet is chosen from it.

The **master user** is the database's administrator account. Passing a
password with `--master-user-password` would put it in the script, in your
shell history, and in anything that logs commands. `--manage-master-user-password`
asks RDS to generate one and keep it in **Secrets Manager** (section 7)
instead, where the application reads it at run time:

```
$ aws rds describe-db-instances --db-instance-identifier app-db \
    --query 'DBInstances[0].[DBInstanceStatus,MultiAZ,StorageEncrypted,MasterUserSecret.SecretArn,Endpoint.Address]'
[
    "available",
    true,
    true,
    "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds!db-8fae5d48-...-XLywks",
    "app-db.aaaaaaaaaa.us-east-1.rds.amazonaws.com"
]
```

The **endpoint** is the database's DNS name, which the app connects to. On
failover, RDS points the same name at the standby, so the app reconnects to
the same address and needs no change.

Deletion protection is on by default only for databases created in the
console; from the CLI you must ask for it (`--deletion-protection`). Once
on, it refuses:

```
An error occurred (InvalidParameterCombination) when calling the DeleteDBInstance operation: Cannot delete protected DB Instance, please disable deletion protection and try again.
```

## Multi-AZ versus read replicas

Both make a second copy of the database. They solve **different** problems,
and the exam checks that you know which is which:

| | Multi-AZ standby | Read replica |
|---|---|---|
| Purpose | **availability**: survive the failure of an AZ or the server | **read scaling**: move reads off the primary |
| Takes traffic? | **no**; it exists only to take over | **yes**, reads only |
| Replication | **synchronous**: a write is on both before it is confirmed | **asynchronous**: can lag behind, so reads may be slightly stale |
| Failover | **automatic**, same endpoint | none by itself; can be **promoted** to a standalone database by hand |
| Location | another AZ in the same Region | the same AZ, another AZ, or another Region |

Two more facts the exam likes: deleting a source database **promotes** its
replicas in the same Region to standalone databases, which stop
replicating; and since encryption is fixed at creation, encrypting an
existing database means copying a snapshot with encryption on and restoring
a new database from it.

So "the reports slow down the application" is a read replica, and "the
database must survive an AZ failure" is Multi-AZ. Many production databases
have both.

(There is also a newer *Multi-AZ DB cluster* option, with two **readable**
standbys; this lesson uses the classic Multi-AZ DB instance.)

❗ **Where this sandbox differs from real AWS.** Real RDS does not allow
creating a read replica of a database whose master password is managed by
Secrets Manager, for every engine except SQL Server and Db2 (RDS User
Guide, "Limitations for Secrets Manager integration"). The emulator allows
it, and this lesson's task combines both to practise both settings. In a
real account you would choose: a managed password and no replica, or a
replica and a password you store and rotate in Secrets Manager yourself.

## More RDS facts

| | RDS | A database you run on EC2 |
|---|---|---|
| Setup, OS patching, engine upgrades | AWS | you |
| Backups and point-in-time restore | built in | you build them |
| Multi-AZ and read replicas | a setting | you build them |
| Shell access to the server | **no** (RDS Custom, for Oracle and SQL Server, allows it) | yes |

- **Backups**: automated backups are kept 1 to 35 days and allow
  point-in-time restore (to within about five minutes); **manual snapshots**
  are kept until you delete them. Any restore creates a **new** database,
  with a new endpoint.
- **Storage auto scaling** grows the disk when it runs low, up to a maximum
  you set; storage never shrinks.
- Up to **15 read replicas**; replication to a replica in the same Region is
  free, to another Region is billed. Turning Multi-AZ on for an existing
  database needs no downtime.
- A **stopped** database is still billed for its storage, and starts again
  by itself after seven days.
- Applications can sign in with **IAM database authentication** instead of a
  password. **RDS Proxy** pools connections, the usual fix when many Lambda
  functions open too many at once.
- **Aurora** is AWS's own MySQL- and PostgreSQL-compatible engine, with
  storage that keeps six copies across three AZs; it has a lesson of its
  own in the exam topics.

## Your task

On top of the Foundations VPC, with a security group **app** for the
application (done for you, in `APP_SG`):

1. a security group **`db`** whose only inbound rule is TCP **5432**
   (PostgreSQL) **from the `app` group**, with no address ranges;
2. a DB subnet group **`app-db`** made of the two **private** subnets;
3. a PostgreSQL instance **`app-db`** with:
   - instance class **db.t3.micro**, **20 GiB** of **gp3** storage;
   - **Multi-AZ**, **encrypted** storage, **7 days** of backups, **deletion
     protection**;
   - **not publicly accessible**, in the `app-db` subnet group, with the
     `db` security group and no other;
   - master user **`app`**, with the password **managed in Secrets
     Manager**;
4. a read replica **`app-db-reports`** of it, also db.t3.micro.

After **Run**, the `describe-db-instances` query above shows the settings,
and `aws rds describe-db-instances --db-instance-identifier app-db-reports
--query 'DBInstances[0].ReadReplicaSourceDBInstanceIdentifier'` names the
source. In the emulator both are `available` at once; real RDS takes 10 to
20 minutes to create each. 💸 A real Multi-AZ database is billed for both
copies, every hour, so it costs about twice a single-AZ one.

## Check yourself

1. The reporting team's queries slow the application down. Multi-AZ or a
   read replica?
   *A read replica: Multi-AZ's standby takes no traffic.*
2. The database must survive an AZ failure. Which?
   *Multi-AZ.*
3. A database was created unencrypted. How do you encrypt it?
   *Copy a snapshot with encryption on, and restore a new database from
   it.*
4. Why `--manage-master-user-password` instead of `--master-user-password`?
   *The password never appears in the script, the shell history or logs.*
