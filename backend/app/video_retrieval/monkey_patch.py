import asyncio
import asyncio_gevent
import gevent.monkey
import gevent

gevent.monkey.patch_all()
asyncio.set_event_loop_policy(asyncio_gevent.EventLoopPolicy())
