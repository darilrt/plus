
class style:
    bold = 1
    underline = 4

class color:
    black = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37

class bg:
    black = 40
    red = 41
    green = 42
    yellow = 43
    blue = 44
    magenta = 45
    cyan = 46
    white = 47

def rtext(text: str, color: int=None, style: int=None, bg: int=None) -> str:
    if color is not None:
        text = f"\033[{color}m{text}\033[0m"
    if style is not None:
        text = f"\033[{style}m{text}\033[0m"
    if bg is not None:
        text = f"\033[{bg}m{text}\033[0m"
    return text