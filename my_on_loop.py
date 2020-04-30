import asyncio
from collections import deque

def done_callback(fut):
    fut._loop.stop()


class Loop:

    def __init__(self):
        self._ready = deque()
        self._stopping = False

    def create_task(self, coro):
        Task = asyncio.tasks.Task
        task = Task(coro, loop=self)
        return task

    def run_until_complete(self, fut):
        task = asyncio.tasks

        fut  = task.ensure_future(fut, loop=self)
        fut.add_done_callback(done_callback)
        self.run_forever()
        fut.remove_done_callback(done_callback)

    def run_forever(self):
        try:
            while True:
                self._run_once()
                if self._stopping:
                    break
        finally:
            self._stopping = False

    def call_soon(self, cb, *args, **kwargs):
        self._ready.append((cb, args))

    def call_exception_handler(self, c):
        pass

    def _run_once(self):
        ntodo = len(self._ready)
        for i in range(ntodo):
            t, a = self._ready.popleft()
            t(*a)

    def stop(self):
        self._stopping = True

    def close(self):
        self._ready.clear()

    def get_debug(self):
        return False

async def foo():
    print("Foo")

async def bar():
    print("Bar")


loop = Loop()
tasks = [loop.create_task(foo()), loop.create_task(bar())]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
