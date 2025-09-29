# app/events/loop_manager.py
import asyncio
import threading

# bikin 1 event loop global
loop = asyncio.new_event_loop()

# jalanin loop di thread terpisah (daemon=True biar otomatis mati kalau app mati)
threading.Thread(target=loop.run_forever, daemon=True).start()


def run_async(coro):
    """
    Submit coroutine ke loop global, return concurrent.futures.Future
    """
    return asyncio.run_coroutine_threadsafe(coro, loop)
