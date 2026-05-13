"""Use PyMySQL as the MySQLdb implementation (Windows-friendly)."""
try:
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:  # pragma: no cover
    pass
