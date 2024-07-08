from client import RawClient


if __name__ == '__main__':
    client = RawClient()
    print(client.fetch_one('http://google.com'))