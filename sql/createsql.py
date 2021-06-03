import sqlite3

connect = sqlite3.connect('question.db')

cursor = connect.cursor()

# CREATE TABLE AND COLUMN
# cursor.execute("CREATE TABLE Database \
#                (id integer primary key, \
#                 Sentence text)")
# connect.commit()

#INSERT DATA
# cursor.execute("INSERT INTO Database (Sentence) \
#                 VALUES ('He is a boy.')")
# connect.commit()


