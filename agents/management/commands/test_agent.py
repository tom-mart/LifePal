import time
import requests
from django.core.management.base import BaseCommand
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
import os

class Command(BaseCommand):
    help = 'Run test agent to interact with chatbot API'

    def add_arguments(self, parser):
        parser.add_argument('--turns', type=int, default=15, help='Number of conversation turns')
        parser.add_argument('--username', type=str, default='TestUser', help='Username for authentication')
        parser.add_argument('--password', type=str, default='Strong#Pass1', help='Password for authentication')
        parser.add_argument('--agent-id', type=int, default=1, help='Agent ID to chat with')

    def handle(self, *args, **options):
        API_BASE_URL = "http://192.168.1.229:8080/api"
        USERNAME = options['username']
        PASSWORD = options['password']
        AGENT_ID = options['agent_id']
        NUM_TURNS = options['turns']

        # Create Test User AI Agent
        ollama_model = OpenAIChatModel(
            model_name="gemma3:latest",
            provider=OllamaProvider(base_url=os.environ.get("OLLAMA_BASE_URL")),
        )

        test_user_agent = Agent(
            ollama_model,
            system_prompt="""You are a realistic user testing a chatbot. Your goal is to have natural, coherent conversations.

Guidelines:
- Start with greetings or simple questions
- Ask follow-up questions based on the chatbot's responses
- Reference information from earlier in the conversation
- Occasionally introduce new topics naturally
- Show curiosity and engagement
- Keep messages conversational and brief (1-3 sentences)
- Act like a real human user would"""
        )

        test_user_messages = []

        def get_access_token():
            response = requests.post(
                f"{API_BASE_URL}/token/pair",
                json={"username": USERNAME, "password": PASSWORD}
            )
            response.raise_for_status()
            data = response.json()
            self.stdout.write(self.style.SUCCESS(f"✓ Authenticated as {data['username']}"))
            return data["access"]

        def chat_with_api(message, access_token, conversation_id=None):
            headers = {"Authorization": f"Bearer {access_token}"}
            payload = {"message": message, "agent_id": AGENT_ID}
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = requests.post(f"{API_BASE_URL}/chatbot/chat", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

        def generate_next_message(chatbot_response):
            nonlocal test_user_messages
            prompt = f"The chatbot just said: '{chatbot_response}'\n\nWhat do you reply?"
            result = test_user_agent.run_sync(prompt, message_history=test_user_messages)
            test_user_messages = list(result.all_messages())
            return result.output

        # Main test loop
        self.stdout.write(f"\nTest User Agent starting...")
        self.stdout.write(f"Username: {USERNAME}")
        self.stdout.write(f"Agent ID: {AGENT_ID}")
        self.stdout.write(f"Turns: {NUM_TURNS}\n")

        access_token = get_access_token()
        conversation_id = None
        current_message = "Hi! How are you today?"

        for turn in range(NUM_TURNS):
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(self.style.WARNING(f"[Turn {turn + 1}]"))
            self.stdout.write(f"{'='*60}")
            self.stdout.write(f"Test User: {current_message}")
            
            result = chat_with_api(current_message, access_token, conversation_id)
            chatbot_response = result["response"]
            conversation_id = result["conversation_id"]
            
            self.stdout.write(f"Chatbot: {chatbot_response}")
            self.stdout.write(self.style.SUCCESS(f"Conversation ID: {conversation_id}"))
            
            if turn < NUM_TURNS - 1:
                time.sleep(1.0)
                current_message = generate_next_message(chatbot_response)

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"Test completed! Conversation ID: {conversation_id}"))
        self.stdout.write(f"{'='*60}")