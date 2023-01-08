# Lightweight version of ChatGPT
Uses API by [Pawan](https://github.com/PawanOsman/)

## Disclaimer
This is not open source. [PawanOsman](https://github.com/PawanOsman/) can see all your requests and your session token.

# Install
`pip3 install ChatGPT-lite --upgrade`

# Setup:

## Getting session token
Check https://github.com/acheong08/ChatGPT/wiki/Setup

# Usage

## Command line

```
usage: ChatGPT-lite [-h] [--session_token SESSION_TOKEN] [--bypass_node BYPASS_NODE (optional)] [--async_mode]
```

## Example development:
```python
import argparse
import sys
import asyncio
from ChatGPT_lite.ChatGPT import Chatbot


async def async_main(args):
    if args.session_token is None:
        print("Please provide a session token")
        sys.exit(1)

    chat = Chatbot(args.session_token, args.bypass_node)
    await asyncio.gather(chat.wait_for_ready())

    while True:
        try:
            prompt = input("You: ")
            if prompt == "!exit":
                break
            response = await chat.ask(prompt)
            print(f"\nBot: {response['answer']}\n")
        except KeyboardInterrupt:
            break
    # Close sockets
    chat.close()
    # exit
    sys.exit(0)


def sync_main(args):
    chat = Chatbot(args.session_token, args.bypass_node)
    # Create loop
    loop = asyncio.new_event_loop()
    # Set
    asyncio.set_event_loop(loop)
    # Run
    loop.run_until_complete(chat.wait_for_ready())
    while True:
        try:
            prompt = input("You: ")
            if prompt == "!exit":
                break
            response = loop.run_until_complete(chat.ask(prompt))
            print(f"\nBot: {response['answer']}\n")
        except KeyboardInterrupt:
            break
    # Close sockets
    chat.close()
    # stop asyncio event loop
    loop.stop()
    # exit
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--session_token', type=str, default=None)
    parser.add_argument('--bypass_node', type=str,
                        default="https://gpt.pawan.krd")
    parser.add_argument('--async_mode', action='store_true')
    args = parser.parse_args()

    if args.session_token is None:
        print("Please provide a session token")
        sys.exit(1)

    print("Starting. Please wait...")
    if args.async_mode:
        asyncio.run(async_main(args))
    else:
        sync_main(args)


if __name__ == "__main__":
    main()
```
