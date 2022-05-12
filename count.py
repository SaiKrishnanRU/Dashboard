from datetime import timedelta, date

# Checking last days count for inventory
def countCheck(source, currSource):
    count = 0
    today = date.today()
    today = today - timedelta(days=1)
    yesterday = today - timedelta(days=1)
    dayBefore = today - timedelta(days=2)
    d2 = yesterday.strftime("%Y-%m-%d")
    d3 = dayBefore.strftime("%Y-%m-%d")
    for past in source:
        if past[1] == d2 and past[0] == currSource:
            count = count + past[2]
    for past in source:
        if past[1] == d3 and past[0] == currSource:
            count = count + past[2]
    return count


# Checking if minimum inventory value is met
def minCheck(day, detail, limit):
    # 0 - If minimum not met for today and last 3 days sum
    # 1 - If minimum not met today
    # 2 - If  minimum not met for 3 days sum
    days = day + 1
    if detail[day] < limit[day] and detail[days] < limit[days]:
        mismatch = [0, detail[0], detail[day], limit[day], detail[days], limit[days]]
        return mismatch
    elif detail[day] < limit[day]:
        mismatch = [1, detail[0], detail[day], limit[day]]
        return mismatch
    elif detail[days] < limit[days]:
        mismatch = [2, detail[0], detail[days], limit[days]]
        return mismatch
