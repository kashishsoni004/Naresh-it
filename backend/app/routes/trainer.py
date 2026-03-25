from flask import Blueprint, request, jsonify
from app.services.trainer_service import generate_trainer

trainer_bp = Blueprint("trainer", __name__)

@trainer_bp.route("/trainer", methods=["POST"])
def trainer():
    try:
        data = request.json
        name = data.get("name")
        role = data.get("role")

        if not name or not role:
            return jsonify({"error": "Name and role required"}), 400

        result = generate_trainer(name, role)

        return jsonify({
            "result": result
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500