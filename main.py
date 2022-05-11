from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import timedelta, date

application = Flask(__name__)

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

@application.route("/saved", methods=["POST", "GET"])
def saved():
    # Updating minimum values for counts
    if request.method == "POST":
        conn = sqlite3.connect('dashboard.sqlite')
        one = request.form["one"]
        three = request.form["three"]
        src = request.form["src"]
        if one == "" and three == "":
            pass
        elif one == "":
            conn.execute('update updates set past_limit = ? where source = ?;', (three, src))
            conn.commit()
        elif three == "":
            conn.execute('update updates set today_limit = ? where source = ?;', (one, src))
            conn.commit()
        else:
            conn.execute('update updates set today_limit = ?  , past_limit = ? where source = ?;', (one, three, src))
            conn.commit()
        conn.close()
        # return '', 204
        return redirect(request.referrer)


@application.route("/inventorymon")
def dashboard():
    conn = sqlite3.connect('/home/vadata/marketfeedsv2/active_counts.sqlite')
    cursor = conn.execute('select * from source_date_counts;')
    source = cursor.fetchall()
    # upSource = conn.execute('select distinct(source) from source_date_count;')
    # upSource = upSource.fetchall()
    conn.close()

    conn = sqlite3.connect('dashboard.sqlite')
    conn.execute('DROP TABLE IF EXISTS source_count;')
    conn.execute('CREATE TABLE IF NOT EXISTS source_count( source TEXT PRIMARY KEY, today INTEGER, past INTEGER);')
    conn.execute('CREATE TABLE IF NOT EXISTS updates( source TEXT, today_limit INTEGER, past_limit INTEGER);')
    conn.execute('CREATE TABLE IF NOT EXISTS graph_links( source TEXT PRIMARY KEY, link TEXT);')
    today = date.today()
    today = today - timedelta(days=1)
    d1 = today.strftime("%Y-%m-%d")

    disSource = conn.execute('select distinct(source) from updates;')
    disSource = disSource.fetchall()
    upSource = []
    for value in disSource:
        upSource.append(value[0])

    # Table for tracking links to metadata graph
    for row in source:
        if row[1] == d1:
            currSource = row[0]
            conn.execute('INSERT OR IGNORE INTO graph_links (source,link) VALUES (?,?)', (currSource, ""))
            conn.commit()

    # Updating tables with all source names and counts
    for row in source:
        if row[1] == d1:
            currSource = row[0]
            # Adding count for last 3 days
            past = countCheck(source, currSource) + row[2]
            tCount = row[2]
            conn.execute("INSERT INTO source_count (source , today , past) VALUES (?, ?, ?)",
                         (currSource, tCount, past))
            conn.commit()
            if currSource not in upSource:
                conn.execute('INSERT INTO updates (source , today_limit , past_limit) VALUES (? , ?, ?)',
                             (currSource, 0, 0))
                conn.commit()
                upSource.append(currSource)
    cursor = conn.execute(
        'SELECT source_count.source, source_count.today, updates.today_limit, source_count.past, updates.past_limit, graph_links.link  FROM source_count INNER JOIN updates ON source_count.source = updates.source INNER JOIN graph_links ON graph_links.source = updates.source')
    source = cursor.fetchall()
    conn.close()
    return render_template('inventorymon.html', a=source)


@application.route("/inventorymon/status")
def status():
    def minCheck(day, detail, limit):
        # 0 - If minimum not met for today and last 3 days sum
        # 1 - If minimum not met today
        # 2 - If  minimum not met for 3 days sum
        days = day + 1
        #mismatch = [0, detail[0], detail[day], limit[day], detail[days], limit[days]]
        mismatch = []
        if detail[day] < limit[day] and detail[days] < limit[days]:
            mismatch = [0, detail[0], detail[day], limit[day], detail[days], limit[days]]
            return mismatch
        elif detail[day] < limit[day]:
            mismatch = [1, detail[0], detail[day], limit[day]]
            return mismatch
        elif detail[days] < limit[days]:
            mismatch = [2, detail[0], detail[days], limit[days]]
            return mismatch

    conn = sqlite3.connect('/home/vadata/marketfeedsv2/active_counts.sqlite')
    cursor = conn.execute('select * from source_date_counts;')
    source = cursor.fetchall()
    conn.close()



    # Displaying status on source count
    conn = sqlite3.connect('dashboard.sqlite')
    conn.execute('DROP TABLE IF EXISTS source_count;')
    conn.execute('CREATE TABLE IF NOT EXISTS source_count( source TEXT PRIMARY KEY, today INTEGER, past INTEGER);')
    today = date.today()
    today = today - timedelta(days=1)
    d1 = today.strftime("%Y-%m-%d")
    for row in source:
        if row[1] == d1:
            currSource = row[0]
            past = countCheck(source, currSource) + row[2]
            tCount = row[2]
            conn.execute("INSERT INTO source_count (source , today , past) VALUES (?, ?, ?)",(currSource, tCount, past))
            conn.commit()


    currDetail = conn.execute('SELECT source, today , past FROM source_count;')
    currDetail = currDetail.fetchall()
    limitDetail = conn.execute('SELECT source , today_limit , past_limit FROM updates;')
    limitDetail = limitDetail.fetchall()
    status = []
    for a in currDetail:
        for b in limitDetail:
            if b[0] == a[0]:
                day = 1
                status.append(minCheck(day, a, b))
    status = list(filter(None, status))
    gStatus = []
    graph = conn.execute('SELECT source , link from graph_links')
    graph = graph.fetchall()
    for data in status:
        for detail in graph:
            if data[1] == detail[0]:
                gStatus.append(data.append(detail[1]))
                break
    conn.close()
    return render_template('status.html', a=status)


if __name__ == "__main__":
     app.debug = True
     application.run()