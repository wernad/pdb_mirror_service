DB_HOST = "172.21.0.3"  # "localhost"
DB_PORT = 5432
DB_NAME = "pdb_mirror"
DB_USER = "admin"
DB_PASSWORD = "admin"

PDB_RSYNC_URL = "rsync://rsync-versioned.pdbj.org/ftp_versioned/data"
PDB_RSYNC_COMMAND = [
    "rsync",
    "--dry-run",
    "--list-only",
    "-r",
    "--include",
    "'*/'",
    "--include",
    " '*.cif.gz'",
    "--exclude",
    "'*'",
]

PDB_HTTP_FILE_AGE = 10  # In days.
PDB_HTTP_TIMEOUT = 5  # Seconds.
PDB_HTTP_VIEW_URL = "https://files-versioned.rcsb.org/pdb_versioned/views/latest/coordinates/mmcif/"

CRON_JOB_DAY = 3  # 0-6 (Mon - Sun).

API_PATH = "/api/v1"
