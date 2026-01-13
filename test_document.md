# Server Maintenance Runbook

## Overview
This runbook covers standard server maintenance procedures for our infrastructure.

## Pre-Maintenance Checklist
1. Notify stakeholders 48 hours in advance
2. Schedule maintenance window during low-traffic hours
3. Prepare rollback plan
4. Test monitoring alerts
5. Have on-call engineer available

## Maintenance Steps
1. Place server in maintenance mode
2. Stop application services gracefully
3. Apply security patches
4. Update configuration files
5. Restart services
6. Verify application health
7. Remove maintenance mode

## Post-Maintenance
1. Monitor system for 2 hours
2. Run automated tests
3. Send completion notification
4. Document any issues encountered

## Emergency Contacts
- Primary: infrastructure-team@company.com
- Secondary: devops-lead@company.com
- Management: it-director@company.com

## Rollback Procedures
If maintenance fails:
1. Immediately revert configuration changes
2. Restore from backup if necessary
3. Restart services with previous configuration
4. Notify stakeholders of rollback
5. Schedule follow-up maintenance