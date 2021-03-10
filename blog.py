import sqlite3
import sys
from contextlib import closing


class DB(object):
    def __init__(self, databaseName):
        self.conn = sqlite3.connect(databaseName)
        with closing(self.conn.cursor()) as c:
            c.execute('PRAGMA foreign_keys = ON;')
            self.conn.commit()

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


def stageFourInit(database):
    database.exNfetch('create table quantity ('
                      'quantity_id integer primary key,'
                      'quantity integer not null,'
                      'recipe_id integer not null,'
                      'measure_id integer not null,'
                      'ingredient_id integer not null,'
                      'FOREIGN KEY(recipe_id) REFERENCES recipes(recipe_id),'
                      'FOREIGN KEY(measure_id) REFERENCES measures(measure_id),'
                      'FOREIGN KEY(ingredient_id) REFERENCES ingredients(ingredient_id));')


def recipeInput(database):
    while True:
        recipeName = input('Enter recipe name: ')
        if len(recipeName) == 0:
            break
        recDesc = input('Enter description: ')

        recipeID = database.exNrowid(
            f'insert into recipes(recipe_name, recipe_description) values ("{recipeName}","{recDesc}");')

        for mealTime in database.exNfetch('select * from meals'):
            print(f'{mealTime[0]}) {mealTime[1]} ', end='')
        print()

        mealList = input('When can it be served: ')
        for mealID in mealList.split():
            database.exNfetch(f'insert into serve(recipe_id, meal_id) values ({recipeID},{mealID});')

        while True:
            ingInput = input('Input qty of ingredient (number, unit, ingredient): ')
            if len(ingInput) == 0:
                break

            ingTokens = ingInput.split()
            qty = ingTokens[0]

            if not qty.isdigit():
                print('Qty needs to be a number. ')
                continue

            if len(ingTokens) > 2:
                unit = ingTokens[1]
                ing = ingTokens[2]
                possMeasures = database.exNfetch(f"select * from measures where measure_name like '{unit}%'")
            else:
                unit = ''
                ing = ingTokens[1]
                possMeasures = database.exNfetch(f"select * from measures where measure_name like '{unit}'")

            if len(possMeasures) != 1:
                print('Measure not conclusive.')
                continue

            measureID = possMeasures[0][0]

            possIng = database.exNfetch(f"select * from ingredients where ingredient_name like '%{ing}%'")
            if len(possIng) != 1:
                print('Ingredient not conclusive.')
                continue

            ingID = possIng[0][0]

            database.exNfetch(
                f'insert into quantity(quantity, recipe_id, measure_id, ingredient_id) values ({qty}, {recipeID}, {measureID}, {ingID})')


def parseArgs(ingArg, mealArg):
    ingStr = ingArg.lstrip('--ingredients').strip('=')
    mealStr = mealArg.lstrip('--meals').strip('=')

    ingL = ingStr.split(',')
    mealL = mealStr.split(',')

    return ingL, mealL


def getRecipes(database, ingredients, meals):
    ingComma = '("' + '","'.join(ingredients) + '")'
    mealComma = '("' + '","'.join(meals) + '")'

    print(ingComma, mealComma)

    ingIDsTuples = database.exNfetch(f'select * from ingredients where ingredient_name in {ingComma}')
    mealIDsTuples = database.exNfetch(f'select * from meals where meal_name in {mealComma}')

    print(ingIDsTuples, mealIDsTuples)

    ingIDsComma = '(' + ','.join([str(i[0]) for i in ingIDsTuples]) + ')'
    mealIDsComma = '(' + ','.join([str(i[0]) for i in mealIDsTuples]) + ')'

    recipeIDTuples = database.exNfetch(f'select * from quantity where ingredient_id in {ingIDsComma}')
    recipeIDsComma = '(' + ','.join([str(i[2]) for i in recipeIDTuples]) + ')'

    print(recipeIDTuples, recipeIDsComma)

    serveIDsTuples = database.exNfetch(f'select * from serve where recipe_id in {recipeIDsComma} and meal_id in {mealIDsComma}')

    recipeIDs = '(' + ','.join([str(i[1]) for i in serveIDsTuples]) + ')'

    recipeTuples = database.exNfetch(f'select * from recipes where recipe_id in {recipeIDs}')

    if len(recipeTuples) == 0:
        print('There are no such recipes in the database.')
    else:
        print('Recipes selected for you: ', end='')
        print(', '.join([str(i[1]) for i in recipeTuples]))


dbName = sys.argv[1]
ingList, mealList = [], []

if len(sys.argv) == 4:
    ingList, mealList = parseArgs(sys.argv[2], sys.argv[3])
elif len(sys.argv) != 2:
    print(f'Error: Expected 0 or 2 arguments. Found {len(sys.argv)}.')
    exit()

with DB(dbName) as db:
    if len(sys.argv) == 4:
        getRecipes(db, ingList, mealList)
    else:
        stageOneInit(db)
        stageTwoInit(db)
        stageThreeInit(db)
        stageFourInit(db)
        # print(db.exNfetch('select * from serve'))
        recipeInput(db)
