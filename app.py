from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Resource, Api

from models import db, User

app = Flask(__name__)

# configure the database connection
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize flask_migrate

migrate = Migrate(app=app, db=db)

# initalize sqlachemy db
db.init_app(app=app)

# flask_restful
api = Api(app=app)


# resources
class Users(Resource):
    def get(self):
        users = User.query.all()

        # parse the list from the db into a format that the client can understand
        users_list = []

        # iterate

        for user in users:
            users_list.append(user.to_dict())

        # return the response
        # response = {
        #     "message": "Users fetched successfully",
        #     "code": 200,
        #     "data": users_list,
        # }

        return make_response(users_list, 200)

    def post(self):
        try:
            data = request.get_json()

            f_name = data.get("first_name")
            l_name = data.get("last_name")
            mail = data.get("email")
            phone_number = data.get("phone")

            # validations
            email_check = User.query.filter_by(email=mail).first()

            if email_check:
                response = {"message": "Email address already taken", "code": 422}
                return make_response(response, 422)

            # create a user instance
            user = User(
                first_name=f_name, last_name=l_name, email=mail, phone=phone_number
            )

            # add to the database
            db.session.add(user)
            db.session.commit()

            # create a response to show the client app that everything went well
            response = {"message": "User account created successfully", "code": 200}

            return make_response(response, 200)

        except ValueError as ve:
            response = {
                "message": "An error was encountered",
                "code": 400,
                "error": f"Error: {str(ve)}",
            }

            return make_response(response, 400)

        except Exception as e:
            response = {
                "message": "Internal Server Error",
                "code": 500,
                "error": f"Error: {str(e)}",
            }

            return make_response(response, 500)


class UserById(Resource):
    def get(self, id):
        user = User.query.filter_by(id=id).first()

        if not user:
            response = {
                "message": "No user found",
                "code": 404,
            }
            return make_response(response, 404)
        else:
            return make_response(user.to_dict(), 200)

    def patch(self, id):
        # check to see if the user exists in the database
        try:
            user = User.query.get(id)

            if user:
                # update the info
                data = request.get_json()

                # get the updated info from the client

                first_name = data.get("first_name")
                last_name = data.get("last_name")
                email = data.get("email")
                phone = data.get("phone")

                # check to see which attributes are to be updated
                if first_name:
                    user.first_name = first_name
                if last_name:
                    user.last_name = last_name
                if email:
                    # validate that the new email is not already taken

                    email_check = User.query.filter_by(email=email).first()

                    if email_check:
                        response = {
                            "message": "Email address already taken",
                            "code": 422,
                        }
                        return make_response(response, 422)

                    user.email = email
                if phone:
                    user.phone = phone

                # commit the updates to the db

                db.session.commit()

                # return response
                response = {
                    "message": "Account updated successfully",
                    "code": 200,
                    "data": user.to_dict(),
                }

                return make_response(response, 200)
        except ValueError as ve:
            response = {
                "message": "An error was encountered",
                "code": 400,
                "error": f"Error: {str(ve)}",
            }

            return make_response(response, 400)

        except Exception as e:
            response = {
                "message": "Internal Server Error",
                "code": 500,
                "error": f"Error: {str(e)}",
            }

            return make_response(response, 500)

        else:
            response = {
                "message": "No user found",
                "code": 404,
            }

            return make_response(response, 404)

    def delete(self, id):
        # confirm that the user exists
        user = User.query.filter_by(id=id).first()
        try:
            if user:
                db.session.delete(user)
                db.session.commit()

                response = {
                    "code": 200,
                    "message": f"User with id {id} was deleted successfully",
                }

                return make_response(response, 200)
            else:
                response = {
                    "message": "No user found",
                    "code": 404,
                }

            return make_response(response, 404)

        except Exception as e:
            response = {
                "message": "Internal Server Error",
                "code": 500,
                "error": f"Error: {str(e)}",
            }

            return make_response(response, 500)


api.add_resource(Users, "/users")
api.add_resource(UserById, "/users/<int:id>")
