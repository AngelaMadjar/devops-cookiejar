from flask import Blueprint, jsonify
from cookiejar.services.database.seed_service import SeedService
from cookiejar.services.database.cleanup_service import CleanupService

bp = Blueprint("db", __name__, url_prefix="/db")


@bp.post("/populate")
def populate_all():
    try:
        result = SeedService.populate_from_csv("data/seed_anonymized.csv")
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal error", "details": str(e)}), 500


@bp.post("/empty")
def empty_all():
    try:
        result = CleanupService.empty_all()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal error", "details": str(e)}), 500


@bp.post("/trackers/empty")
def empty_trackers():
    try:
        result = CleanupService.empty_trackers_only()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal error", "details": str(e)}), 500


@bp.post("/vendors/empty")
def empty_vendors():
    try:
        result = CleanupService.empty_vendors_only()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "internal error", "details": str(e)}), 500
