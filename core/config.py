import yaml


def load_config():

    with open("configs/settings.yaml") as f:
        return yaml.safe_load(f)
