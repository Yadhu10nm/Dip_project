import os
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, request, send_from_directory
import config
from skills.system_orchestrator.implementation import SystemOrchestrator


class WebDashboardSkill:
    """
    Web Surveillance Dashboard Skill.
    Wraps Flask web service and MJPEG video streaming server,
    communicating strictly through the SystemOrchestrator.
    """

    def __init__(self, orchestrator: SystemOrchestrator, template_folder=None, static_folder=None):
        self.orchestrator = orchestrator
        templates = template_folder or os.path.join(config.BASE_DIR, "web", "templates")
        statics = static_folder or os.path.join(config.BASE_DIR, "web", "static")

        self.app = Flask(__name__, template_folder=templates, static_folder=statics)
        self._register_routes()

    def _register_routes(self):
        app = self.app

        @app.route("/")
        def index():
            return render_template("index.html")

        @app.route("/video_feed")
        def video_feed():
            return Response(
                self._generate_mjpeg_stream(),
                mimetype="multipart/x-mixed-replace; boundary=frame"
            )

        @app.route("/api/status")
        def api_status():
            st = self.orchestrator.get_status()
            state = self.orchestrator.state
            recognitions = state.detected_people
            auth_count = sum(1 for r in recognitions if r.get("authorized"))
            unauth_count = sum(1 for r in recognitions if not r.get("authorized"))

            return jsonify({
                "fps": round(state.fps, 1),
                "total_faces": len(recognitions),
                "authorized_count": auth_count,
                "unauthorized_count": unauth_count,
                "registered_users": st.get("enrolled_users_count", 0),
                "voice_enabled": state.sound_enabled,
                "is_dip_mode": state.dip_mode,
                "camera_flipped": state.camera_flipped,
                "locate_target": state.locate_target,
                "turret_connected": state.turret_connected,
                "turret_port": state.turret_port,
                "turret_is_mock": state.turret_is_mock,
                "turret_pan": round(state.turret_pan, 1),
                "turret_tilt": round(state.turret_tilt, 1),
                "turret_laser": state.turret_laser,
                "turret_target_locked": state.turret_target_locked,
            })


        @app.route("/api/command", methods=["POST"])
        def api_command():
            data = request.json or {}
            cmd_text = data.get("command", "")
            result = self.orchestrator.execute_command(cmd_text)
            return jsonify(result)

        @app.route("/api/toggle_dip", methods=["POST"])
        def api_toggle_dip():
            res = self.orchestrator.execute_command("toggle DIP")
            return jsonify({"success": True, "is_dip_mode": self.orchestrator.state.dip_mode})

        @app.route("/api/toggle_voice", methods=["POST"])
        def api_toggle_voice():
            res = self.orchestrator.execute_command("toggle sound")
            return jsonify({"success": True, "voice_enabled": self.orchestrator.state.sound_enabled})

        @app.route("/api/toggle_flip", methods=["POST"])
        def api_toggle_flip():
            self.orchestrator.camera.toggle_flip()
            self.orchestrator.state.camera_flipped = self.orchestrator.camera.flip_horizontal
            return jsonify({"success": True, "camera_flipped": self.orchestrator.state.camera_flipped})

        @app.route("/api/users", methods=["GET"])
        def api_get_users():
            users = self.orchestrator.enroller.list_users()
            return jsonify({"users": users})

        @app.route("/api/users", methods=["POST"])
        def api_create_user():
            data = request.json or {}
            name = data.get("name", "").strip()
            role = data.get("role", "Authorized Personnel").strip()
            if not name:
                return jsonify({"error": "User name is required"}), 400

            user_id = f"AUTH_{len(self.orchestrator.enroller.list_users()) + 1:03d}"
            # Initial placeholder record
            user = {
                "id": user_id,
                "name": name,
                "role": role,
                "sample_count": 0,
            }
            return jsonify({"success": True, "user": user})

        @app.route("/api/users/<user_id>", methods=["DELETE"])
        def api_delete_user(user_id):
            self.orchestrator.enroller.delete_person(user_id)
            return jsonify({"success": True, "message": f"User {user_id} revoked."})

        @app.route("/api/capture_enrollment_sample", methods=["POST"])
        def api_capture_enrollment():
            data = request.json or {}
            user_id = data.get("user_id")
            name = data.get("name", "Authorized User")
            if not user_id:
                return jsonify({"error": "user_id required"}), 400

            _, raw_frame = self.orchestrator.camera.get_frame()
            ok, msg = self.orchestrator.enroller.enroll_single_image(user_id, name, raw_frame)

            users = self.orchestrator.enroller.list_users()
            curr_user = next((u for u in users if u.get("id") == user_id), None)
            cnt = curr_user["sample_count"] if curr_user else 0

            return jsonify({
                "success": ok,
                "sample_count": cnt,
                "message": msg
            })

        @app.route("/api/upload_photos", methods=["POST"])
        @app.route("/api/upload_photo", methods=["POST"])
        def api_upload_photos():
            user_id = request.form.get("user_id")
            name = request.form.get("name")
            if not name and user_id:
                user_rec = self.orchestrator.enroller.get_user(user_id)
                if user_rec:
                    name = user_rec.get("name")
            name = name or "Authorized User"
            if not user_id:
                return jsonify({"error": "user_id required"}), 400

            uploaded_files = (
                request.files.getlist("photos")
                or request.files.getlist("photos[]")
                or request.files.getlist("photo")
            )
            if not uploaded_files or (len(uploaded_files) == 1 and uploaded_files[0].filename == ""):
                return jsonify({"error": "No image files provided"}), 400

            images = []
            for f in uploaded_files:
                if f.filename == "":
                    continue
                file_bytes = np.frombuffer(f.read(), np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                if img is not None:
                    images.append(img)

            if not images:
                return jsonify({"error": "No decodable images found"}), 400

            count, msg = self.orchestrator.enroller.enroll_batch_images(user_id, name, images)
            return jsonify({
                "success": count > 0,
                "processed_count": count,
                "total_images": len(images),
                "message": msg,
            })

        @app.route("/api/user_photo/<user_id>/<filename>")
        def api_user_photo(user_id, filename):
            folder = os.path.join(config.DATASET_DIR, user_id)
            return send_from_directory(folder, filename)

        @app.route("/api/intruders", methods=["GET"])
        def api_get_intruders():
            logs = self.orchestrator.audit.get_logs(limit=50)
            return jsonify({"logs": logs})

        @app.route("/api/intruder_snapshot/<filename>")
        def api_intruder_snapshot(filename):
            return send_from_directory(config.INTRUDERS_DIR, filename)

        @app.route("/api/clear_intruders", methods=["POST"])
        def api_clear_intruders():
            self.orchestrator.audit.clear_logs()
            return jsonify({"success": True, "message": "Intrusion audit log cleared."})

        # --- ESP32 Sentry Turret & Calibration Endpoints ---
        @app.route("/api/turret/status", methods=["GET"])
        def api_turret_status():
            st = self.orchestrator.turret.get_status()
            ports = self.orchestrator.turret.list_ports()
            return jsonify({"status": st, "available_ports": ports})

        @app.route("/api/turret/move", methods=["POST"])
        def api_turret_move():
            data = request.json or {}
            pan = float(data.get("pan", 90.0))
            tilt = float(data.get("tilt", 90.0))
            laser = data.get("laser")
            res = self.orchestrator.turret.manual_move(pan, tilt, laser=laser)
            return jsonify(res)

        @app.route("/api/turret/laser", methods=["POST"])
        def api_turret_laser():
            data = request.json or {}
            state = bool(data.get("laser", False))
            res = self.orchestrator.turret.set_laser(state)
            return jsonify(res)

        @app.route("/api/turret/pulse", methods=["POST"])
        def api_turret_pulse():
            res = self.orchestrator.turret.pulse_laser(duration_seconds=1.5)
            return jsonify(res)

        @app.route("/api/turret/calibrate_center", methods=["POST"])
        def api_turret_calibrate_center():
            res = self.orchestrator.turret.calibrate_center_current()
            return jsonify(res)

        @app.route("/api/turret/calibrate", methods=["POST"])
        def api_turret_calibrate():
            data = request.json or {}
            res = self.orchestrator.turret.update_calibration(data)
            return jsonify(res)

        @app.route("/api/turret/reset_calibration", methods=["POST"])
        def api_turret_reset_calib():
            res = self.orchestrator.turret.reset_calibration()
            return jsonify(res)

        @app.route("/api/turret/reconnect", methods=["POST"])
        def api_turret_reconnect():
            data = request.json or {}
            port = data.get("port")
            res = self.orchestrator.turret.reconnect(port)
            return jsonify(res)

        @app.route("/api/turret/set_mode", methods=["POST"])
        def api_turret_set_mode():
            data = request.json or {}
            mode = data.get("mode", "AUTO")
            res = self.orchestrator.turret.set_mode(mode)
            return jsonify(res)

        @app.route("/api/turret/aim_pixel", methods=["POST"])
        def api_turret_aim_pixel():
            data = request.json or {}
            px = float(data.get("x", 320))
            py = float(data.get("y", 240))
            laser = bool(data.get("laser", True))
            res = self.orchestrator.turret.aim_at_pixel(px, py, laser=laser)
            return jsonify(res)


    def _generate_mjpeg_stream(self):
        """Yields MJPEG encoded video multipart chunks from orchestrator process_cycle."""
        while True:
            display_frame, _, _ = self.orchestrator.process_cycle()
            if display_frame is None:
                continue

            ret, buffer = cv2.imencode(".jpg", display_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

    def run(self, host="0.0.0.0", port=5000, debug=False):
        self.orchestrator.start_camera()
        print(f"\n[WebDashboardSkill] Control Center: http://127.0.0.1:{port}\n")
        self.app.run(host=host, port=port, debug=debug, threaded=True)
