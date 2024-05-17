def escape(data: str):
    print(data)
    returned = ""
    for c in data:
        # Escape special characters
        if c in '&#;`|*?~<>^()[]{}$\\,\x0A\xFF':
            returned += '\\'
        returned += c
    return returned

print(escape(';pwd;'))