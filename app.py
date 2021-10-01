from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_marshmallow import Marshmallow

app = Flask(__name__)
db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class User(db.Model):
    id = db.Column(db.Integer)
    name = db.Column(db.String(50), nullable=False, unique=True, primary_key=True)
    age = db.Column(db.Integer, nullable=False)

    def __init__ (self, name, age):
        self.name = name
        self.age = age

class UserSchema(ma.Schema):
    class Meta():
        fields = ('name', 'age')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def add_new(obj):
    db.session.add(obj)
    try:
        db.session.commit()
    except:
        db.session.rollback()

class Hello(Resource):
    def get(self):
        return users_schema.dump(User.query.all())

api.add_resource(Hello, '/')

@app.post('/user/add')
def user_add():
    res = request.get_json()
    name = res.get("name")
    age = res.get("age")
    if User.query.get(name) is None:
        new_user  = User(name, age)
        add_new(new_user)
        return {
            "status": True,
            "data": {
                "message": "User added",
                "user": user_schema.dump(User.query.get(name))
            }
        }

    return {
            "status": False,
            "error": {
                "code": -1000,
                "message": "User exists"
            }
        }

@app.get('/users')
def user_list():
    print(users_schema.dump(User.query.all()))
    return {
        "result": users_schema.dump(User.query.all())
    }

@app.delete('/user/delete')
def user_delete():
    res = request.get_json()
    user = User.query.get(res.get("name"))
    if user:
        db.session.delete(user)
        db.session.commit()
        return {
            "status": "true",
            "data": {
                "message": "User deleted"
            }
        }
    else:
        return {
            "status": "false",
            "error": {
                "message": "User does not exists"
            }
        }, 403

if __name__ == '__main__':
    app.run(debug=True)