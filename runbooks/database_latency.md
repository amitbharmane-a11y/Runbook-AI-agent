---
title: Database Latency High
version: 1.0
service_owner: Platform / DB Ops
severity: High
trigger_criteria: p95 query latency > 500ms for 10m OR DB CPU > 85% for 10m
---

# Database Latency High

## Diagnosis
1. Confirm the alert scope and impact (which service, which region).
2. Check DB health:

```bash
# Example commands (replace with your tooling)
echo "Check CPU, memory, IOPS, connections, slow queries"
```

3. Identify top offenders:

```bash
echo "Inspect slow query log / top queries"
```

## Remediation
1. Mitigate quickly (least risky first):
   - Add read replicas (if supported) or scale up instance size.
   - Increase connection pool limits carefully (avoid overload).
2. Reduce load:

```bash
echo "Enable caching / rate limit heavy callers / pause batch jobs"
```

3. Validate improvement:

```bash
echo "Re-check p95 latency, error rate, and DB resource metrics"
```

## Rollback
1. If scaling changes caused instability, revert to previous instance size/class.
2. If config changes were applied, restore previous values from version control / backups.

```bash
echo "Rollback steps depend on your DB platform; ensure backups exist before major changes"
```

## Safety
Warning: avoid destructive operations (e.g., deleting data, dropping tables) during incident response without explicit approval.

