from datetime import datetime, timedelta, timezone
from sklearn.cluster import DBSCAN
import numpy as np
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from db import get_db
from api.models import Hotspot, Cluster


def compute_clusters(db: Session):
    """
    Compute DBSCAN clustering for hotspots within the last 48 hours.
    Updates hotspot.cluster_id in the database.

    Args:
        db (Session): SQLAlchemy session.

    Returns:
        int: Number of clusters created.
    """

    # Get hotspots in time window
    hotspots = (
        db.query(Hotspot)
        .filter(
            Hotspot.sensing_time >= datetime.now(timezone.utc) - timedelta(hours=48)
        )
        .all()
    )

    if not hotspots:
        return 0

    # Extract coordinates
    coords = [(to_shape(h.geometry).y, to_shape(h.geometry).x) for h in hotspots]
    coords_rad = np.radians(coords)

    # Haversine distance
    kms_per_radian = 6371.0088
    epsilon = 5 / kms_per_radian  # 5 km radius

    model = DBSCAN(eps=epsilon, min_samples=3, metric="haversine").fit(coords_rad)
    labels = model.labels_
    labels = [int(l) for l in labels]
    for cid in set(labels):
        if cid == -1:
            continue
        if not db.query(Cluster).filter(Cluster.id == cid).first():
            db.add(Cluster(id=int(cid)))  # <-- s'assurer que c'est int natif
    cluster_count = len(set([l for l in labels if l != -1]))

    # Assign cluster ids
    for hotspot, cid in zip(hotspots, labels):
        if cid != -1:
            hotspot.cluster_id = int(cid)

    db.commit()
    return cluster_count


if __name__ == "__main__":
    session = next(get_db())  # get a live DB session
    clusters = compute_clusters(session)
