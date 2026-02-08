from datetime import datetime, timezone
from cookiejar import db
from cookiejar.daos.vendor.vendor_dao import VendorDAO
from cookiejar.daos.vendor.vendor_description_dao import VendorDescriptionDAO
from cookiejar.daos.vendor.vendor_descriptions_dao import VendorDescriptionsDAO


def now_utc():
    return datetime.now(timezone.utc)


class VendorService:
    @staticmethod
    def update_vendor_description(vendor_id: int, new_description_text: str) -> dict:
        """
        SCD Type-2 update for vendor description:
        - Get/create vendor_description row (lookup table)
        - Set previous current link to is_current=False
        - Insert new current link is_current=True
        - Update vendor.last_modified

        Run as transaction
        """
        if not new_description_text or not new_description_text.strip():
            raise ValueError("vendor_description must be a non-empty string")

        new_description_text = new_description_text.strip()
        ts = now_utc()

        with db.session.begin():
            vendor = VendorDAO.get_by_id(vendor_id)
            if vendor is None:
                raise ValueError(f"Vendor {vendor_id} not found")

            new_desc_id = VendorDescriptionDAO.get_or_create(new_description_text)

            current_desc_id = VendorDescriptionsDAO.get_current_vendor_description_id(vendor_id)
            if current_desc_id == new_desc_id:
                VendorDAO.touch_last_modified(vendor_id, ts)
                return {
                    "status": "ok",
                    "vendor_id": vendor_id,
                    "message": "description already current (no link change)",
                    "vendor_description_id": new_desc_id,
                    "last_modified": ts.isoformat(),
                }

            closed = VendorDescriptionsDAO.set_not_current(vendor_id)
            VendorDescriptionsDAO.insert_current(vendor_id, new_desc_id, created_at=ts)
            VendorDAO.touch_last_modified(vendor_id, ts)

        return {
            "status": "ok",
            "vendor_id": vendor_id,
            "vendor_description_id": new_desc_id,
            "previous_current_rows_closed": closed,
            "last_modified": ts.isoformat(),
        }

    @staticmethod
    def list_vendors(limit: int = 500) -> list[dict]:
        return VendorDAO.list_vendors(limit=limit)
    
    @staticmethod
    def stats() -> dict:
        return {
            "vendor_count": VendorDAO.count_vendors(),
            "sample_vendor_id": VendorDAO.get_sample_vendor_id(),
        }