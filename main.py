import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration
GATEWAY = "VBV Lookup"
WEB_KEY = "AloneOp"

def check_vbv_bin(bin_number):
    """Check BIN status from vbvbin.txt file"""
    try:
        if not os.path.exists("vbvbin.txt"):
            return {
                "status": "3D FALSE",
                "response": "BIN Database Not Found"
            }

        with open("vbvbin.txt", "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line.startswith(bin_number[:6]):
                    parts = line.split('|')
                    if len(parts) >= 3:
                        return {
                            "status": parts[1],
                            "response": parts[2]
                        }

        return {
            "status": "3D FALSE",
            "response": "BIN Not Found in Database"
        }
    except Exception as e:
        print(f"Error reading BIN database: {e}")
        return {
            "status": "3D FALSE",
            "response": "Lookup Error"
        }

@app.route('/key=<key>/cc=<cc>', methods=['GET'])
def handle_request(key, cc):
    # Validate access key
    if key != WEB_KEY:
        return jsonify({"error": "Invalid access key"}), 403

    # Validate CC parameter
    if not cc:
        return jsonify({"error": "CC parameter is required"}), 400

    # Parse CC format (CC|MM|YYYY|CVV)
    parts = cc.split('|')
    if len(parts) != 4:
        return jsonify({"error": "Invalid CC format. Use CC|MM|YYYY|CVV"}), 400

    cc_num, mes, ano, cvv = parts
    bin_number = cc_num[:6]

    # Check VBV status
    vbv_status = check_vbv_bin(bin_number)

    # Determine status and emoji
    if "FALSE" in vbv_status["status"]:
        status = "✅ Passed"
        response_emoji = "✅"
    else:
        status = "❌ Rejected"
        response_emoji = "❌"

    response_text = f"{response_emoji} {vbv_status['response']}"

    # Prepare response data
    data = {
        "CC": cc,
        "Gateway": GATEWAY,
        "Status": status,
        "Response": response_text,        
        "Dev": "@YAMRAJSAHIL2"
    }

    return jsonify(data)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "VBV Checker API",
        "usage": f"/key=[key]/cc=[cc]",
        "format": "CC|MM|YYYY|CVV",
        "example": f"/key=[key]/cc=[cc]"
    })

if __name__ == '__main__':
    print("VBV API running")
    app.run(debug=True)