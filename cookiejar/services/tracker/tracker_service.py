from datetime import datetime, timezone
from cookiejar import db

from cookiejar.daos.tracker.tracker_dao import TrackerDAO
from cookiejar.daos.tracker.tracker_purpose_dao import TrackerPurposeDAO
from cookiejar.daos.tracker.tracker_purposes_dao import TrackerPurposesDAO


def now_utc():
    return datetime.now(timezone.utc)


class TrackerService:
    @staticmethod
    def update_tracker_purpose(tracker_id: int, new_purpose_text: str) -> dict:
        """
        SCD Type-2 update for tracker purpose:
        - Get/create tracker_purpose row (lookup table)
        - Set previous current link to is_current=False
        - Insert new current link is_current=True
        - Update tracker.last_modified

        Run as transaction
        """
        if not new_purpose_text or not new_purpose_text.strip():
            raise ValueError("new_purpose_text must be a non-empty string")

        new_purpose_text = new_purpose_text.strip()
        ts = now_utc()

        with db.session.begin():
            # Validate tracker exists (NOTE: if there's ui i can remove this)
            tracker = TrackerDAO.get_by_id(tracker_id)
            if tracker is None:
                raise ValueError(f"Tracker {tracker_id} not found")

            # Get or create purpose id
            new_purpose_id = TrackerPurposeDAO.get_or_create(new_purpose_text)

            # Set is_current=False for previous purpose
            closed_count = TrackerPurposesDAO.set_not_current(tracker_id)

            # Set is_current=True for new purpose
            TrackerPurposesDAO.insert_current(tracker_id, new_purpose_id, created_at=ts)

            # Update tracker.last_modified
            TrackerDAO.touch_last_modified(tracker_id, ts)

        return {
            "status": "ok",
            "tracker_id": tracker_id,
            "tracker_purpose_id": new_purpose_id,
            "previous_current_rows_closed": closed_count,
            "last_modified": ts.isoformat(),
        }


    @staticmethod
    def delete_tracker(tracker_id: int) -> dict:
        """
        Deletes a tracker:
        - delete link rows (child tables)
        - delete tracker row (parent table)
        In a single transaction.
        """
        with db.session.begin():
            tracker = TrackerDAO.get_by_id(tracker_id)
            if tracker is None:
                raise ValueError(f"Tracker {tracker_id} not found")

            deleted_links = TrackerPurposesDAO.delete_by_tracker_id(tracker_id)
            deleted_trackers = TrackerDAO.delete_by_id(tracker_id)

        return {
            "status": "ok",
            "tracker_id": tracker_id,
            "deleted_tracker_rows": deleted_trackers,
            "deleted_tracker_purpose_links": deleted_links,
        }

    @staticmethod
    def list_trackers(limit: int = 500) -> list[dict]:
        """
        Returns rows for UI table:
        Domain, Category, Vendor, Type, Name, Purpose
        """
        return TrackerDAO.list_trackers(limit=limit)
    
    @staticmethod
    def stats() -> dict:
        return {
            "tracker_count": TrackerDAO.count_trackers(),
            "sample_tracker_id": TrackerDAO.get_sample_tracker_id(),
        }