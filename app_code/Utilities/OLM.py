import urllib.parse
import requests
import urllib
import typing as t

import config as C
class OLM:
    '''
    This is the ollama utility.
    It makes doing requests with ollama simpler and easier
    '''
    complete_ollama_api_url = C.complete_ollama_api_url
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


        