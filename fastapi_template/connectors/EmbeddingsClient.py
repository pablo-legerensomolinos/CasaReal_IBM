from langchain_ibm import WatsonxEmbeddings
from fastapi_template.connectors.Singleton import Singleton
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams

from fastapi_template.connectors.WatsonxClient import WatsonxAPIClient
from fastapi_template.env import EmbeddingsConfig


class EmbeddingClient(metaclass=Singleton):

    def __init__(self, embeddingsconfig: EmbeddingsConfig):
        self.client = WatsonxAPIClient(embeddingsconfig).client
        self.project_id = embeddingsconfig.project_id
        self.dense_embeding = embeddingsconfig.dense_embedding_id

    def get_dense_embeddings(self, text_contents):
        embed_params = {
            EmbedParams.TRUNCATE_INPUT_TOKENS: 512,
            EmbedParams.RETURN_OPTIONS: {
                'input_text': True
            }
        }

        embedding = WatsonxEmbeddings(
            model_id=self.dense_embeding,
            project_id=self.project_id,
            params=embed_params,
            verify=True,
            watsonx_client=self.client
        )
        embedding_vectors = embedding.embed_documents(
            texts=[text_contents])
        return embedding_vectors
