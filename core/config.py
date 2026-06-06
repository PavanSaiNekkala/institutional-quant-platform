import yaml

def load_config():

    with open(
        "configs/settings.yaml",
        "r"
    ) as f:
        return yaml.safe_load(f)
