import asyncio
from backtest.backtest import Backtest

async def run(runner):
    while runner:
        waiter = asyncio.Future()
        await waiter

if __name__ == '__main__':
    try:
        asyncio.get_event_loop().set_debug(True)
        runner = asyncio.ensure_future(Backtest.downloadStocksData())
        run(runner)
    except (KeyboardInterrupt, SystemExit):
        None