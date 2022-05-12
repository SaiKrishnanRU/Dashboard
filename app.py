from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import timedelta, date
from count import countCheck, minCheck
from database import userDb, sourceDb

application = Flask(__name__)

@application.route("/saved", methods=["POST", "GET"])
def saved():
    # Updating minimum values for counts
    if request.method == "POST":
        conn = userDb()
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


@application.route("/inventorymon/")
def dashboard():
    conn = sourceDb()
    updateT = conn.execute('select max(date) from source_date_counts;')
    updateT = updateT.fetchall()
    cursor = conn.execute('select * from source_date_counts;')
    source = cursor.fetchall()
    conn.close()

    conn = userDb()
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
        'SELECT source_count.source, source_count.today, updates.today_limit, source_count.past, updates.past_limit, graph_links.link  FROM source_count INNER JOIN updates ON source_count.source = updates.source INNER JOIN graph_links ON graph_links.source = updates.source ORDER BY source_count.source')
    source = cursor.fetchall()
    conn.close()
    return render_template('inventorymon.html', a=source, b=updateT)


@application.route("/inventorymon/status")
def status(): 
    conn = sourceDb()
    cursor = conn.execute('select * from source_date_counts ORDER BY source;')
    source = cursor.fetchall()
    conn.close()


    # Displaying status on source count
    conn = userDb()
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
