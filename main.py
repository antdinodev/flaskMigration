from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from utilities import login
import sys
from flask import abort
from flask_migrate import Migrate

app = Flask(__name__)

port = "localhost:5432"
table = "todoapp"

connection_uri = f"postgres://{login.DATABASE}:{login.SECRET_KEY}@{port}/{table}"

app.config['SQLALCHEMY_DATABASE_URI'] = connection_uri
db = SQLAlchemy(app)
#migrate = Migrate(app, db)
migrate = Migrate(app)

#flask db init is not working
# i cannot move on
#skip this migration lesson


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

db.create_all()

@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())


#the better way with ajax async request
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route("/remove_todo/<todo_id>")
def delete_todo(todo_id):
    api_key = request.args.get("api_key")
    api = "TopSecretAPIKey"
    if api_key == api:
        todo = db.session.query(Todo).get(todo_id)
        if todo:
            print(f"deleting cafe: {todo}")
            db.session.delete(todo)
            db.session.commit()
            return jsonify(response={"success": f"Successfully deleted cafe.{todo} {todo.description}"}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404

    else:
        return jsonify(error={"Sorry, that's not allowed. Make Sure you have the correct api_key."}), 403



if __name__ == '__main__':
    app.run(debug=True)
