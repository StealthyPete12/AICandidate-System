import re
from skill_registry import SKILL_REGISTRY, flatten_role_skills


def extract_skills_from_text(text: str) -> list[str]:
    """Match CV text against the skill registry and return found skills."""
    text = text.lower()
    all_skills = flatten_role_skills()

    found_skills = set()

    for skill in all_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text):
            found_skills.add(skill)

    return sorted(found_skills)
