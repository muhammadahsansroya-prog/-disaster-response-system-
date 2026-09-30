import pymysql
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

pymysql.install_as_MySQLdb()

# MariaDB Version check bypass
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# MariaDB 10.4 RETURNING clause syntax error bypass
DatabaseFeatures.can_return_columns_from_insert = False