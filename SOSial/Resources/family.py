from flask import session, redirect, request, jsonify
from flask_restful import Resource
import pickle

from SOSial.Models.user import UserModel
from SOSial.Models.details import UserDetailModel


class UserFamily(Resource):
    def post(self):
        username = session.get("username", None)
        user_id = session["user_id"]

        if username:
            json_data = request.get_json()
            family_member = UserModel.fetch_using_email(json_data["email"])

            if family_member is None:
                return {"message": "Family member has not registered."}, 404

            if family_member.user_id == user_id:
                return {"message": "You cannot add yourself as a family member."}, 406

            user_details = UserDetailModel.fetch_using_id(user_id=user_id)

            if user_details is None:
                user_details = UserDetailModel(user_id=user_id, location=None, family=pickle.dumps([family_member.user_id]))
            else:
                family = []
                if user_details.family is not None:
                    family = pickle.loads(user_details.family)
                if family_member.user_id in family:
                    return {"message": "Family member already exists in family"}, 400
                family.append(family_member.user_id)
                user_details.family = pickle.dumps(family[:])

            try:
                user_details.save_to_db()
            except Exception as e:
                print(e)
                return {"message": "An error occurred while adding family member."}, 500

            return {"user_id": family_member.user_id,
                    "email": family_member.email,
                    "name": family_member.first_name + " " + family_member.last_name}, 200

        else:
            return {"message": "User not logged in."}, 401

    def delete(self):
        username = session.get("username", None)
        user_id = session.get("user_id", None)
        if username:
            user_details = UserDetailModel.fetch_using_id(user_id)
            json_data = request.get_json()
            family = pickle.loads(user_details.family)
            family_member = UserModel.fetch_using_email(json_data["email"])
            if family_member.user_id in family:
                family.remove(family_member.user_id)
                user_details.family = pickle.dumps(family[:])
                try:
                    user_details.save_to_db()
                except:
                    return {"message": "An error occurred while deleting family member."}, 500

                return {"message": "Family member successfully deleted."}, 200
            else:
                return {"message": "Family member is not part of the family."}, 400

        else:
            return {"message": "User not logged in."}, 401
