from flask import Flask, request
import random
import sqlite3
from flask import g
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

DATABASE = 'test.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()



def convert_data(quote: tuple) -> dict:
    keys = ["id", "author", "text"]
    return (dict(zip(keys, quote)))

#выводим весь список цит
@app.route("/quotes")
def get_quotes():
    select_quotes = "SELECT * from quotes"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    quotes = cursor.fetchall()
    quotes = list(map(convert_data, quotes))
    return quotes

#выводим цитату по заданному id
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    select_quote = "SELECT * FROM quotes WHERE id=?;"
    cursor = get_db().cursor()
    cursor.execute(select_quote, (quote_id,))
    quote = cursor.fetchone()
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    quote = convert_data(quote)
    return quote, 200

#добавление цитаты
@app.route("/quotes", methods=["POST"])
def create_quotes():
    new_quote = request.json
    create_quote_sql = """
    INSERT INTO
    quotes (author,text)
    VALUES
    (?, ?);
    """
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()
    cursor.execute(create_quote_sql, (new_quote['author'], new_quote['text']))
    connection.commit()
    cursor.close()
    connection.close()
    new_quote["id"] = cursor.lastrowid
    return new_quote, 201

#редактирование цитаты
@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    new_quote = request.json
    connection = get_db()
    cursor = get_db().cursor()
    update_quotes = """UPDATE quotes SET author=?, text=? WHERE id=?"""
    cursor.execute(update_quotes,(new_quote["author"], new_quote["text"],quote_id,))
    connection.commit()
    cursor.close()
    if cursor.rowcount:
         return {}, 200
    return f"Quote with id={quote_id} not found", 404



 #удаление элемента
@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    del_id = """DELETE FROM quotes WHERE id=?;"""
    connection = get_db()
    cursor = get_db().cursor()
    cursor.execute(del_id, (id,))
    connection.commit()
    cursor.close()
    connection.close()
    if cursor.rowcount:
        return f"Quote with id {id} is deleted.", 200
    return f"Quote with id={id} not found", 404




if __name__ == "__main__":
    app.run(debug=True)

