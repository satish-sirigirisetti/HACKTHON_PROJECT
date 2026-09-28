"""Feature-vector construction boundary for future career models."""

from collections.abc import Mapping


def profile_to_features(profile: Mapping[str, object]) -> dict[str, float]:
    """Build a validated numeric feature vector from a normalized profile."""
    skill_levels = profile.get("skill_levels", {})
    if not isinstance(skill_levels, Mapping):
        raise ValueError("skill_levels must be a mapping of skill names to proficiency")
    features: dict[str, float] = {}
    for name, level in skill_levels.items():
        if not isinstance(name, str) or not isinstance(level, (int, float)) or not 0 <= level <= 1:
            raise ValueError("skill levels must have string names and numeric values from 0 to 1")
        features[f"skill:{name.strip().casefold()}"] = float(level)
    return features