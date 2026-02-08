from flask import Blueprint, request, jsonify
from cookiejar.services.vendor.vendor_service import VendorService

bp = Blueprint("vendor", __name__, url_prefix="/vendors")


@bp.patch("/<int:vendor_id>/description")
def update_vendor_description(vendor_id: int):
    payload = request.get_json(silent=True) or {}
    new_desc = payload.get("vendor_description")

    if not new_desc or not str(new_desc).strip():
        return jsonify({"error": "vendor_description is required"}), 400

    try:
        result = VendorService.update_vendor_description(vendor_id, str(new_desc))
        return jsonify(result), 200
    except ValueError as e:
        # vendor not found or invalid input
        msg = str(e)
        status = 404 if "not found" in msg.lower() else 400
        return jsonify({"error": msg}), status
    except Exception as e:
        return jsonify({"error": "internal error", "details": str(e)}), 500


@bp.get("")
def list_vendors():
    # /vendors?limit=1000
    limit = request.args.get("limit", default=500, type=int)
    limit = max(1, min(limit, 5000))  # safety clamp

    rows = VendorService.list_vendors(limit=limit)
    return jsonify(rows), 200

