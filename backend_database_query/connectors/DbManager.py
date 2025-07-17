from sqlalchemy import create_engine, Connection, text
from sqlalchemy.orm import sessionmaker

from backend_database_query.Logger import Logger
from backend_database_query.connectors.Singleton import Singleton

from backend_database_query.models.LastFilesModel import LastFiles
from base64 import b64encode


class DatabaseManager(metaclass=Singleton):
    def __init__(self, db2config):
        """
        Initializes the DatabaseManager object with connection details.
        """
        self.logger = Logger('app_logger').logger
        self.local_logger = Logger('db_manager').logger
        self.connection_string = (
            f"db2://{db2config.username}:{db2config.password}"
            f"@{db2config.hostname}:{db2config.port}/{db2config.database}?"
            f"CurrentSchema={db2config.schema};"
            f"SSLServerCertificate={db2config.ssl_server_certificate};"
            f"Security={db2config.security}"
        )
        self.schema = db2config.schema
        self.connection: Connection = None
        self.session: sessionmaker = None
        self.connect()
        self.logger.info("DB Client successfully initialized.")

    def connect(self) -> Connection:
        """
        Connects to the DB2 database.
        """
        if self.connection is None:
            self.logger.info("Connecting to database...")
            self.engine = create_engine(self.connection_string)
            self.connection = self.engine.connect()
            self.session = sessionmaker(bind=self.engine)()
            self.logger.info("Database connection established.")
            self.local_logger.info('other stuff')
        else:
            self.logger.info("Already connected to the database.")
    
    def test_connection(self):
        """
        Executes a simple query to test the DB2 connection.
        Returns the current date from the database.
        """
        self.logger.info("Testing DB2 connection with SELECT CURRENT DATE")
        result = self.connection.execute(text("SELECT CURRENT DATE AS today FROM SYSIBM.SYSDUMMY1"))
        # Use _mapping to get a dict
        return [dict(row._mapping) for row in result]

    def getLastFiles(self) -> list[LastFiles]:
        return self.session.query(LastFiles).all()
    
    def execute_sql(self, sql: str) -> list[dict]:
        """
        Executes a raw SQL query and returns the results as a list of dictionaries.
        """
        self.logger.info(f"Executing SQL: {sql}")
        with self.connection.execute(text(sql)) as result:
            def jsonable(row):
                # RowMapping → plain dict
                d = dict(row)            # ✔ mapping to dict
                # make binary columns JSON-safe
                for k, v in d.items():
                    if isinstance(v, (bytes, bytearray, memoryview)):
                        d[k] = b64encode(v).decode()
                return d

            return [jsonable(r) for r in result.mappings()]

    def execute_raw_sql(self, sql: str) -> list[dict]:
        """
        Executes a raw SQL query and returns the results as a list of dictionaries, limited to 50 rows.
        """
        self.logger.info(f"Executing SQL: {sql}")
        result = self.connection.execute(text(sql))
        # Limit to 50 rows
        return [row._mapping for idx, row in enumerate(result) if idx < 50]
