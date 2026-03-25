# backend/app/routes/chat.py
from flask import Blueprint, request, jsonify
from app.services.chat_service import get_chat_response

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"content": [{"type": "text", "text": "Invalid request."}]}), 400

        # Frontend sends: { system, max_tokens, messages: [...] }
        messages = data.get('messages', [])
        system_prompt = data.get('system', None)

        if not messages:
            return jsonify({"content": [{"type": "text", "text": "Please enter a message."}]}), 400

        reply = get_chat_response(messages, system_prompt)

        # ✅ Match the Anthropic API response format the frontend expects
        return jsonify({
            "content": [{"type": "text", "text": reply}]
        }), 200

    except Exception as e:
        print(f"❌ Chat route error: {e}")
        return jsonify({
            "content": [{"type": "text", "text": "Sorry, something went wrong. Please call us at +91 8179191999."}]
        }), 500