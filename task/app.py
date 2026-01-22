import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role
import pprint


async def start(stream: bool, custom_client: bool) -> None:
    #TODO:
    # 1.1. Create DialClient 
    # (you can get available deployment_name via https://ai-proxy.lab.epam.com/openai/models
    #  you can import Postman collection to make a request, file in the project root `dial-basics.postman_collection.json`
    #  don't forget to add your API_KEY)
    deployment_name = "gpt-4o-mini-2024-07-18"
    dial_client = DialClient(deployment_name)

    # 1.2. Create CustomDialClient
    custom_dial_client = CustomDialClient(deployment_name)
    # 2. Create Conversation object
    conversation = Conversation()
    # 3. Get System prompt from console or use default -> constants.DEFAULT_SYSTEM_PROMPT and add to conversation
    #    messages.
    system_prompt = input("System prompt: ")
    if system_prompt == "":
        system_prompt = DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=system_prompt))

    # 4. Use infinite cycle (while True) and get user message from console
    while True:
        user_message = input("User: ")
    # 5. If user message is `exit` then stop the loop
        if user_message == "exit":
            break
    # 6. Add user message to conversation history (role 'user')
        conversation.add_message(Message(role=Role.USER, content=user_message))
    # 7. If `stream` param is true -> call DialClient#stream_completion()
    #    else -> call DialClient#get_completion()
        if custom_client:
            if stream:
                response = await custom_dial_client.stream_completion(conversation.get_messages())
            else:
                response = custom_dial_client.get_completion(conversation.get_messages())
        else:
            if stream:
                response = await dial_client.stream_completion(conversation.get_messages())
            else:
                response = dial_client.get_completion(conversation.get_messages())
        # 8. Add generated message to history
        conversation.add_message(Message(role=Role.AI, content=response.content))
        # 9. Print response content
        print("AI: ", response.content)


    pp = pprint.PrettyPrinter(indent=1)
    print("END OF THE CONVERSATION")
    pp.pprint(conversation.get_messages())
    # 9. Test it with DialClient and CustomDialClient
    # 10. In CustomDialClient add print of whole request and response to see what you send and what you get in response


asyncio.run(
    start(stream=True, custom_client=True)
)
