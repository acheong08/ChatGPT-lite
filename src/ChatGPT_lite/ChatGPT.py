import uuid
import socketio
import datetime
import asyncio
import json
import base64
import threading
import time


class Chatbot:
    def __init__(self, session_token, bypass_node="https://gpt.pawan.krd"):
        self.ready = False
        self.socket = socketio.Client()
        self.socket.connect(
            f'{bypass_node}/?client=python&version=1.0.2&versionCode=102', transports=['websocket', 'polling'])
        self.session_token = session_token
        self.conversations = []
        self.auth = None
        self.expires = datetime.datetime.now()
        self.token_next_check = datetime.datetime.now()
        self.stop_check_tokens = False
        self.socket.on('connect', self.on_connect)
        self.socket.on('disconnect', self.on_disconnect)
        # Start a new thread to run check_tokens every 2 minutes
        self.check_tokens_thread = threading.Thread(
            target=self.check_tokens_periodically)
        self.check_tokens_thread.start()

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def check_tokens_periodically(self):
        while True:
            if self.stop_check_tokens:
                return
            # Check if token next check time has passed
            if self.token_next_check > datetime.datetime.now():
                time.sleep(1)
                continue
            now = datetime.datetime.now()
            # Use timedelta to subtract time
            offset = datetime.timedelta(milliseconds=2 * 60 * 1000)
            if self.expires < (now - offset) or self.auth is None:
                # Run get_tokens as an asyncio task using run_in_executor
                self.get_tokens()
            # Set the next check time to 2 minutes from now
            self.token_next_check = now + offset
            time.sleep(5)

    def add_conversation(self, id):
        conversation = {
            'id': id,
            'conversation_id': None,
            'parent_id': str(uuid.uuid4()),
            'last_active': datetime.datetime.now()
        }
        self.conversations.append(conversation)
        return conversation

    def get_conversation_by_id(self, id):
        conversation = next(
            (c for c in self.conversations if c['id'] == id), None)
        if conversation is None:
            conversation = self.add_conversation(id)
        else:
            conversation['last_active'] = datetime.datetime.now()
        return conversation

    def wait(self, time):
        return asyncio.sleep(time)

    async def wait_for_ready(self):
        while not self.ready:
            await self.wait(5)

    async def ask(self, prompt, id="default"):
        if self.auth is None or not self.validate_token(self.auth):
            await self.get_tokens()
        conversation = self.get_conversation_by_id(id)

        # Use the callback function to process the response
        data = self.socket.call(event='askQuestion', data={
            'prompt': prompt,
            'parentId': conversation['parent_id'],
            'conversationId': conversation['conversation_id'],
            'auth': self.auth
        }, timeout=180)

        # Keep checking the queue for data
        if 'error' in data:
            print(f'Error: {data["error"]}')
            data["answer"] = "Error occurred"
            return data
        conversation['parent_id'] = data['messageId']
        conversation['conversation_id'] = data['conversationId']
        return data

    def validate_token(self, token):
        if token is None:
            return False
        parsed = json.loads(base64.b64decode(
            token.split('.')[1] + "===").decode())
        return datetime.datetime.now().timestamp() <= parsed['exp']

    def get_tokens(self):
        time.sleep(1)  # equivalent to await self.wait(1000)
        self.socket.emit(event='getSession', data=self.session_token,
                         callback=self.get_tokens_callback)

    def get_tokens_callback(self, data):
        if 'error' in data:
            print(f'Error: {data["error"]}')
            return
        self.session_token = data['sessionToken']
        self.auth = data['auth']
        # Convert 2023-01-31T15:16:58.065Z to datetime object
        self.expires = datetime.datetime.strptime(
            data['expires'], '%Y-%m-%dT%H:%M:%S.%fZ')
        self.ready = True

    def close(self):
        self.socket.disconnect()
        self.stop_check_tokens = True
        self.check_tokens_thread.join()
