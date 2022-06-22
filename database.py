import sqlite3

def userDb():
    connection = sqlite3.connect('dashboard.sqlite')
    return connection

def sourceDb():
    connection = sqlite3.connect('/home/vadata/marketfeedsv2/active_counts.sqlite')
    return connection

def listingDb():
    connection = sqlite3.connect('/home/vadata/marketfeedsv2/inventory_recent.sqlite')
    return connection

def createTb():
  connection = userDb()
  connection.execute('CREATE TABLE IF NOT EXISTS source_count( source TEXT PRIMARY KEY, today INTEGER, past INTEGER, date TEXT);')
  connection.execute('CREATE TABLE IF NOT EXISTS updates( source TEXT, today_limit INTEGER, past_limit INTEGER);')
  connection.execute('CREATE TABLE IF NOT EXISTS graph_links( source TEXT PRIMARY KEY, link TEXT);')
  connection.close()

def getLatestInfo():
  connection = sourceDb()
  latestDate = connection.execute('select max(date) from source_date_counts where date not in (select max(date) from source_date_counts);')
  latestDate = latestDate.fetchall()
  cursor = connection.execute('select * from source_date_counts;')
  sources = cursor.fetchall()
  connection.close()
  return latestDate , sources
