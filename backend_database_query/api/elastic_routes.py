from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from typing import Optional
import traceback

from backend_database_query.Logger import Logger
from backend_database_query.connectors.ElasticSearch import ElasticSearchClient
from backend_database_query.env import ElasticConfig

logger = Logger("api_logger").logger
elastic_bp = APIRouter(prefix='/api/elastic', tags=['ElasticSearch'])


class SearchSimilarsBody(BaseModel):
    query: str = Field(description="Query to search documents related to it")
    params: Optional[dict] = Field(
        description="Optional additional parameters to narrow the search", default=dict())
    augment_user_query: Optional[bool] = Field(
        description="Optional boolean to augment the search", default=False)


class SearchSimilarsResponse(BaseModel):
    todo: str = Field(description="TO-DO")


@elastic_bp.post('/search-similar-documents',
                 summary="Search in Elastic",
                 description="Get data from Elasticsearch"
                 )
def search_similar_documents(body: SearchSimilarsBody):
    logger.info(f"Received request: {body}")
    elastic_client = ElasticSearchClient(ElasticConfig)

    try:
        results = elastic_client.search(
            query=body.query,
            augment_user_query=body.augment_user_query,
            metadata_filters=body.params
        )
    except Exception as e:
        logger.error(f"Error running retrieval pipeline: {e}")
        error_traceback = traceback.format_exc()
        logger.error(f"Traceback: {error_traceback}")
        return {"error": "Internal server error"}

    cleaned_results = ElasticSearchClient.clean_results(results)
    logger.info(f"Found {len(cleaned_results)} matching results")

    return cleaned_results
