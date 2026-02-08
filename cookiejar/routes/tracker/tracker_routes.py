from flask import Blueprint, request, jsonify, render_template
from cookiejar.services.tracker.tracker_service import TrackerService

bp = Blueprint("tracker", __name__, url_prefix="/trackers")


@bp.patch("/<int:tracker_id>/purpose")
def update_tracker_purpose(tracker_id: int):
    """
    Update a tracker's purpose

    Request JSON:
      { "tracker_purpose": "Some new purpose" }
    """
    payload = request.get_json(silent=True) or {}
    new_purpose = payload.get("tracker_purpose")

    if not new_purpose or not str(new_purpose).strip():
        return jsonify({"error": "tracker_purpose is required"}), 400

    try:
        result = TrackerService.update_tracker_purpose(tracker_id, str(new_purpose))
        return jsonify(result), 200
    except ValueError as e: # NOTE: could remove this if there's a UI
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error", "details": str(e)}), 500


@bp.delete("/<int:tracker_id>")
def delete_tracker(tracker_id: int):
    """
    Deletes a tracker and its link rows.
    """
    try:
        result = TrackerService.delete_tracker(tracker_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "internal error", "details": str(e)}), 500
    
@bp.get("")
def list_trackers():
    rows = TrackerService.list_trackers(limit=1000)
    return render_template("trackers.html", rows=rows)
