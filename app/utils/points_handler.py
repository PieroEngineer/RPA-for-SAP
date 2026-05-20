def remove_last_point(s) -> str:
    s = str(s)
    if not s:  # Check if the string is empty
        return s
        
    points_to_avoid = (',', '.')
    if s[-1] in points_to_avoid:
        return s[:-1]
    else:
        return s
