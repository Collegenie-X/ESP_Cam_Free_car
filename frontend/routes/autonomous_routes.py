"""
Autonomous Driving API Routes

Provides routes for starting/stopping autonomous driving,
status checking, and single frame analysis.
"""

from flask import Blueprint, jsonify, current_app, request, Response
import logging
import requests
import cv2
import numpy as np
import base64

autonomous_bp = Blueprint("autonomous", __name__, url_prefix="/api/autonomous")
logger = logging.getLogger(__name__)


@autonomous_bp.route("/start", methods=["POST"])
def start_autonomous():
    """
    Start autonomous driving

    Returns:
        {"success": bool, "message": str}
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Autonomous service not initialized",
                    }
                ),
                500,
            )

        # Get ESP32 service
        esp32_service = current_app.config.get("ESP32_SERVICE")
        if not esp32_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "ESP32 service not initialized",
                    }
                ),
                500,
            )

        # Verify ESP32 connection before starting (with extended timeout)
        try:
            response = requests.get(f"{esp32_service.base_url}/status", timeout=5)
            if response.status_code != 200:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"ESP32-CAM not responding (HTTP {response.status_code})",
                        }
                    ),
                    400,
                )
        except requests.exceptions.RequestException as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Cannot connect to ESP32-CAM: {str(e)}",
                    }
                ),
                400,
            )

        # Start autonomous driving immediately without waiting for initial frame
        # This prevents timeout issues
        result = auto_service.start()

        # Try to get initial frame asynchronously (non-blocking)
        try:
            capture_url = esp32_service.get_capture_url()
            response = requests.get(capture_url, timeout=3)

            if response.status_code == 200:
                # Decode image
                nparr = np.frombuffer(response.content, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if image is not None:
                    # Analyze initial frame
                    frame_result = auto_service.analyze_single_frame(
                        image, draw_overlay=True
                    )

                    if frame_result.get("success"):
                        # Convert image to base64
                        processed_image = base64.b64encode(
                            frame_result["image"]
                        ).decode("utf-8")

                        # Add initial frame data
                        result["initial_frame"] = {
                            "processed_image": processed_image,
                            "command": frame_result["command"],
                            "state": frame_result["state"],
                            "histogram": frame_result["histogram"],
                            "confidence": frame_result["confidence"],
                        }
                        logger.info("Initial frame analysis successful")

        except Exception as e:
            logger.warning(f"Could not get initial frame (non-critical): {e}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Failed to start autonomous driving: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/stop", methods=["POST"])
def stop_autonomous():
    """
    Stop autonomous driving

    Returns:
        {"success": bool, "message": str, "stats": {...}}
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Autonomous service not initialized",
                    }
                ),
                500,
            )

        # Get ESP32 service
        esp32_service = current_app.config.get("ESP32_SERVICE")
        if not esp32_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "ESP32 service not initialized",
                    }
                ),
                500,
            )

        # Stop autonomous service (this will send stop command)
        result = auto_service.stop()

        # Double-check with emergency stop to ensure motors are stopped
        logger.info("Executing emergency stop verification")
        try:
            esp32_service.send_command("control", {"cmd": "stop"})
        except Exception as e:
            logger.warning(f"Emergency stop verification failed: {e}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Failed to stop autonomous driving: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/status")
