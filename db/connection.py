# File: db/connection.py
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

# Automatically fetch CLOBs as strings to avoid validation issues in agents
oracledb.defaults.fetch_lobs = False

def get_connection(timeout=None):
    """
    Establishes a connection to the Oracle Database.
    If `timeout` (seconds) is provided, the connect attempt will be given that
    many seconds to succeed; otherwise a TimeoutError is raised and caller can
    fallback to an alternative DB for development.
    """
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN", "reconcilationdb_high")
    wallet_location = os.getenv("ORACLE_WALLET_LOCATION", "wallet")
    wallet_password = os.getenv("ORACLE_WALLET_PASSWORD")

    def _connect(q):
        try:
            conn = oracledb.connect(
                user=user,
                password=password,
                dsn=dsn,
                config_dir=wallet_location,
                wallet_location=wallet_location,
                wallet_password=wallet_password
            )
            q.append((True, conn))
        except Exception as e:
            q.append((False, e))

    if timeout is None:
        return oracledb.connect(
            user=user,
            password=password,
            dsn=dsn,
            config_dir=wallet_location,
            wallet_location=wallet_location,
            wallet_password=wallet_password
        )

    # Run connect in a thread so we can implement a simple timeout
    import threading
    q = []
    t = threading.Thread(target=_connect, args=(q,))
    t.daemon = True
    t.start()
    t.join(timeout)
    if not q:
        raise TimeoutError(f"Oracle connect did not complete within {timeout} seconds")
    ok, val = q[0]
    if not ok:
        raise val
    return val

def execute_query(query, params=None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

def execute_statement(statement, params=None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(statement, params)
            else:
                cursor.execute(statement)
            conn.commit()
