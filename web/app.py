import os
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, request, send_from_directory
import config
from core.surveillance_system import SurveillanceSystem

app = Flask(__name__, template_folder="templates", static_folder="static")

# Shared Surveillance System instance
surveillance = SurveillanceSystem()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(
        surveillance.generate_mjpeg_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/api/status")
def api_status():
    return jsonify(surveillance.get_status_summary())

@app.route("/api/toggle_dip", methods=["POST"])
def api_toggle_dip():
    is_dip = surveillance.toggle_dip_mode()
    return jsonify({"success": True, "is_dip_mode": is_dip})

@app.route("/api/toggle_voice", methods=["POST"])
def api_toggle_voice():
    current = surveillance.alert_system.voice_enabled
    surveillance.alert_system.voice_enabled = not current
    return jsonify({"success": True, "voice_enabled": surveillance.alert_system.voice_enabled})

@app.route("/api/users", methods=["GET"])
def api_get_users():
    users = surveillance.access_manager.list_users()
    return jsonify({"users": users})

@app.route("/api/users", methods=["POST"])
def api_create_user():
    data = request.json or {}
    name = data.get("name", "").strip()
    role = data.get("role", "Authorized Personnel").strip()
    if not name:
        return jsonify({"error": "User name is required"}), 400

    user = surveillance.access_manager.add_user(name, role)
    return jsonify({"success": True, "user": user})

@app.route("/api/users/<user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    surveillance.access_manager.revoke_user(user_id)
    surveillance._refresh_user_cache()
    return jsonify({"success": True, "message": f"User {user_id} revoked and model retrained."})

@app.route("/api/capture_enrollment_sample", methods=["POST"])
def api_capture_enrollment():
    data = request.json or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    raw_frame = surveillance.read_raw_frame()
    success = surveillance.access_manager.enroll_from_frame(user_id, raw_frame)

    user = surveillance.access_manager.get_user(user_id)
    sample_count = user["sample_count"] if user else 0

    return jsonify({
        "success": success,
        "sample_count": sample_count,
        "message": "Face sample captured successfully" if success else "No face detected in camera view"
    })

@app.route("/api/upload_photo", methods=["POST"])
def api_upload_photo():
    user_id = request.form.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    if "photo" not in request.files:
        return jsonify({"error": "No photo file provided"}), 400

    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Read image into OpenCV
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({"error": "Invalid image file"}), 400

    faces = surveillance.detector.detect_faces(img)
    if len(faces) == 0:
        return jsonify({"error": "No face found in uploaded photo"}), 400

    largest = max(faces, key=lambda f: f[2] * f[3])
    roi, _ = surveillance.detector.extract_face_roi(img, largest)
    surveillance.access_manager.save_sample_with_augmentations(user_id, roi)
    surveillance.access_manager.retrain()
    surveillance._refresh_user_cache()

    user = surveillance.access_manager.get_user(user_id)
    return jsonify({
        "success": True,
        "sample_count": user["sample_count"] if user else 0,
        "message": "Photo uploaded and processed successfully!"
    })

@app.route("/api/retrain", methods=["POST"])
def api_retrain():
    success, message = surveillance.access_manager.retrain()
    surveillance._refresh_user_cache()
    return jsonify({"success": success, "message": message})

@app.route("/api/user_photo/<user_id>/<filename>")
def api_user_photo(user_id, filename):
    folder = os.path.join(config.DATASET_DIR, user_id)
    return send_from_directory(folder, filename)

@app.route("/api/intruders", methods=["GET"])
def api_get_intruders():
    logs = surveillance.alert_system.get_audit_logs()
    return jsonify({"logs": logs})

@app.route("/api/intruder_snapshot/<filename>")
def api_intruder_snapshot(filename):
    return send_from_directory(config.INTRUDERS_DIR, filename)

@app.route("/api/clear_intruders", methods=["POST"])
def api_clear_intruders():
    surveillance.alert_system.clear_audit_logs()
    return jsonify({"success": True, "message": "Intrusion log cleared."})

def run_server(host="0.0.0.0", port=5000, debug=False):
    surveillance.start_camera()
    print(f"\n=======================================================")
    print(f"  AI CCTV SURVEILLANCE & INTRUDER DETECTION SYSTEM")
    print(f"  Live Control Center: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == "__main__":
    run_server()
