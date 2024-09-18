def alphanum_only(string: str) -> str:
    return "".join([char for char in string if char.isalnum()])
