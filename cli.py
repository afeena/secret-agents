import requests
import asyncio
import urllib.request
from aiohttp_jrpc import Client, InvalidResponse

api_url = "http://192.168.1.3:8080/api"
upload_url = "http://192.168.1.3:8080/upload"
download_root = "http://192.168.1.3:8080/"
remote = Client(api_url)


def request_api(method, params):
    loop = asyncio.get_event_loop()
    result = None
    try:
        result = loop.run_until_complete(remote.call(method, params))
    except InvalidResponse as e:
        print("Error with request", e)
    return result


def add(data):
    result = request_api('add', {"name": data[0], "city": data[1]})
    if not result:
        return
    print(result.result)


def where(data):
    result = request_api('where', {"name": data[0]})
    if not result:
        return
    print(result.result)


def help(data):
    result = request_api('help', {"name": data[0]})
    if not result:
        return
    print(result.result)


def upload(data):
    files = {'file': open(data[0], 'rb')}
    r = requests.post(upload_url, files=files)
    print(r.text)


def save(data):
    result = request_api("save", data[0])
    if not result:
        return
    urllib.request.urlretrieve(download_root + result.result, data[0])


if __name__ == '__main__':
    print("""
 _____                    _      ___                   _
/  ___|                  | |    / _ \                 | |
\ `--.  ___  ___ _ __ ___| |_  / /_\ \ __ _  ___ _ __ | |_
 `--. \/ _ \/ __| '__/ _ \ __| |  _  |/ _` |/ _ \ '_ \| __|
/\__/ /  __/ (__| | |  __/ |_  | | | | (_| |  __/ | | | |_
\____/ \___|\___|_|  \___|\__| \_| |_/\__, |\___|_| |_|\__|
                                       __/ |
                                      |___/
 _____                       _
/  __ \                     | |
| /  \/ ___  _ __  ___  ___ | | ___
| |    / _ \| '_ \/ __|/ _ \| |/ _ \\
| \__/\ (_) | | | \__ \ (_) | |  __/
 \____/\___/|_| |_|___/\___/|_|\___|

    """)

    commands = {
        "add": add,
        "where": where,
        "help": help,
        "save": save,
        "load": upload
    }

    try:
        while (True):
            arguments = input()
            arguments = arguments.split(' ')
            command = arguments.pop(0)
            params = arguments
            commands[command](params)
    except KeyboardInterrupt:
        print("Bye-bye")
