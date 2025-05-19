"""Configuration module for the PDB Mirror application.

This module contains all configuration variables used throughout the application,
including database connection details, API endpoints, and application settings.
"""

# Database configuration
DB_HOST = "172.21.0.3"  # "localhost"
DB_PORT = 5432
DB_NAME = "pdb_mirror"
DB_USER = "admin"
DB_PASSWORD = "admin"

# API configuration
API_PATH = "/api/v1"

# PDB API endpoints and settings
PDB_DATA_API_URL = "https://data.rcsb.org/graphql"
PDB_SEARCH_API_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
PDB_SEARCH_API_LIMIT = 1000  # Maximum number of results per search query
PDB_FTP_STATUS_URL = "https://files.rcsb.org/pub/pdb/data/status/"

# HTTP settings
PDB_HTTP_TIMEOUT = 5  # Seconds
PDB_HTTP_FILE_URL = (
    "https://files-versioned.wwpdb.org/pdb_versioned/views/all/coordinates/mmcif/"
)

# Application settings
WORKER_LIMIT = 100  # Maximum number of concurrent workers
CRON_JOB_DAY = 3  # 0-6 (Mon - Sun)
