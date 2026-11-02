def load_config(path):
    with open(path) as f:
        return json.load(f)

def get_env(name, default=None):
    return os.environ.get(name, default)
