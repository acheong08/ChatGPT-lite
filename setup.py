from setuptools import find_packages
from setuptools import setup

setup(
    name="ChatGPT_lite",
    version="0.0.5",
    license="GNU General Public License v2.0",
    author="Antonio Cheong",
    author_email="acheong@student.dalat.org",
    description="ChatGPT is a reverse engineering of OpenAI's ChatGPT API",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=["revChatGPT"],
    url="https://github.com/acheong08/ChatGPT-lite",
    install_requires=[
        "asyncio",
        "python-socketio[client]",
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "ChatGPT-lite = ChatGPT_lite.__main__:main",
        ]
    },
)
