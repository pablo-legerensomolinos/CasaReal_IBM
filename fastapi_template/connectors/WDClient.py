"""
Created on Fri Jan  5 13:25:44 2024
@author: mariariosdelgado
"""

import ast
from ibm_watson import DiscoveryV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from fastapi_template.Logger import Logger
from fastapi_template.connectors.Singleton import Singleton


class WDClient(metaclass=Singleton):
    def __init__(self, wd_config):

        self.apikey = wd_config.wd_apikey
        self.version = wd_config.wd_version
        self.project_id = wd_config.wd_project_id
        self.url = wd_config.wd_url

        authenticator = IAMAuthenticator(self.apikey)
        self.discovery = DiscoveryV2(
            version=self.version, authenticator=authenticator)

        self.discovery.set_service_url(self.url)

        # self.discovery.set_disable_ssl_verification(True)

    def list_projects(self):
        return self.discovery.list_projects()

    def search(self, query: str, limit: int):

        results_nlq = self.discovery.query(
            project_id=self.project_id,
            natural_language_query=query , 
            # passages: 'QueryLargePassages' = True,
            # find_answers
            # count = limit
        ).get_result()
        return results_nlq

    def format_results(self, results):

        dic_results = []

        for element in results['results']:
            if 'text' in element.keys():
                text = (element['text'])
            if 'metadata' in element.keys():
                metadata = (element['metadata'])
                if "contract_id" in metadata:
                    contract_id = metadata["contract_id"]
                if "file_id" in metadata:
                    file_id = metadata["file_id"]
            if 'result_metadata' in element.keys():
                result_metadata = (element['result_metadata'])
            if 'document_passages' in element.keys():
                document_passages = (element['document_passages'])

            dic_results.append({"contract_id": contract_id,
                                "file_id": file_id,
                                "document_passages": document_passages,
                                #"text": text,
                                #"metadata": metadata,
                                "result_metadata": result_metadata})

        return dic_results


    # search_results_dict ={query1:{doc1:score1,doc2:score2,...},query2:{doc1:score1,doc2:score2,...}}
    def search_results_dict(self, query:str, limit:int):
        results = self.search(query, limit)
        dic = {}
        dic_text = {}
        cont = 0
        for element in results['results']:
            if 'subtitle' in element.keys():
                title = element['subtitle']
                score = element['result_metadata']['confidence']
                dic[title] = score
            else:
                title = 'notitle' + str(cont)
            if 'text' in element.keys():
                text = (element['text'])
            else:
                text = ((''))
            # diccionario = ast.literal_eval(string)
            if 'text_mappings' in element['extracted_metadata'].keys():
                dic_pagenumber = ast.literal_eval(
                    element['extracted_metadata']['text_mappings'])
                pagenumber = dic_pagenumber['text_mappings'][0]['page']['page_number']
            else:
                pagenumber = ' '
            metadata = {'title': title, 'filename': element['extracted_metadata']
                        ['filename'], 'page_number': pagenumber, 'extracted': text}
            dic_text[title] = metadata

            cont += 1
        return (dic, dic_text)