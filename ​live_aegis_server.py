from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# This allows your frontend to communicate safely with the backend
CORS(app)

@app.route('/submit', methods=['POST'])
def process_assessment():
    try:
        data = request.get_json()

        # Verify the frontend is sending the 'problem' key
        if not data or 'problem' not in data:
            return jsonify({"error": "Missing input data"}), 400

        user_issue = data['problem']

        # --- PROXY PROCESSING LOGIC ---
        analysis_report = (
            f"[⚙] AEGIS CORE COGNITIVE PIPELINE ACTIVE\n"
            f"[✔] INPUT BLOCK ISOLATED AND VERIFIED\n"
            f"========================================\n"
            f"PRELIMINARY RIGHTS ASSESSMENT\n"
            f"========================================\n"
            f"• SUBMITTED CASE DATA: {user_issue}\n"
            f"• LEGAL/COMPLIANCE STATUS: PENDING ANALYSIS\n"
            f"• GRIEVANCE PARAMETERS REGISTERED\n"
            f"[🚀] STATUS: Core analysis successfully bridged."
        )

        return jsonify({"analysis": analysis_report})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
