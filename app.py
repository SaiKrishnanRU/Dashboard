from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import timedelta, date
from count import minCheck
from database import userDb, sourceDb, listingDb

application = Flask(__name__)


@application.route("/saved", methods=["POST"])
def saved():
  # Updating minimum values for counts
  if request.method == "POST":
    connection = userDb()
    one = request.form["one"]
    three = request.form["three"]
    src = request.form["src"]
    if one == "" and three == "":
      pass
    elif one == "":
      connection.execute('update updates set past_limit = ? where source = ?;', (three, src))
      connection.commit()
    elif three == "":
      connection.execute('update updates set today_limit = ? where source = ?;', (one, src))
      connection.commit()
    else:
      connection.execute('update updates set today_limit = ?  , past_limit = ? where source = ?;', (one, three, src))
      connection.commit()
    connection.close()
    return redirect(request.referrer)


@application.route("/inventorymon")
def dashboard():
  connection = sourceDb()
  latestDate = connection.execute('select max(date) from source_date_counts where date not in (select max(date) from source_date_counts);')
  latestDate = latestDate.fetchall()
  cursor = connection.execute('select * from source_date_counts;')
  sources = cursor.fetchall()
  connection.close()
  page = "RUN"
  today = (date.today().strftime('%Y-%m-%d'))
  yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
  dayBefore = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
  fourthDay = (date.today() - timedelta(days=3)).strftime('%Y-%m-%d')
  connection = userDb()
  updatedDate = connection.execute('select max(date) from source_count;')
  updatedDate = updatedDate.fetchall()

  if latestDate[0][0] < dayBefore:
    connection.execute("UPDATE source_count SET today = ?, past = ?;", (0, 0))
    connection.commit()
    page = "ISSUE"
  else:
    if updatedDate[0][0] < dayBefore:
      connection.execute('CREATE TABLE IF NOT EXISTS source_count( source TEXT PRIMARY KEY, today INTEGER, past INTEGER, date TEXT);')
      connection.execute('CREATE TABLE IF NOT EXISTS updates( source TEXT, today_limit INTEGER, past_limit INTEGER);')
      connection.execute('CREATE TABLE IF NOT EXISTS graph_links( source TEXT PRIMARY KEY, link TEXT);')
      disSource = connection.execute('select distinct(source) from updates;')
      disSource = disSource.fetchall()
      upSource = []
      for value in disSource:
        upSource.append(value[0])

      # Table for tracking links to metadata graph
      for source in sources:
        if source[1] == dayBefore:
          currSource = source[0]
          connection.execute('INSERT OR IGNORE INTO graph_links (source,link) VALUES (?,?)', (currSource, ""))
          connection.commit()

      # Updating tables with all source names and counts
      if latestDate[0][0] < dayBefore:
        connection.execute("UPDATE source_count SET today = ?, past = ?;", (0, 0))
        connection.commit()
      for source in sources:
        if source[1] == dayBefore:
          currSource = source[0]
          tCount = source[2]
          if currSource not in upSource:
            connection.execute("INSERT INTO source_count (source , today , past , date) VALUES (?, ?, ?, ?)",(currSource, 0, 0, ""))
            connection.commit()
          connection.execute("UPDATE source_count SET today = ?, past = ?, date = ? WHERE source = ?;",(tCount, 0, "",currSource))
          connection.commit()
          if currSource not in upSource:
            connection.execute('INSERT INTO updates (source , today_limit , past_limit) VALUES (? , ?, ?)',
                            (currSource, 0, 0))
            connection.commit()
            upSource.append(currSource)
      sources = connection.execute('SELECT source FROM source_count')
      sources = sources.fetchall()
      # Calculating 3 day inventory
      connectionB = listingDb()
      pastDetails = connectionB.execute('SELECT vid_vin , sources FROM listings WHERE date_max >= ?;', (fourthDay,));
      pastDetails = pastDetails.fetchall()

      connectionB.close()
      for source in sources:
        count = 0
        for detail in pastDetails:
          for name in detail[1].split(','):
            if str(source[0]) == name:
              count = count + 1
        connection.execute('UPDATE source_count SET past = ?, date = ? WHERE source = ?;', (count, latestDate[0][0], str(source[0])))
        connection.commit()
  cursor = connection.execute('SELECT source_count.source, source_count.today, updates.today_limit, source_count.past, updates.past_limit, graph_links.link  FROM source_count INNER JOIN updates ON source_count.source = updates.source INNER JOIN graph_links ON graph_links.source = updates.source ORDER BY source_count.source')
  source = cursor.fetchall()
  connection.close()
  return render_template('inventorymon.html', details=source, updated=latestDate)


