import os


def get_bool(env_name: str, default: bool = False) -> bool:
    raw = os.getenv(env_name, str(default)).lower()
    if raw in ['true', '1']:
        return True
    if raw in ['false', '0']:
        return False



def must_get(env_name: str) -> str:
    raw = os.getenv(env_name)
    if raw is None:
        raise Exception(f"Environment variable {env_name} must be set")
    return raw
