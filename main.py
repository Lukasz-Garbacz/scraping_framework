from client import RawClient
from retry_decorator import retry


if __name__ == '__main__':
    client = RawClient()
    print(client.fetch_one('http://google.com'))