def get_key(filename):
    with open(filename, "r", encoding="utf-8") as file:
        key_content = file.read().strip()
    return key_content
