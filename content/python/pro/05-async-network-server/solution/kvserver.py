import asyncio


class KVServer:
    def __init__(self):
        self.store = {}
        self.server = None

    def execute(self, line):
        parts = line.split(maxsplit=2)
        if not parts:
            return "ERR unknown command", False
        cmd, args = parts[0].upper(), parts[1:]
        if cmd == "SET" and len(args) == 2:
            self.store[args[0]] = args[1]
            return "OK", False
        if cmd == "GET" and len(args) == 1:
            return self.store.get(args[0], "NIL"), False
        if cmd == "DEL" and len(args) == 1:
            return ("1" if self.store.pop(args[0], None) is not None else "0"), False
        if cmd == "KEYS" and not args:
            return " ".join(sorted(self.store)), False
        if cmd == "QUIT" and not args:
            return "BYE", True
        return "ERR unknown command", False

    async def handle_client(self, reader, writer):
        try:
            while line := await reader.readline():
                reply, close = self.execute(line.decode().strip())
                writer.write((reply + "\n").encode())
                await writer.drain()
                if close:
                    break
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionError:
                pass

    async def start(self, host="127.0.0.1", port=0):
        self.server = await asyncio.start_server(self.handle_client, host, port)
        return self.server.sockets[0].getsockname()[1]

    async def stop(self):
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()


async def main():
    kv = KVServer()
    port = await kv.start(port=7070)
    print(f"listening on 127.0.0.1:{port}  (try: printf 'SET a 1\\nGET a\\n' | nc 127.0.0.1 {port})")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
