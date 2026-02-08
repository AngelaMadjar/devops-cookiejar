from datetime import datetime, timezone
import pandas as pd

from cookiejar.daos.vendor.vendor_dao import VendorDAO
from cookiejar.daos.vendor.vendor_description_dao import VendorDescriptionDAO
from cookiejar.daos.vendor.vendor_descriptions_dao import VendorDescriptionsDAO

from cookiejar.daos.tracker.tracker_type_dao import TrackerTypeDAO
from cookiejar.daos.tracker.tracker_category_dao import TrackerCategoryDAO
from cookiejar.daos.tracker.tracker_source_dao import TrackerSourceDAO
from cookiejar.daos.tracker.tracking_domain_dao import TrackingDomainDAO
from cookiejar.daos.tracker.tracker_purpose_dao import TrackerPurposeDAO
from cookiejar.daos.tracker.tracker_dao import TrackerDAO
from cookiejar.daos.tracker.tracker_purposes_dao import TrackerPurposesDAO


def now_utc():
    return datetime.now(timezone.utc)


class SeedService:
    @staticmethod
    def populate_from_csv(csv_path: str, source_name: str = "seed_anonymized.csv") -> dict:
        # Read CSV
        data = pd.read_csv(csv_path, sep=";", dtype=str)
        data = data.where(pd.notnull(data), None)  # NaN -> None

        if "Vendor Description" in data.columns:
            data = data.rename(columns={"Vendor Description": "vendor_description"})

        # Distinct lists 
        # DB tableshave UNIQUE constraints, so I first select distinct values for these entities
        distinct_vendors = data["vendor_name"].dropna().unique().tolist()
        distinct_tracker_types = data["tracker_type"].dropna().unique().tolist()
        distinct_tracker_categories = data["consent_category"].dropna().unique().tolist()
        distinct_tracker_purposes = data["tracker_purpose"].dropna().unique().tolist()
        distinct_vendor_descriptions = data["vendor_description"].dropna().unique().tolist()

        # Insert lookups first
        # Tracker entity depends on vendor/type/category/source/domain, so those must exist in the 
        # DB before creating Tracker rows
        VendorDAO.bulk_insert_vendors(distinct_vendors)
        TrackerTypeDAO.bulk_insert_tracker_types(distinct_tracker_types)
        TrackerCategoryDAO.bulk_insert_tracker_categories(distinct_tracker_categories)
        TrackerPurposeDAO.bulk_insert_tracker_purposes(distinct_tracker_purposes)
        VendorDescriptionDAO.bulk_insert_vendor_descriptions(distinct_vendor_descriptions)
        TrackerSourceDAO.bulk_insert_tracker_sources([source_name])

        # Build maps (value -> id)
        # These maps convert the string values from the CSV into foreign-key IDs.
        vendor_map = VendorDAO.get_vendors()
        tracker_type_map = TrackerTypeDAO.get_tracker_types()
        tracker_category_map = TrackerCategoryDAO.get_tracker_categories()
        tracker_purpose_map = TrackerPurposeDAO.get_tracker_purposes()
        vendor_description_map = VendorDescriptionDAO.get_vendor_descriptions()
        tracker_source_map = TrackerSourceDAO.get_tracker_sources()
        tracker_source_id = tracker_source_map[source_name]

        # Insert TrackingDomains 
        # tracking_domain has a unique constraint with vendor_id: (vendor_id, tracking_domain)
        distinct_domains = data[["tracking_domain", "vendor_name"]].drop_duplicates()


        domain_rows = []
        for _, r in distinct_domains.iterrows():
            domain = r["tracking_domain"]
            vendor_name = r["vendor_name"]

            if domain is None:
                continue

            vendor_id = vendor_map.get(vendor_name) if vendor_name is not None else None
            domain_rows.append({
                "tracking_domain": domain,
                "vendor_id": vendor_id
            })

        TrackingDomainDAO.bulk_insert_tracking_domains(domain_rows)
        tracking_domain_map = TrackingDomainDAO.get_tracking_domains()  # (domain, vendor_id) -> id


        # Insert Trackers
        # In order to create tracker_purposes associations, trackers must be created first to retrieve their IDs
        trackers_to_create = []
        for _, r in data.iterrows():
            vendor_name = r["vendor_name"]
            vendor_id = vendor_map.get(vendor_name) if vendor_name is not None else None

            domain = r["tracking_domain"]
            tracking_domain_id = tracking_domain_map.get((domain, vendor_id)) if domain is not None else None

            tracker_type_id = tracker_type_map.get(r["tracker_type"])
            tracker_category_id = tracker_category_map.get(r["consent_category"])

            # Required FKs
            if tracking_domain_id is None or tracker_type_id is None or tracker_category_id is None:
                continue

            trackers_to_create.append({
                "tracker_name": r["tracker_name"],
                "tracker_duration": r.get("tracker_duration"),
                "last_modified": now_utc(),
                "tracker_type_id": tracker_type_id,
                "tracker_category_id": tracker_category_id,
                "tracker_source_id": tracker_source_id,
                "vendor_id": vendor_id,
                "tracking_domain_id": tracking_domain_id,
            })

        TrackerDAO.bulk_insert_trackers(trackers_to_create)


        # Build tracker_id map 
        tracker_id_map = TrackerDAO.get_trackers()  # (name,type_id,domain_id) -> tracker_id

        # Insert TrackerPurposes links
        # Creating *-* relationships requires tracker ids
        tracker_purpose_links = []
        for _, r in data.iterrows():
            vendor_name = r["vendor_name"]
            vendor_id = vendor_map.get(vendor_name) if vendor_name is not None else None

            domain = r["tracking_domain"]
            tracking_domain_id = tracking_domain_map.get((domain, vendor_id)) if domain is not None else None
            tracker_type_id = tracker_type_map.get(r["tracker_type"])

            if tracking_domain_id is None or tracker_type_id is None:
                continue

            tracker_key = (r["tracker_name"], tracker_type_id, tracking_domain_id)
            tracker_id = tracker_id_map.get(tracker_key)

            purpose = r.get("tracker_purpose")
            tracker_purpose_id = tracker_purpose_map.get(purpose) if purpose is not None else None

            if tracker_id is None or tracker_purpose_id is None:
                continue

            tracker_purpose_links.append({
                "tracker_id": tracker_id,
                "tracker_purpose_id": tracker_purpose_id,
                "created_at": now_utc(),
                "is_current": True
            })

        TrackerPurposesDAO.bulk_insert_tracker_purpose_links(tracker_purpose_links)


        # Insert VendorDescriptions links
        vendor_desc_links = []
        for _, r in data.iterrows():
            vendor_name = r["vendor_name"]
            desc = r.get("vendor_description")

            if vendor_name is None or desc is None:
                continue

            vendor_id = vendor_map.get(vendor_name)
            vendor_description_id = vendor_description_map.get(desc)

            if vendor_id is None or vendor_description_id is None:
                continue

            vendor_desc_links.append({
                "vendor_id": vendor_id,
                "vendor_description_id": vendor_description_id,
                "created_at": now_utc(),
                "is_current": True
            })

        VendorDescriptionsDAO.bulk_insert_vendor_description_links(vendor_desc_links)

        return {
            "status": "ok",
            "rows_in_csv": int(len(data)),
            "trackers_attempted": int(len(trackers_to_create)),
            "vendor_desc_links_attempted": int(len(vendor_desc_links)),
            "tracker_purpose_links_attempted": int(len(tracker_purpose_links)),
        }
