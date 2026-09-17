import asyncio


class KVServer:
    def __init__(self):
        self.store = {}
        self.server = None

    async def handle_client(self, reader, writer):
        pass

    async def start(self, host="127.0.0.1", port=0):
        pass

    async def stop(self):
        pass


async def main():
    kv = KVServer()
    port = await kv.start(port=7070)
    print(f"listening on 127.0.0.1:{port}  (try: printf 'SET a 1\\nGET a\\n' | nc 127.0.0.1 {port})")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
