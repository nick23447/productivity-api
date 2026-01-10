from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from taskflow import db, bcrypt
from taskflow.models import User

users = Blueprint("users", __name__, url_prefix="/api/auth")

@users.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email, password required"}), 400

    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already in use"}), 409

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(email=email, password=hashed)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": token,
        "user": {"id": user.id, "email": user.email}
    }), 201


@users.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": token,
        "user": {"id": user.id, "email": user.email}
    }), 200


# @users.route("/api/auth/logout")
# def logout():
#     # JWT-style logout is usually “client deletes token”.
#     # If you use refresh tokens or server-side token blacklist, handle it here.
#     return jsonify({"message": "logged out"}), 200