def get_autonomous_status():
    """
    Get autonomous driving status

    Returns:
        {
            "is_running": bool,
            "last_command": str,
            "state": str,
            "command_history": [...],
            "stats": {...}
        }
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Autonomous service not initialized",
                    }
                ),
                500,
            )

        status = auto_service.get_status()
        return jsonify({"success": True, **status})

    except Exception as e:
        logger.error(f"Failed to get autonomous status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/analyze", methods=["POST"])
def analyze_frame():
    """
    Analyze single frame (for testing)

    Request:
        - JSON: {"image_url": "http://..."} or
        - multipart/form-data: file upload

    Returns:
        {
            "success": bool,
            "command": str,
            "state": str,
            "histogram": {...},
            "confidence": float,
            "image_base64": str  # Processed image (Base64)
        }
    """
    try:
        auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
        if not auto_service:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Autonomous service not initialized",
                    }
                ),
                500,
            )

        # Get image
        image = None

        # Method 1: JSON with URL
        if request.is_json:
            data = request.get_json()
            image_url = data.get("image_url")

            if image_url:
                # Get image from ESP32-CAM
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    nparr = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Method 2: File upload
        elif "file" in request.files:
            file = request.files["file"]
            nparr = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Method 3: Direct capture from ESP32-CAM
        else:
            esp32_service = current_app.config.get("ESP32_SERVICE")
            if esp32_service:
                capture_url = esp32_service.get_capture_url()
                logger.info(f"Capturing image from: {capture_url}")
                response = requests.get(capture_url, timeout=10)
                if response.status_code == 200:
                    nparr = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    logger.info("Image captured successfully")
                else:
                    logger.error(f"Image capture failed: HTTP {response.status_code}")

        if image is None:
            return (
                jsonify({"success": False, "error": "Could not get image"}),
                400,
            )

        # Analyze frame
        result = auto_service.analyze_single_frame(image, draw_overlay=True)

        if not result["success"]:
            return jsonify(result), 500

        # Encode image as Base64
        image_base64 = base64.b64encode(result["image"]).decode("utf-8")

        return jsonify(
            {
                "success": True,
                "command": result["command"],
                "state": result["state"],
                "histogram": result["histogram"],
                "confidence": result["confidence"],
                "image_base64": image_base64,
            }
        )

    except Exception as e:
        logger.error(f"Frame analysis failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/stream")
def autonomous_stream():
    """
    Autonomous driving real-time stream
    Gets ESP32-CAM stream, processes lane tracking, and re-streams

    Returns:
        MJPEG stream
    """

    def generate():
        """Generate MJPEG stream (limited to 5fps)"""
        import time
        from flask import current_app as app

        # Get services within Application context
        with current_app.app_context():
            auto_service = current_app.config.get("AUTONOMOUS_SERVICE")
            esp32_service = current_app.config.get("ESP32_SERVICE")

        if not auto_service or not esp32_service:
            logger.error("Services not initialized")
            return

        try:
            capture_url = esp32_service.get_capture_url()
            logger.info(f"Connecting to stream: {capture_url}")

            # Frame rate control
            TARGET_FPS = 5
            FRAME_INTERVAL = 1.0 / TARGET_FPS  # 0.2 seconds
            frame_count = 0
            last_frame_time = 0

            while True:
                try:
                    # Frame rate limiting
                    current_time = time.time()
                    if current_time - last_frame_time < FRAME_INTERVAL:
                        time.sleep(0.01)  # Small sleep to prevent CPU overuse
                        continue

                    # Get image from ESP32-CAM
                    response = requests.get(capture_url, timeout=5)
                    if response.status_code != 200:
                        logger.error(f"Failed to get image: {response.status_code}")
                        message = "Failed to get image from ESP32-CAM"
                        yield b"--frame\r\nContent-Type: text/plain\r\n\r\n" + message.encode(
                            "utf-8"
                        ) + b"\r\n"
                        time.sleep(1)  # Wait before retry
                        continue

                    # Decode image
                    nparr = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if image is None or image.size == 0:
                        logger.warning("Invalid image data")
                        continue

                    # Process lane tracking
                    result = auto_service.process_frame(
                        image, send_command=True, debug=True
                    )

                    # Get overlay image
                    if result.get("success") and "debug_images" in result:
                        processed_image = result["debug_images"].get("7_final", image)
                    else:
                        processed_image = image

                    # Encode as JPEG
                    _, buffer = cv2.imencode(
                        ".jpg", processed_image, [cv2.IMWRITE_JPEG_QUALITY, 70]
                    )
                    frame = buffer.tobytes()

                    # Send frame
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                    )

                    # Update timing
                    last_frame_time = current_time
                    frame_count += 1

                    # Log status (every 10 frames)
                    if frame_count % 10 == 0:
                        status = "Running" if auto_service.is_running else "Monitoring"
                        logger.info(
                            f"Stream status: frames={frame_count}, "
                            f"state={status}, "
                            f"command={result.get('command', 'N/A')}"
                        )

                except Exception as e:
                    logger.error(f"Stream processing error: {e}")
                    time.sleep(FRAME_INTERVAL)

        except Exception as e:
            logger.error(f"Stream generation error: {e}")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@autonomous_bp.route("/check_camera")
def check_camera():
    """
    Check ESP32-CAM connection status
    """
    try:
        esp32_service = current_app.config.get("ESP32_SERVICE")
        if not esp32_service:
            return jsonify({"success": False, "error": "ESP32 service not found"}), 500

        # 1. Basic connection check
        base_url = esp32_service.base_url
        try:
            response = requests.get(f"{base_url}/status", timeout=5)
            if response.status_code != 200:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"ESP32-CAM not responding (code: {response.status_code})",
                        }
                    ),
                    400,
                )
        except requests.exceptions.RequestException as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"ESP32-CAM connection failed: {str(e)}",
                    }
                ),
                400,
            )

        # 2. Stream URL - return success (actual stream checked on connection)
        stream_url = esp32_service.get_stream_url()

        return jsonify(
            {
                "success": True,
                "message": "ESP32-CAM OK",
                "base_url": base_url,
                "stream_url": stream_url,
            }
        )

    except Exception as e:
        logger.error(f"Camera check failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@autonomous_bp.route("/test")
def test_autonomous():
    """
    Test autonomous driving system

    Returns:
        {
            "success": bool,
            "components": {
                "lane_tracker": bool,
                "esp32_service": bool,
                "autonomous_service": bool
            }
        }
    """
    try:
        components = {
            "lane_tracker": current_app.config.get("LANE_TRACKER") is not None,
            "esp32_service": current_app.config.get("ESP32_SERVICE") is not None,
            "autonomous_service": current_app.config.get("AUTONOMOUS_SERVICE")
            is not None,
        }

        all_ok = all(components.values())

        return jsonify(
            {
                "success": all_ok,
                "components": components,
                "message": "All components OK" if all_ok else "Missing components",
            }
        )

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
