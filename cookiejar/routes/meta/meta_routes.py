import os
from flask import Blueprint, jsonify
from cookiejar.services.tracker.tracker_service import TrackerService
from cookiejar.services.vendor.vendor_service import VendorService

bp = Blueprint("meta", __name__)

@bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@bp.get("/version")
def version():
    return jsonify({
        "color": os.getenv("APP_COLOR", "unknown"),
        "version": os.getenv("APP_VERSION", "dev")
    }), 200

@bp.get("/stats")
def stats():
    t = TrackerService.stats()
    v = VendorService.stats()
    return jsonify({**t, **v}), 200
