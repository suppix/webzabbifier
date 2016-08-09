

def human_readable_date(timedelta):
    age = ""
    age_length = 0

    if timedelta.years != 0:
        age += str(timedelta.years) + "y "
        age_length += 1
    if timedelta.months != 0:
        age += str(timedelta.months) + "m "
        age_length += 1
    if timedelta.days != 0:
        age += str(timedelta.days) + "d "
        age_length += 1
    if timedelta.hours != 0 and age_length < 3:
        age += str(timedelta.hours) + "h "
        age_length += 1
    if timedelta.minutes != 0 and age_length < 3:
        age += str(timedelta.minutes) + "m "
        age_length += 1
    if timedelta.seconds != 0 and age_length < 3:
        age += str(timedelta.seconds) + "s "
        age_length += 1

    return age