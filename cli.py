import requests
import asyncio
import urllib.request
import argparse
from aiohttp_jrpc import Client, InvalidResponse, InvalidParams


class WrongResult(Exception):
    pass


class RpcCalls:
    def __init__(self, host, port):
        self.api_url = "http://%s:%s/api" % (host, str(port))
        self.upload_url = "http://%s:%s/upload" % (host, str(port))
        self.download_root = "http://%s:%s/" % (host, str(port))
        self.remote = Client(self.api_url)

    def request_api(self, method, params):
        loop = asyncio.get_event_loop()
        result = None
        try:
            result = loop.run_until_complete(self.remote.call(method, params))
        except InvalidResponse as e:
            print("Error with request", e)
        except InvalidParams as e:
            print(e)
        return result

    def add(self, data):
        result = self.request_api('add', {"name": data[0], "city": data[1]})
        if not result:
            return
        print(result.result)

    def where(self, data):
        result = self.request_api('where', {"name": data[0]})
        if not result or result is None:
            return
        print(result.result)

    def help(self, data):
        result = self.request_api('help', {"name": data[0]})
        if not result:
            return
        print(result.result)

    def load(self, data):
        files = {'csv': open(data[0], 'rb')}
        r = requests.post(self.upload_url, files=files)
        print(r.text)
        print("OK")

    def save(self, data):
        result = self.request_api("save", {"filename": data[0]})
        if not result:
            return
        urllib.request.urlretrieve(self.download_root + result.result, data[0])
        print("OK")


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="server host", default='localhost')
    parser.add_argument("--port", help="server port", default=8080)
    args = parser.parse_args()
    rpc = RpcCalls(args.host, args.port)

    try:
        while (True):
            arguments = input()
            arguments = arguments.split(' ')
            command = arguments.pop(0)
            try:
                getattr(rpc, command)(arguments)
            except AttributeError as e:
                print("Command %s not found. Try another command" % command)
    except KeyboardInterrupt:
        print("Bye-bye")
