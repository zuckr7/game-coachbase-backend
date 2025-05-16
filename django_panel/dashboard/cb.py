from couchbase.options import ClusterOptions
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from django.conf import settings

class CB:
    cluster = Cluster(
        settings.DB_HOST,
        ClusterOptions(PasswordAuthenticator(
            settings.USERNAME,
            settings.PASSWORD
        ))
    )
    users_bucket  = cluster.bucket(settings.BUCKET_NAME)
    users_col     = users_bucket.default_collection()
    levels_bucket = cluster.bucket(settings.LEVELS_BUCKET)
    levels_col    = levels_bucket.default_collection()
