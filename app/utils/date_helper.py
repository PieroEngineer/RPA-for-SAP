from datetime import datetime, timedelta

def subtract_n_days(date_str, n):
    # Convert string to datetime object
    # %d = day, %m = month, %Y = 4-digit year
    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
    
    # Subtract exactly 31 days
    past_date = date_obj - timedelta(days=n)
    
    # Return formatted as "dd.mm.yyyy"
    return past_date.strftime("%d.%m.%Y")

def check_overlap(range1: tuple, range2: tuple):
    date_format = "%d.%m.%Y"

    # Parse string dates into datetime objects
    # range1 = ("dd.mm.yyyy", "dd.mm.yyyy")
    start1 = datetime.strptime(range1[0], date_format)
    end1 = datetime.strptime(range1[1], date_format)
    
    start2 = datetime.strptime(range2[0], date_format)
    end2 = datetime.strptime(range2[1], date_format)
    
    # Overlap Logic: (StartA <= EndB) AND (EndA >= StartB)
    return start1 <= end2 and end1 >= start2