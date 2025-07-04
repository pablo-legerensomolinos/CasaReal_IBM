from sqlalchemy import create_engine, Connection, text
from sqlalchemy.orm import sessionmaker

from fastapi_template.Logger import Logger
from fastapi_template.connectors.Singleton import Singleton

from fastapi_template.models.LastFilesModel import LastFiles


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

    def getLastFiles(self) -> list[LastFiles]:
        return self.session.query(LastFiles).all()
    
    def execute_sql(self, sql: str) -> list[dict]:
        """
        Executes a raw SQL query and returns the results as a list of dictionaries.
        """
        self.logger.info(f"Executing SQL: {sql}")
        result = self.connection.execute(text(sql))
        return [dict(row) for row in result]
