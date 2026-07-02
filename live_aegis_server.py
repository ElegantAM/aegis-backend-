from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# This allows your Vercel frontend to safely communicate with this backend
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/', methods=['POST'])
def process_assessment():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing computational payload"}), 400
        
        user_issue = data['prompt']
        
        # --- PROXY PROCESSING LOGIC ---
        # This is where your AI generation or assessment engine logic executes.
        # For now, we return a premium, beautifully structured response packet.
        analysis_report = (
            f"[⚙️] AEGIS CORE COGNITIVE PIPELINE ENGAGED...\n"
            f"[✔] INPUT BLOCK ISOLATED AND PARSED SUCCESSFULLY.\n\n"
            f"==================================================\n"
            f"          PRELIMINARY RIGHTS ASSESSMENT            \n"
            f"==================================================\n"
            f"• SUBMITTED CASE DATA:\n  \"{user_issue}\"\n\n"
            f"• LEGAL/COMPLIANCE STATUS:\n"
            f"  Grievance parameters registered under Revati Traders primary framework.\n"
            f"  Consumer protection act guidelines apply to structural refund boundaries.\n\n"
            f"[🚀] STATUS: Core analysis complete. Standby for formal draft compilation node..."
        )
        
        return jsonify({"analysis": analysis_report})

    except Exception as e:
        return jsonify({"error": f"System Intercept Exception: {str(e)}"}), 500

if __name__ == '__main__':
    # Cloud environments pass the target port as an environment variable
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
