
from plover.engine import StenoEngine
from plover import log

import asyncio
from functools import wraps, partial

def async_wrap(func):
    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
    return run 

class TuiEngine(StenoEngine):

    def __init__(self, config, keyboard_emulation):
        StenoEngine.__init__(self, config, keyboard_emulation)
        self.name += '-engine'
        # hax, but we can't use threading.RLock
        # thankfully the methods are, like, the same
        log.info("tui init")
        self._lock = asyncio.Lock()

    # deliberately overwriting StenoEngine so we can await func
    def run(self):
        while True:
            self.process_queue()

    @async_wrap
    def process_queue(self):
        func, args, kwargs = self._queue.get()
        try:
            with self._lock:
                if func(*args, **kwargs):
                    return
        except Exception:
            log.error('engine %s failed', func.__name__[1:], exc_info=True)

    def _in_engine_thread(self):
        # lol, everything on queue pls
        return False

    def start(self):
        StenoEngine.start(self)
