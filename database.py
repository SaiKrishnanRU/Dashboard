import sqlite3

def userDb():
    conn = sqlite3.connect('dashboard.sqlite')
    return conn

def sourceDb():
    conn = sqlite3.connect('/home/vadata/marketfeedsv2/active_counts.sqlite')
    return conn

def listingDb():
    conn = sqlite3.connect('/home/vadata/marketfeedsv2/inventory_recent.sqlite')
    return conn
