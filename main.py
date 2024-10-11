from client import RawClient
from retry_decorator import http_retry


if __name__ == '__main__':
    client = RawClient()
    print(client.get_one('https://www.geeksforgeeks.org/decorators-in-python/'))