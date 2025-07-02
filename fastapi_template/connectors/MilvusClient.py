from pymilvus import MilvusClient as MC
from pymilvus import AnnSearchRequest, CollectionSchema
from pymilvus import WeightedRanker, RRFRanker

from fastapi_template.Logger import Logger
from fastapi_template.env import LogConfig
from fastapi_template.connectors.Singleton import Singleton
from fastapi_template.connectors.EmbeddingsClient import EmbeddingClient

from fastapi_template.env import MilvusConfig, EmbeddingsConfig, WatsonxAPIConfig


class MilvusClient(metaclass=Singleton):
    def __init__(self, config: MilvusConfig, embeddingsconfig: EmbeddingsConfig, wx_apiconfig: WatsonxAPIConfig):

        self.logger = Logger('milvus_logger', LogConfig.misc_level).logger
        self.client = MC(
            uri=config.uri,
            token=f"{config.user}:{config.password}",
            db_name=config.db_name
        )
        self.logger.debug("Milvus Client successfully initialized.")
        self.embeddings = EmbeddingClient(
            embeddingsconfig=embeddingsconfig, wx_apiconfig=wx_apiconfig)
        self.sparse_embedding_function = None

    def create_collection(self, collection_name: str, schema: CollectionSchema = None, **kwargs) -> None:
        if not self.client.has_collection(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                schema=schema,
                kwargs=kwargs
            )
            self.logger.debug(f"Collection {collection_name} created")
        else:
            self.logger.warning(f"Collection {collection_name} already exist")

    def delete_collection(self, collection_name: str) -> None:
        self.client.drop_collection(collection_name)
        self.logger.debug(f"Collection {collection_name} deleted")

    def list_collections(self) -> list[str]:
        return self.client.list_collections()
    
    def flush_collection(self, collection_name: str) -> None:
        self.client.flush(collection_name=collection_name)

    # TODO: create index from index_params

    def build_index(self, collection_name: str, index_type: str, field_name: str, metric_type: str) -> None:
        self.logger.debug(f"Building collection index for {collection_name}")

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name=field_name,
            metric_type=metric_type,
            index_type=index_type
        )

        self.client.create_index(
            collection_name=collection_name, index_params=index_params)

        self.logger.debug(f"Built collection index for {collection_name}")

    # TODO: load collection before query

    def insert_data(self, documents: dict | list[dict], collection_name: str) -> None:
        insertion = self.client.insert(
            collection_name=collection_name, data=documents)
        self.logger.debug(
            f"Inserted {len(documents) if type(documents) == list else 1}"
            f" document/s on collection {collection_name}"
        )
        return (insertion)
    
    def upsert(self, collection_name: str, documents: dict | list[dict]) -> None:
        self.client.upsert(collection_name=collection_name, data=documents)

    def query(self, collection_name: str, filter: str = None, limit: int = 10, output_fields: list[str] = ["*"]) -> list[dict]:
        return self.client.query(collection_name=collection_name, filter=filter, limit=limit, output_fields=output_fields)
    
    def lexical_search(self, query: str, collection_name: str, output_fields: list[str], anns_field: str, limit=10, **kwargs) -> list[dict]:
        self.logger.debug(f"Lexical searching in collection {collection_name}")

        filter_expression = kwargs.get("filter", "")

        search_params = {
            "metric_type": "BM25",
        }

        res = self.client.search(
            collection_name=collection_name,
            data=[query],
            filter=filter_expression,
            anns_field=anns_field,
            output_fields=output_fields,
            limit=limit,
            search_params=search_params
        )
        return res

    def semantic_search(self, collection_name: str, query: str, output_fields: list[str], anns_field: str, limit=10, **kwargs) -> list[dict]:
        self.logger.debug(
            f"Semantic searching in collection {collection_name}")

        filter_expression = kwargs.get("filter", "")
        search_params = {
            "metric_type": "IP",
        }

        dense_vector_query = self.get_embeddings(query=query)

        res = self.client.search(
            collection_name=collection_name,
            data=[dense_vector_query],
            filter=filter_expression,
            anns_field=anns_field,
            output_fields=output_fields,
            limit=limit,
            search_params=search_params
        )
        return res

    def hybrid_search(
        self, query: str, collection_name: str, dense_field: str = "vector_dense", sparse_field: str = "vector_sparse",
        output_fields: list[str] = ["text"], sparse_weight=1.0, dense_weight=1.0, limit=10, drop_ratio_build=0.0, ranker_type="weighted",  **kwargs
    ) -> list[dict]:

        filter_expression = kwargs.get("filter", "")

        self.logger.debug(f"Hybrid searching in collection {collection_name}")

        query_dense_embedding = self.embeddings.get_dense_embeddings(query)

        dense_search_params = {
            "metric_type": "IP",
        }
        dense_req = AnnSearchRequest(
            data=[query_dense_embedding],
            expr=filter_expression,
            anns_field=dense_field,
            param=dense_search_params,
            limit=limit
        )

        sparse_search_params = {
            "metric_type": "BM25"
        }
        sparse_req = AnnSearchRequest(
            data=[query],
            expr=filter_expression,
            anns_field=sparse_field,
            param=sparse_search_params,
            limit=limit
        )

        # Selección del ranker según el parámetro de entrada
        if ranker_type.lower() == "rrf":
            rerank = RRFRanker()
        else:
            rerank = WeightedRanker(sparse_weight, dense_weight)

        res = self.client.hybrid_search(  # TODO: comprobar si hybrid_search admite filter
            collection_name=collection_name,
            reqs=[dense_req, sparse_req],
            ranker=rerank,
            limit=limit,
            output_fields=output_fields
        )[0]

        return res

    def get_embeddings(self, query) -> tuple[any, any]:
        dense = self.embeddings.get_dense_embeddings(query)
        return dense
