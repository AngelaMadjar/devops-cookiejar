from cookiejar.daos.tracker.tracker_purposes_dao import TrackerPurposesDAO
from cookiejar.daos.vendor.vendor_descriptions_dao import VendorDescriptionsDAO

from cookiejar.daos.tracker.tracker_dao import TrackerDAO
from cookiejar.daos.tracker.tracking_domain_dao import TrackingDomainDAO

from cookiejar.daos.tracker.tracker_purpose_dao import TrackerPurposeDAO
from cookiejar.daos.tracker.tracker_type_dao import TrackerTypeDAO
from cookiejar.daos.tracker.tracker_category_dao import TrackerCategoryDAO
from cookiejar.daos.tracker.tracker_source_dao import TrackerSourceDAO

from cookiejar.daos.vendor.vendor_description_dao import VendorDescriptionDAO
from cookiejar.daos.vendor.vendor_dao import VendorDAO


class CleanupService:
    """
    Deletes rows from all tables in a safe order (children first, then parents)
    to avoid Foreign Key constraint errors.
    """

    @staticmethod
    def empty_all():
        # Association tables first (*-* tables)
        TrackerPurposesDAO.delete_all()
        VendorDescriptionsDAO.delete_all()

        # Main tables that depend on lookups
        TrackerDAO.delete_all()
        TrackingDomainDAO.delete_all()

        # Lookup tables for tracker side
        TrackerPurposeDAO.delete_all()
        TrackerTypeDAO.delete_all()
        TrackerCategoryDAO.delete_all()
        TrackerSourceDAO.delete_all()

        # Lookup tables for vendor side
        VendorDescriptionDAO.delete_all()
        VendorDAO.delete_all()

    @staticmethod
    def empty_trackers_only():
        TrackerPurposesDAO.delete_all()
        TrackerDAO.delete_all()

    @staticmethod
    def empty_vendors_only():
        VendorDescriptionsDAO.delete_all()
        VendorDescriptionDAO.delete_all()
        VendorDAO.delete_all()
