import httpx

from ibm_watsonx_ai.foundation_models import get_model_specs
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models.schema import TextChatParameters
from ibm_watsonx_ai.utils.utils import HttpClientConfig
import requests

from fastapi_template.Logger import Logger
from fastapi_template.env import LogConfig
from fastapi_template.connectors.Singleton import Singleton
from fastapi_template.env import WatsonxAPIConfig, WatsonxConfig


class WatsonxAPIClient(metaclass=Singleton):
    def __init__(self, watsonxconfig: WatsonxAPIConfig):
        self.wx_cloud_url = watsonxconfig.url
        self.wx_apikey = watsonxconfig.apikey

        self.credentials = Credentials(
            url=self.wx_cloud_url,
            api_key=self.wx_apikey
        )

        limits = httpx.Limits(
            max_connections=watsonxconfig.limits
        )

        self.client = APIClient(
            self.credentials, httpx_client=HttpClientConfig(limits=limits))


class WatsonxClient(metaclass=Singleton):
    def __init__(self, watsonxconfig: WatsonxConfig, wx_apiconfig: WatsonxAPIConfig):

        self.logger = Logger('watsonx_logger', LogConfig.misc_level).logger

        self.wx_cloud_url = watsonxconfig.url
        self.wx_apikey = watsonxconfig.apikey

        self.client = WatsonxAPIClient(wx_apiconfig).client

        # one of these two is required
        self.project_id = watsonxconfig.project_id
        self.space_id = watsonxconfig.space_id
        self.model_id = watsonxconfig.model_id

        self.deployment_id = watsonxconfig.deployment_id

        model_data = {
            "deployment_id": self.deployment_id,
            "api_client": self.client,
            "validate": False
        }
        if self.project_id:
            model_data['project_id'] = self.project_id
        elif self.space_id:
            model_data['space_id'] = self.space_id
        else:
            raise Exception(
                'Project ID or Space ID required for Watsonx AI model inference')

        self.model = ModelInference(**model_data)
        self.logger.debug("WatsonX Client successfully initialized.")

    def text_generation(self, prompt_query: str = None, params: dict = None, label: str = ""):
        self.logger.debug(
            f"Called text generation")
        response = None
        retry = True
        # retry in case WX dies
        while retry:
            try:
                response = self.model.generate_text(
                    prompt=prompt_query, params=params)
                self.logger.debug(f"generated ok {response}")

                retry = False
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)
        return response

    def text_generation_stream(self, prompt_query: str = None, params: dict = None):
        self.logger.debug(
            f"Called text stream generation")
        response = None
        retry = True
        while retry:
            try:
                response = self.model.generate_text_stream(
                    prompt=prompt_query, params=params)
                self.logger.debug(f"generated ok {response}")
                retry = False
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)
        return response
    
    def vision_request(self, encoded_image: str, user_prompt: str, params: dict = None):
        self.logger.debug(
            f"Called vision request")
        
        # Set up parameters for the model
        params_config = TextChatParameters(**params) if params else TextChatParameters()

        model = ModelInference(
            model_id=self.model_id,
            api_client=self.client,
            project_id=self.project_id,
            params=params_config
        )

        # Prepare the messages
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpg;base64,{encoded_image}",
                    
                        }
                    }
                ]
            }
        ]

        # Generate response
        try:
            response = model.chat(messages=messages)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            self.logger.error(f"Error in vision request: {str(e)}")
            raise

    def tokenize(self, prompt):
        self.logger.debug(f"Tokenizing")
        tokenized_response = self.model.tokenize(prompt=prompt)
        return tokenized_response["result"]["token_count"]

    def list_models(self):
        models_list = get_model_specs(url=self.wx_cloud_url)
        self.logger.debug(f"Available models: {models_list}")
        return models_list

    def get_model_detail(self):
        model_detail = get_model_specs(
            url=self.wx_cloud_url, model_id=self.model_id)
        self.logger.debug(f"Model details: {model_detail}")
        return model_detail
