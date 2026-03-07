# 🛡️ Security Playbook - Veryfyn Tracking System

**Purpose**: Define security protocols, audit requirements, and data protection measures for the Veryfyn Tracking System.

---

## 🎯 Security Principles

1. **Data Integrity First**: All user data must be validated before storage
2. **Audit Everything**: Every state change must be logged
3. **Least Privilege**: Users only access their own data
4. **Defense in Depth**: Multiple layers of validation

---

## 🔐 Authentication & Authorization

### POLICY_001: Authentication Required
- All operations require valid user authentication
- Session tokens must be validated on every request
- No anonymous access to data endpoints

### POLICY_002: Role-Based Access Control
| Role | Permissions |
|------|-------------|
| User | Read/write own data only |
| Admin | System configuration, data export |

---

## 📊 Audit Trail Requirements

### BRAIN_002: Always Log to Audit
Every operation must create an audit record including:
- **Timestamp**: UTC timestamp of the operation
- **User ID**: Who performed the action
- **Action Type**: CREATE, READ, UPDATE, DELETE
- **Entity Type**: habit, task, goal, finance, etc.
- **Entity ID**: Unique identifier of affected entity
- **Previous State**: Snapshot before change (for UPDATE/DELETE)
- **New State**: Snapshot after change (for CREATE/UPDATE)
- **IP Address**: Source of the request
- **Session ID**: Active session identifier

### XP Change Logging (Anti-Cheat)
All XP modifications must include:
```python
{
    "xp_change": int,
    "reason": str,  # "habit_complete", "goal_achieved", "streak_freeze_purchase"
    "previous_xp": int,
    "new_xp": int,
    "timestamp": datetime,
    "verification_hash": str  # SHA256 of previous_xp + xp_change + reason
}
```

**Validation Rules**:
- XP cannot be negative
- Single habit completion cannot grant >50 XP
- Daily XP cap: 500 XP (configurable)
- Streak freeze purchases must deduct exactly the configured cost

---

## 📤 Export Guard Protocol

### Who Can Download CSVs?
| Data Type | Authorized Roles | Approval Required |
|-----------|-----------------|-------------------|
| Personal Habits | User (owner) | No |
| Personal Tasks | User (owner) | No |
| Personal Finances | User (owner) | No |
| Full Database Export | Admin only | Yes (2FA) |
| Analytics Data | User (owner) | No |

### Export Validation Checklist
- [ ] User is authenticated
- [ ] User owns the requested data
- [ ] Export request is rate-limited (max 5 exports/hour)
- [ ] Sensitive fields are masked (passwords, tokens)
- [ ] Export file includes watermark with timestamp
- [ ] Export action is logged to audit trail

---

## 🛡️ Data Protection Measures

### Input Validation (POLICY_003)
All user inputs must be validated:
- **Type Checking**: Ensure integers are integers, strings are strings
- **Range Validation**: Numbers within acceptable bounds
- **Length Limits**: Strings have maximum length
- **Sanitization**: Remove/escape special characters
- **SQL Injection Prevention**: Use parameterized queries only

### Foreign Key Constraints (POLICY_004)
- All relationships enforced at database level
- Cascading deletes logged to audit trail
- Orphaned records prevented by design

---

## ⚠️ Risk Tier Classification

| Tier | Operations | Confirmation Required |
|------|------------|----------------------|
| RISK_001 (TRIVIAL) | Read-only views | No |
| RISK_002 (LOW) | Create habit, log task | No |
| RISK_003 (MEDIUM) | Delete single entry | Yes (toast confirmation) |
| RISK_004 (HIGH) | Bulk delete, financial changes | Yes (modal confirmation) |
| RISK_005 (CRITICAL) | Account deletion, full export | Yes (2FA + password) |

---

## 🔍 Security Monitoring

### Guardrail Checks (GUARD_001-005)
- **Loop Detection**: Prevent infinite retry loops
- **Rate Limiting**: Max 100 requests/minute per user
- **Resource Protection**: Query result limits (max 1000 rows)
- **Error Isolation**: One failed operation doesn't crash the system

### Anomaly Detection
Flag for review:
- XP gains >1000 in single day
- More than 50 habit completions in 1 hour
- Export requests from new IP addresses
- Multiple failed login attempts

---

## 📋 Incident Response

### Data Breach Protocol
1. **Immediate**: Revoke all active sessions
2. **Assessment**: Audit logs for unauthorized access
3. **Notification**: Alert affected users within 24 hours
4. **Remediation**: Patch vulnerability, rotate credentials
5. **Documentation**: Update this playbook with lessons learned

### Data Corruption Recovery
1. **Stop**: Halt all write operations
2. **Backup**: Preserve current state for analysis
3. **Restore**: Load from last known good backup
4. **Verify**: Run integrity checks on restored data
5. **Resume**: Gradually restore normal operations

---

## 🧪 Security Testing Checklist

- [ ] SQL injection attempts blocked
- [ ] XSS attacks prevented
- [ ] CSRF tokens validated
- [ ] Rate limiting functional
- [ ] Audit logs capture all actions
- [ ] Export guards enforce permissions
- [ ] XP anti-cheat validation working
- [ ] Session timeout enforced

---

**Last Updated**: 2026-03-07
**Version**: 1.0.0
**Next Review**: 2026-04-07