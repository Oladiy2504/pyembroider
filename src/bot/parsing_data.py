def strings_parsing(s : str) -> list:
    ans = []
    for i in s.split(','):
        color, length = map(int, i.split())
        try:
            color = int(color)
            length = int(length)
            ans.append([color, length])
        except:
            return []
    return ans

def conv_parsing(s : str) -> list:
    try:
        length, width = map(int, s.split())
        return [length, width]
    except:
        return []