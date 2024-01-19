def strtobool(s: str) -> bool:
    s = s.lower()
    if s in ("y", "yes", "t", "true", "on", "1"):
        return True
    if s in ("n", "no", "f", "false", "off", "0"):
        return False
    raise ValueError(f"invalid truth value {s}")
