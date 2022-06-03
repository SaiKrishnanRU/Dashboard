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
