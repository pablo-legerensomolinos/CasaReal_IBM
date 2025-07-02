from os import getcwd

from elasticsearch import Elasticsearch, helpers

from fastapi_template.Logger import Logger
from fastapi_template.env import LogConfig
from fastapi_template.connectors.Singleton import Singleton


class ElasticSearchClient(metaclass=Singleton):
    def __init__(self, elasticconfig):
        sslConfig = {}
        if elasticconfig.cert_path != "":
            sslConfig = {
                "ca_certs": f"{elasticconfig.cert_path}",
            }
        else:
            sslConfig = {
                "verify_certs": False,
            }

        self.logger = Logger('elasticsearch_logger',
                             LogConfig.misc_level).logger
        self.client = Elasticsearch(
            hosts=elasticconfig.url,
            basic_auth=[
                elasticconfig.user,
                elasticconfig.passwd
            ],
            **sslConfig
        )

        self.index = elasticconfig.index
        self.logger.debug("ElasticSearch Client successfully initialized.")

    def insert(self, document: dict, doc_id: str = None, index: str = None, refresh: bool = False):
        return self.client.index(
            index=(index if index != None else self.index),
            document=document,
            id=doc_id,
            refresh=refresh
        )

    def bulk_insert(self, documents: list[dict], index: str = None, refresh: bool = False, batch_size: int = 10000):
        index = index if index is not None else self.index

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            actions = [
                {
                    "_index": index,
                    # Use provided ID or let ES generate one
                    "_id": doc.get("id", None),
                    "_source": doc
                }
                for doc in batch
            ]
            helpers.bulk(self.client, actions, refresh=refresh)
        return {"status": "Bulk insert completed"}

    def bulk_update(self, documents: list[dict], index: str = None, refresh: bool = False, batch_size: int = 10000):
        index = index if index is not None else self.index

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            actions = []

            for doc in batch:
                doc_id = doc.get("id")  # Ensure there's an ID
                if doc_id:
                    actions.append({
                        "_op_type": "update",
                        "_index": index,
                        "_id": doc_id,
                        "doc": doc  # Partial update
                    })
                else:
                    # Log missing IDs
                    print(f"Skipping document without ID: {doc}")

            if actions:  # Ensure we have valid actions before sending
                helpers.bulk(self.client, actions, refresh=refresh)

        return {"status": "Bulk update completed"}

    def upsert(self, doc_id: str, document: dict, index: str = None, refresh: bool = False):
        return self.client.update(
            index=(index if index != None else self.index),
            id=doc_id,
            doc=document,
            refresh=refresh
        )

    def delete(self, query: dict, index: str = None, refresh: bool = False):
        return self.client.delete_by_query(
            index=(index if index != None else self.index),
            query=query,
            refresh=refresh
        )

    def search(
            self,
            query: dict = None,
            knn: dict = None,
            rank: dict = None,
            source: list[str] = ["*"],
            size: int = 100,
            index: str = None,
            from_: int = 0
    ):
        default_query_all = {
            "query_string": {
                "query": "*"
            }
        }
        return self.client.search(
            index=(index if index != None else self.index),
            query=(query if query != None else default_query_all),
            knn=knn,
            rank=rank,
            source=source,
            size=size, from_=from_
        )

    def search_after(
        self,
        sort: dict,
        query: dict = None,
        knn: dict = None,
        rank: dict = None,
        source: list[str] = ["*"],
        search_after: list[any] | None = None,
        index: str = None,
    ):
        default_query_all = {
            "query_string": {
                "query": "*"
            }
        }
        return self.client.search(
            index=(index if index != None else self.index),
            query=(query if query != None else default_query_all),
            knn=knn,
            rank=rank,
            sort=sort,
            search_after=search_after,
            source=source,
        )

    def count_documents(self, query: dict, index: str = None):
        return self.client.count(
            index=(index if index != None else self.index),
            query=query
        )

    def flush(self):
        self.client.indices.flush(index=self.index)

    @staticmethod
    def clean_results(results):
        hits = results["hits"]["hits"]
        cleaned = []
        for hit in hits:
            cleaned.append(hit["_source"] | {"_id": hit["_id"]})

        return cleaned

    @staticmethod
    def clean_results_id(results):
        hits = results["hits"]["hits"]
        cleaned = []
        for hit in hits:
            cleaned.append(hit["_source"] | {
                           "id": hit["_id"], "score": hit["_score"]})

        return cleaned

    @staticmethod
    def get_search_after(results) -> list[any]:
        last = results["hits"]["hits"][-1]
        return last['sort']

    def get_indices(self):
        indices = self.client.indices.get_alias(index="*")
        return list(indices.keys())

    def get_mapping(self, index):
        mapping = self.client.indices.get_mapping(index=index)
        return mapping

    def get_ml_models(self):
        """
        Lists all available machine learning models in Elasticsearch
        Returns the raw response from Elasticsearch containing model information
        """
        try:
            return self.client.ml.get_trained_models()
        except Exception as e:
            self.logger.error(f"Error getting ML models: {e}")

            return None
