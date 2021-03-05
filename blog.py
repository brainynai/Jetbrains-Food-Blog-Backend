import sqlite3
import sys
from contextlib import closing


class DB(object):
    def __init__(self, databaseName):
        self.conn = sqlite3.connect(databaseName)

    def __del__(self):
        self.conn.close()

    def exNfetch(self, sql):
        #print(sql)
        with closing(self.conn.cursor()) as c:
            c.execute(sql)
            self.conn.commit()
            return c.fetchall()


dbName = sys.argv[1]

db = DB(dbName)
db.exNfetch('create table ingredients ('
            'ingredient_id integer primary key, '
            'ingredient_name text not null unique)')

db.exNfetch('create table measures ('
            'measure_id integer primary key,'
            'measure_name text unique)')

db.exNfetch('create table meals ('
            'meal_id integer primary key, '
            'meal_name text not null unique)')

data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
        "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
        "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

db.exNfetch('insert into meals(meal_name) values ("' + '"), ("'.join(data['meals']) + '");')
db.exNfetch('insert into ingredients(ingredient_name) values ("' + '"), ("'.join(data['ingredients']) + '");')
db.exNfetch('insert into measures(measure_name) values ("' + '"), ("'.join(data['measures']) + '");')

del(db)
