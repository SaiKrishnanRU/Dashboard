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
