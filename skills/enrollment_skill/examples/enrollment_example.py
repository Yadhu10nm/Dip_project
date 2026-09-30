from skills.enrollment_skill.implementation import EnrollmentSkill


def main():
    enroller = EnrollmentSkill()
    users = enroller.list_users()
    print(f"[EnrollmentSkill] Currently enrolled users: {len(users)}")
    for u in users:
        print(f" - {u.get('name')} (ID: {u.get('id')}, samples: {u.get('sample_count')})")


if __name__ == "__main__":
    main()
