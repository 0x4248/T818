import sqlite3
conn = sqlite3.connect("t818.db")
c = conn.cursor()
# if no db then create it



def generate_databases():
	c.execute("CREATE TABLE IF NOT EXISTS Users (ID INTEGER PRIMARY KEY, Username TEXT, Password TEXT, Role TEXT)")
	c.execute("CREATE TABLE IF NOT EXISTS Posts (ID INTEGER PRIMARY KEY, User TEXT, FileID TEXT, Tags TEXT, Description TEXT, Date TEXT, Rating TEXT, Score INTEGER, Type TEXT, Source TEXT, FileName TEXT)")
	conn.commit()

def add_post(User, FileID, Tags, Description, Date, Rating, Score, Type, Source, FileName):
	c.execute("INSERT INTO Posts (User, FileID, Tags, Description, Date, Rating, Score, Type, Source, FileName) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (User, FileID, Tags, Description, Date, Rating, Score, Type, Source, FileName))
	conn.commit()

def get_post(ID):
	c.execute("SELECT * FROM Posts WHERE ID=?", (ID,))
	data = c.fetchone()
	return data

def get_recent_posts():
	c.execute("SELECT * FROM Posts ORDER BY ID DESC LIMIT 50")
	data = c.fetchall()
	return data

def get_with_tags(tag):
	# c.execute("SELECT * FROM Posts WHERE Tags LIKE ?", (tag,))
	# not exact match e.g ?q=tag1,tag4 should work with post tag1,tag2,tag3,tag4
	c.execute("SELECT * FROM Posts WHERE Tags LIKE ?", (f"%{tag}%",))
	data = c.fetchall()
	return data

if not c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users'").fetchone():
	generate_databases()