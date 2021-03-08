import sqlite3
import sys
from contextlib import closing


class DB(object):
    def __init__(self, databaseName):
        self.conn = sqlite3.connect(databaseName)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def __del__(self):
        self.conn.close()

    def exNfetch(self, sql):
        # print(sql)
        with closing(self.conn.cursor()) as c:
            c.execute(sql)
            self.conn.commit()
            return c.fetchall()

    def exNrowid(self, sql):
        # print(sql)
        with closing(self.conn.cursor()) as c:
            rowid = c.execute(sql).lastrowid
            self.conn.commit()
            return rowid


def stageOneInit(database):
    database.exNfetch('create table ingredients ('
                      'ingredient_id integer primary key, '
                      'ingredient_name text not null unique)')

    database.exNfetch('create table measures ('
                      'measure_id integer primary key,'
                      'measure_name text unique)')

    database.exNfetch('create table meals ('
                      'meal_id integer primary key, '
                      'meal_name text not null unique)')

    data = {"meals": ("breakfast", "brunch", "lunch", "supper"),
            "ingredients": ("milk", "cacao", "strawberry", "blueberry", "blackberry", "sugar"),
            "measures": ("ml", "g", "l", "cup", "tbsp", "tsp", "dsp", "")}

    database.exNfetch('insert into meals(meal_name) values ("' + '"), ("'.join(data['meals']) + '");')
    database.exNfetch('insert into ingredients(ingredient_name) values ("' + '"), ("'.join(data['ingredients']) + '");')
    database.exNfetch('insert into measures(measure_name) values ("' + '"), ("'.join(data['measures']) + '");')


def stageTwoInit(database):
    database.exNfetch('create table recipes ('
                      'recipe_id integer primary key,'
                      'recipe_name text not null,'
                      'recipe_description text);')


def stageThreeInit(database):
    database.exNfetch('create table serve ('
                      'serve_id integer primary key,'
                      'recipe_id integer not null,'
                      'meal_id integer not null,'
                      'FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id)'
                      'FOREIGN KEY(meal_id) REFERENCES meals(meal_id));')


def recipeInput(database):
    while True:
        recipeName = input('Enter recipe name: ')
        if len(recipeName) == 0:
            break
        recDesc = input('Enter description: ')

        recipeID = database.exNrowid(f'insert into recipes(recipe_name, recipe_description) values ("{recipeName}","{recDesc}");')

        for mealTime in database.exNfetch('select * from meals'):
            print(f'{mealTime[0]}) {mealTime[1]} ', end='')
        print()

        mealList = input('When can it be served: ')
        for mealID in mealList.split():
            database.exNfetch(f'insert into serve(recipe_id, meal_id) values ({recipeID},{mealID});')


dbName = sys.argv[1]

with DB(dbName) as db:
    stageOneInit(db)
    stageTwoInit(db)
    stageThreeInit(db)
    recipeInput(db)
    #print(db.exNfetch('select * from serve'))


