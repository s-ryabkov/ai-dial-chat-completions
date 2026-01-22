from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        #TODO:
        # Documentation: https://pypi.org/project/aidial-client/ (here you can find how to create and use these clients)
        # 1. Create Dial client
        self.dial = Dial(api_key=self._api_key, base_url=DIAL_ENDPOINT)
        # 2. Create AsyncDial client
        self.async_dial = AsyncDial(api_key=self._api_key, base_url=DIAL_ENDPOINT)

    def get_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # 1. Create chat completions with client
        #    Hint: to unpack messages you can use the `to_dict()` method from Message object
        msgs = [message.to_dict() for message in messages]
        response = self.dial.chat.completions.create(messages=msgs, stream=False, deployment_name=self._deployment_name)
        # 2. Get content from response, print it and return message with assistant role and content
        # 3. If choices are not present then raise Exception("No choices in response found")
        if response.choices is None or len(response.choices) == 0:
            raise Exception("No choices in response found")

        content = response.choices[0].message.content
        message = Message(role=Role.AI, content=content)
        return message
 
        

    async def stream_completion(self, messages: list[Message]) -> Message:
        #TODO:
        # 1. Create chat completions with async client
        #    Hint: don't forget to add `stream=True` in call.
        msgs = [message.to_dict() for message in messages]
        response = await self.async_dial.chat.completions.create(messages=msgs, stream=True, deployment_name=self._deployment_name)
        # 2. Create array with `contents` name (here we will collect all content chunks)
        contents = []
        # 3. Make async loop from `chunks` (from 1st step)
        # 4. Print content chunk and collect it contents array
        async for chunk in response:
            if hasattr(chunk, "choices"):
                if chunk.choices[0]:
                    content = chunk.choices[0].delta.content
                    if content is not None:
                        contents.append(content)
                        print(chunk)
            else:
                # For backward compatibility or debugging
                print(chunk)

        # 5. Print empty row `print()` (it will represent the end of streaming and in console we will print input from a new line)
        print()
        # 6. Return Message with assistant role and message collected content
        return Message(role=Role.AI, content="".join(contents))
