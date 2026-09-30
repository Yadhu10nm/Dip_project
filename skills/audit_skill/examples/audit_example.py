from skills.audit_skill.implementation import AuditSkill


def main():
    audit = AuditSkill()
    rec = audit.log_event("SYSTEM_STARTUP", person_name="System", similarity=1.0)
    print(f"[AuditSkill] Logged startup event: {rec}")
    logs = audit.get_logs(limit=5)
    print(f"[AuditSkill] Recent 5 entries count: {len(logs)}")


if __name__ == "__main__":
    main()
