import os
import re
from urllib.parse import unquote
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration
GATEWAY = "VBV Lookup"
WEB_KEY = "AloneOp"

def validate_card_format(cc_string):
    """Validate card format CC|MM|YYYY|CVV"""
    if not cc_string or '|' not in cc_string:
        return False, "Missing | separators"
    
    parts = cc_string.split('|')
    if len(parts) != 4:
        return False, f"Expected 4 parts, got {len(parts)}"
    
    cc_num, mes, ano, cvv = parts
    
    # Validate card number (13-19 digits)
    if not cc_num.isdigit() or len(cc_num) < 13 or len(cc_num) > 19:
        return False, "Invalid card number"
    
    # Validate month (01-12)
    if not mes.isdigit() or len(mes) != 2 or int(mes) < 1 or int(mes) > 12:
        return False, "Invalid month"
    
    # Validate year (4 digits)
    if not ano.isdigit() or len(ano) != 4:
        return False, "Invalid year"
    
    # Validate CVV (3-4 digits)
    if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
        return False, "Invalid CVV"
    
    return True, "Valid"

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

@app.route('/key=<key>/cc=<path:cc>', methods=['GET'])
def handle_request(key, cc):
    # Validate access key
    if key != WEB_KEY:
        return jsonify({"error": "Invalid access key"}), 403

    # Validate CC parameter
    if not cc:
        return jsonify({"error": "CC parameter is required"}), 400

    # URL decode the card data (handles %7C -> |)
    cc = unquote(cc)

    # Validate card format
    is_valid, error_msg = validate_card_format(cc)
    if not is_valid:
        return jsonify({
            "error": f"Invalid CC format: {error_msg}. Use CC|MM|YYYY|CVV",
            "received": cc,
            "example": "4532123456789012|12|2025|123"
        }), 400

    # Parse CC format (CC|MM|YYYY|CVV)
    parts = cc.split('|')
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
        "usage": f"/key=[KEY]/cc=[CC]",
        "format": "CC|MM|YYYY|CVV",
        "example": f"/key=[KEY]/cc=[CC]"
    })

if __name__ == '__main__':
    print("VBV API running on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
