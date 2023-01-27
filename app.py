from flask import Flask, abort, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import g
from pathlib import Path

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"# BASE_DIR  чтобы работать с ORM
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class QuoteModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   author = db.Column(db.String(32), unique=False)
   text = db.Column(db.String(255), unique=False)
   rate = db.Column(db.Integer)

   def __init__(self, author, text,rate=1):
       self.author = author
       self.text  = text
       self.rate = rate

   def to_dict(self):
       return {
           "id": self.id,
           'author': self.author,
           'text': self.text,
           'rate': self.rate
       }

#выводим весь список цитат
#здесь идет сериализация,т.е. преобразование питоновского объекта к формату json
#oбъeкт преобразуем в dict потом в  json
@app.route("/quotes")
def get_quotes():
    quotes = QuoteModel.query.all()
    quotes_dict=[quote.to_dict() for quote in quotes]
    return quotes_dict

#выводим цитату по заданному id
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote:
        return quote.to_dict(),200
    return f'not found',404

# добавление цитаты
@app.route("/quotes", methods=["POST"])
def create_quote():
    new_quote = request.json
    quote = QuoteModel(**new_quote)
    db.session.add(quote)
    db.session.commit()
    return quote.to_dict(), 201
# изменение цитаты
@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    quote_data = request.json
    quote = QuoteModel.query.get(id)
    if quote is None:
        return f"Quote with id={id} not found", 404
    if 'text' in quote_data:
        quote.text = quote_data['text']
    if 'author' in quote_data:
        quote.author = quote_data['author']
    # или можно так
    # for key, value in quote_data.items():
    #     setattr(quote, key, value)
    db.session.commit()
    return quote.to_dict(), 200

#удаление
@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    db.session.delete(quote)
    db.session.commit()
    return f"Quote with id={quote_id} delete", 200

#фильтр по рейтингу и автору в одном запросе"
@app.route("/quotes/filter", methods=["GET"])
def filter_quote():
    data = request.args
    if 'author'in data:
        quotes = QuoteModel.query.filter_by(author=data['author'])
        if quotes is None:
            return f"Quote with {data['author']} not found", 404
        quotes_dict = [quote.to_dict()['text'] for quote in quotes]
        return quotes_dict, 200

    if 'rate' in data:
        quotes = QuoteModel.query.filter_by(rate=data['rate'])
        if quotes is None:
            return f"Quote with {data['rate']} not found", 404
        quotes_dict = [quote.to_dict()['text']for quote in quotes]
        return quotes_dict, 200







if __name__ == "__main__":
    app.run(debug=True)

