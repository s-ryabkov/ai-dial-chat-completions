import json
import aiohttp
import requests
from aiohttp import StreamReader

from task.constants import DIAL_ENDPOINT, API_KEY
from task.models.message import Message
from task.models.role import Role


async def _get_content_snippet(stream: StreamReader) -> str:
    contents = []
    async for chunk in stream:
        # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
        if chunk.startswith(b"data: "):
            chunk_data = chunk[len(b"data: "):].decode("utf-8").strip()
            if chunk_data == "[DONE]":
                break
            #    chunks, collect them and return as assistant message
            json_response = json.loads(chunk_data)
            delta = json_response["choices"][0]["delta"]
            if "content" in delta:
                contents.append(delta["content"])
    return "".join(contents)


class DialClient:
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        super().__init__()
        self._api_key = API_KEY
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        
        # 2. Create request_data dictionary with messages
        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }
        
        # 3. Make POST request
        response = requests.post(
            self._endpoint,
            headers=headers,
            json=request_data
        )
        
        # 5. Check status code and raise exception if not 200
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        # 4. Get content from response, print it and return message with assistant role
        content = response.json()["choices"][0]["message"]["content"]
        print(content)
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }

        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        request_data = {
            "messages": [msg.to_dict() for msg in messages],
            "stream": True,
        }

        # 3. Create empty list called 'contents' to store content snippets
        content = None
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        async with aiohttp.ClientSession() as session:
            # 5. Inside session, make POST request using session.post() with:
            #    - URL: self._endpoint
            #    - json: request_data from step 2
            #    - headers: headers from step 1
            #    - Use 'async with' context manager for response
            async with session.post(self._endpoint, json=request_data, headers=headers) as response:
                content = await _get_content_snippet(response.content)

        return Message(role=Role.AI, content=content)

