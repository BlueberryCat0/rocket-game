def load_frame(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()
