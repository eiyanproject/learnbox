import asyncio

from kvserver import KVServer


async def with_server(scenario):
    kv = KVServer()
    port = await asyncio.wait_for(kv.start(), 5)
    assert isinstance(port, int) and port > 0, "start() must return the listening port"
    try:
        return await asyncio.wait_for(scenario(port), 10)
    finally:
        await asyncio.wait_for(kv.stop(), 5)


async def client(port):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)

    async def ask(line):
        writer.write((line + "\n").encode())
        await writer.drain()
        return (await reader.readline()).decode().rstrip("\n")

    return reader, writer, ask


def test_set_get_del_keys():
    async def scenario(port):
        _, writer, ask = await client(port)
        assert await ask("GET missing") == "NIL"
        assert await ask("SET name Ana Wijaya") == "OK"
        assert await ask("GET name") == "Ana Wijaya"
        assert await ask("SET city Jakarta") == "OK"
        assert await ask("KEYS") == "city name"
        assert await ask("DEL name") == "1"
        assert await ask("DEL name") == "0"
        assert await ask("KEYS") == "city"
        writer.close()

    asyncio.run(with_server(scenario))


def test_errors_keep_connection_open():
    async def scenario(port):
        _, writer, ask = await client(port)
        assert await ask("FLY away") == "ERR unknown command"
        assert await ask("GET") == "ERR unknown command"
        assert await ask("SET k v") == "OK"
        writer.close()

    asyncio.run(with_server(scenario))


def test_quit_closes_connection():
    async def scenario(port):
        reader, writer, ask = await client(port)
        assert await ask("QUIT") == "BYE"
        assert await reader.read() == b""
        writer.close()

    asyncio.run(with_server(scenario))


def test_clients_share_the_store_and_run_concurrently():
    async def scenario(port):
        _, w1, ask1 = await client(port)
        _, w2, ask2 = await client(port)
        assert await ask1("SET shared 42") == "OK"
        assert await ask2("GET shared") == "42"

        async def many(i):
            _, w, ask = await client(port)
            for j in range(20):
                assert await ask(f"SET k{i}-{j} {j}") == "OK"
            w.close()

        await asyncio.gather(*(many(i) for i in range(10)))
        keys = (await ask1("KEYS")).split()
        assert len(keys) == 201
        w1.close()
        w2.close()

    asyncio.run(with_server(scenario))
