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

**Amazon RDS** runs a relational database engine - PostgreSQL, MySQL,
MariaDB, Oracle, SQL Server, Db2 - and does the chores: provisioning,
patching, backups, failover. You still choose and own the settings, and the
defaults are not all the ones you want.

## The settings that matter

| Setting | Why |
|---|---|
| **Private subnets** via a **DB subnet group**, **not publicly accessible** | the database is reached by the app, never by the internet |
| A **security group** allowing the port only from the app's group | same chaining as the web tier |
| **Multi-AZ** | a synchronous standby in another AZ; automatic failover in a minute or two |
| **Storage encryption** | KMS at rest, including backups, snapshots and replicas - and it can only be chosen at creation |
| **Backup retention** 1-35 days | automated backups and point-in-time restore to any second in the window |
| **Deletion protection** | a delete call fails until someone turns it off |
| **Managed master password** | RDS generates it, stores it in Secrets Manager and can rotate it |

## Multi-AZ versus read replicas

They solve different problems, and the exam checks you know which:

- **Multi-AZ** is for **availability**. The standby (of a Multi-AZ DB
  instance) takes no traffic; it exists to take over.
- A **read replica** is for **read scaling**. Replication is asynchronous,
  so it can lag; it can be in another Region; it can be promoted to a
  standalone database by hand.

## Your task

On top of the foundations VPC, with security group **app** (done for you):

1. a security group **`db`** allowing **5432 only from `app`**;
2. a DB subnet group **`app-db`** of the two **private** subnets;
3. a PostgreSQL instance **`app-db`**: db.t3.micro, 20 GiB gp3, **Multi-AZ**,
   **encrypted**, **7 days** of backups, **deletion protection**, **not
   publicly accessible**, in `app-db` with the `db` group, master user `app`
   with the password **managed in Secrets Manager**;
4. a read replica **`app-db-reports`**.
