import numpy as np
from skills.vector_database_skill.implementation import VectorDatabaseSkill


def main():
    db = VectorDatabaseSkill()
    print(f"[VectorDatabaseSkill] Collection vector count: {db.count()}")
    people = db.list_people()
    print(f"[VectorDatabaseSkill] Registered people: {people}")


if __name__ == "__main__":
    main()
