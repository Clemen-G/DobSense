import sys
import termios
import asyncio
import contextlib

class KeyReader:
    def __init__(self):
        self.callback = None
    
    @contextlib.contextmanager
    def raw_mode(self, file):
        old_attrs = termios.tcgetattr(file.fileno())
        new_attrs = old_attrs[:]
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        try:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
            yield
        finally:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)

    async def read_keys(self):
        with self.raw_mode(sys.stdin):
            reader = asyncio.StreamReader()
            loop = asyncio.get_event_loop()
            await loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(reader), sys.stdin)

            while not reader.at_eof():
                ch = await reader.read(1)
                # '' means EOF, chr(4) means EOT (sent by CTRL+D on UNIX terminals)
                if not ch or ord(ch) <= 4:
                    break
                ch = ch.decode("utf-8")
                if self.callback:
                    self.callback(ch)
                # print(f'Got: {ch!r}')
