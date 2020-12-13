import sqlite3

#Create new database
dbname = 'enter Database Name (end it with .db)'
conn = sqlite3.connect(dbname)
c = conn.cursor()

#Create a table in the database
c.execute("""create blackjPlayers(name string, money integer)""")

#add money to your player account
name = 'player name'
c.execute("""update blackjPlayers set money = 100 where name = '{}'""".format(name))
conn.commit()
conn.close()
