
def load_env(filename):
    # Load environment variables from a .env file.
    """
    Loads environment variables from the specified .env file and sets them in the OS environment.

    Args:
        filename (str): The path to the .env file containing environment variables.
    """
    with open(filename) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value