@application.route("/inventorymon/status")
def status():
  page = request.args.get("page")
  connection = sourceDb()
  latestDate = connection.execute('select max(date) from source_date_counts where date not in (select max(date) from source_date_counts);')
  latestDate = latestDate.fetchall()
  cursor = connection.execute('select * from source_date_counts ORDER BY source;')
  sources = cursor.fetchall()
  connection.close()

  # Displaying status on source count
  connection = userDb()
  connection.execute('CREATE TABLE IF NOT EXISTS source_count( source TEXT PRIMARY KEY, today INTEGER, past INTEGER);')
  today = (date.today().strftime('%Y-%m-%d'))
  yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
  dayBefore = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
  fourthDay = (date.today() - timedelta(days=3)).strftime('%Y-%m-%d')
  updatedDate = connection.execute('select max(date) from source_count;')
  updatedDate = updatedDate.fetchall()

  if updatedDate[0][0] < dayBefore:
    connection.execute('CREATE TABLE IF NOT EXISTS source_count( source TEXT PRIMARY KEY, today INTEGER, past INTEGER, date TEXT);')
    connection.execute('CREATE TABLE IF NOT EXISTS updates( source TEXT, today_limit INTEGER, past_limit INTEGER);')
    connection.execute('CREATE TABLE IF NOT EXISTS graph_links( source TEXT PRIMARY KEY, link TEXT);')

    disSource = connection.execute('select distinct(source) from source_count;')
    disSource = disSource.fetchall()
    upSource = []
    for value in disSource:
      upSource.append(value[0])

    # Table for tracking links to metadata graph
    for source in sources:
      if source[1] == dayBefore:
        currSource = source[0]
        connection.execute('INSERT OR IGNORE INTO graph_links (source,link) VALUES (?,?)', (currSource, ""))
        connection.commit()

    # Updating tables with all source names and counts
    if latestDate[0][0] < dayBefore:
      connection.execute("UPDATE source_count SET today = ?, past = ?;", (0, 0))
      connection.commit()
      page = "ISSUE"

    else:
      for source in sources:
        if source[1] == dayBefore:
          currSource = source[0]
          # Adding count for last 3 days
          tCount = source[2]
          if currSource not in upSource:
            connection.execute("INSERT INTO source_count (source , today , past , date) VALUES (?, ?, ?, ?)",(currSource, 0, 0, ""))
            connection.commit()
          connection.execute("UPDATE source_count SET today = ?, past = ?, date = ? WHERE source = ?;",(tCount, 0, "",currSource))
          connection.commit()
      sources = connection.execute('SELECT source FROM source_count')
      sources = sources.fetchall()
      # Calculating 3 day inventory
      connectionB = listingDb()
      pastDetails = connectionB.execute('SELECT vid_vin , sources FROM listings WHERE date_max >= ?;', (fourthDay,));
      pastDetails = pastDetails.fetchall()
      connectionB.close()
      for source in sources:
        count = 0
        for detail in pastDetails:
          for name in detail[1].split(','):
            if str(source[0]) == name:
              count = count + 1
        connection.execute('UPDATE source_count SET past = ?, date = ? WHERE source = ?;', (count, latestDate[0][0], str(source[0])))
        connection.commit()

  currDetail = connection.execute('SELECT source, today , past FROM source_count;')
  currDetail = currDetail.fetchall()
  limitDetail = connection.execute('SELECT source , today_limit , past_limit FROM updates;')
  limitDetail = limitDetail.fetchall()
  status = []
  for current in currDetail:
    for limit in limitDetail:
      if limit[0] == current[0]:
        day = 1
        status.append(minCheck(day, current, limit))
  status = list(filter(None, status))
  gStatus = []
  graph = connection.execute('SELECT source , link from graph_links')
  graph = graph.fetchall()
  for data in status:
    for detail in graph:
      if data[1] == detail[0]:
        gStatus.append(data.append(detail[1]))
        break
  connection.close()
  if page == "STATUS":
    return render_template('status.html', details=status)
  elif page == "ISSUE":
    return "No Inventories are updated today"
  elif page == "ALERT":
    if status == []:
      return "OK"
    else:
      return "Few inventories did not meet minimum value. Visit http://inventorymon.vinaudit.com:8000/inventorymon/status?page=STATUS"


if __name__ == "__main__":
  app.debug = True
  application.run()
