def squeeze(text):
    out = []
    i = 0
    while i < len(text):
        j = i
        while j < len(text) and text[j] == text[i]:
            j += 1
        run = j - i
        out.append(text[i] if run == 1 else f"{text[i]}{run}")
        i = j
    return "".join(out)


def unsqueeze(packed):
    out = []
    i = 0
    while i < len(packed):
        ch = packed[i]
        j = i + 1
        while j < len(packed) and packed[j].isdigit():
            j += 1
        out.append(ch * (int(packed[i + 1 : j]) if j > i + 1 else 1))
        i = j
    return "".join(out)
