from sqlalchemy.dialects.postgresql import insert
from cookiejar import db
from cookiejar.models.tracker.tracking_domain import TrackingDomain


class TrackingDomainDAO:
    @staticmethod
    def bulk_insert_tracking_domains(domains: list[dict]):
        """
        domains example:
        [
          {"tracking_domain": "example.com", "vendor_id": 1}
        ]
        """
        # keep only rows that have a domain value
        rows = [d for d in domains if d.get("tracking_domain") is not None]
        if not rows:
            return

        query = insert(TrackingDomain).values(rows).on_conflict_do_nothing(
            index_elements=["vendor_id", "tracking_domain"]  # unique constraint
        )
        db.session.execute(query)
        db.session.commit()

    @staticmethod
    def get_tracking_domains():
        """
        Returns mapping keyed by (tracking_domain, vendor_id) -> tracking_domain_id
        """
        return {
            (d.tracking_domain, d.vendor_id): d.tracking_domain_id
            for d in TrackingDomain.query.all()
        }

    @staticmethod
    def delete_all():
        TrackingDomain.query.delete(synchronize_session=False)
        db.session.commit()