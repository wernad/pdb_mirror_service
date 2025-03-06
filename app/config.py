DB_HOST = "172.21.0.3"  # "localhost"
DB_PORT = 5432
DB_NAME = "pdb_mirror"
DB_USER = "admin"
DB_PASSWORD = "admin"


PDB_DATA_API_URL = "https://data.rcsb.org/graphql"
PDB_SEARCH_API_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
PDB_SEARCH_API_LIMIT = 1000
PDB_FTP_STATUS_URL = "https://files.rcsb.org/pub/pdb/data/status/"

PDB_HTTP_TIMEOUT = 5  # Seconds.
PDB_HTTP_FILE_URL = "https://files-versioned.wwpdb.org/pdb_versioned/views/all/coordinates/mmcif/"


WORKER_LIMIT = 100
CRON_JOB_DAY = 3  # 0-6 (Mon - Sun).

API_PATH = "/api/v1"
