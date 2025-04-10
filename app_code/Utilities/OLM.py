import urllib.parse
import requests
import urllib
import typing as t

import app_code.config as C
class OLM:
    '''
    This is the ollama utility.
    It makes doing requests with ollama simpler and easier
    '''
    complete_ollama_api_url = C.complete_ollama_api_url

    @classmethod
    def get_model_names_list(cls) -> t.List[str]:
        '''
        This function returns a list of model names available in ollama
        '''
        list_api_endpoint = "api/tags"
        list_api_url = urllib.parse.urljoin(cls.complete_ollama_api_url, list_api_endpoint)
        response = requests.get(list_api_url)
        result = cls.get_response_dict(response)
        models_info = result["models"]
        model_names_list = [info["name"] for info in models_info]
        return model_names_list


    @classmethod
    def get_version(cls) -> t.Any:
        '''
        This function gets the status from the API of the running ollama instance
        '''
        status_url = urllib.parse.urljoin(cls.complete_ollama_api_url, "api/version")
        response = requests.get(status_url)
        return cls.get_response_dict(response)



    @classmethod
    def get_response_dict(cls, response: requests.Response) -> t.Any:
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"ERROR: Unable to check to get response! (Status Code: {response.status_code})")


        