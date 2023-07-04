import asyncio
import aiohttp
import argparse
import json
import time

class BlockchainValidator:
    def __init__(self, base_url):
        self.latest_block_url = base_url + "/latest_block"
        self.prev_block_url = base_url + "/prev_block?num="
        self.rate_limit = asyncio.Semaphore(20)
        self.last_request_time = time.time()
        
    async def get_latest_block(self):
        async with self.rate_limit:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.latest_block_url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Failed to get the latest block. Status code: {response.status}")
                        return None

    async def get_prev_block(self, block_num):
        async with self.rate_limit:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.prev_block_url + str(block_num)) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Failed to get the block number {block_num}. Status code: {response.status}")
                        return None
    
    async def validate_chain(self):
        latest_block = await self.get_latest_block()
        print(latest_block)
        
        if latest_block is None:
            return
        
        while int(latest_block['number']) > 0:
            prev_block = await self.get_prev_block(latest_block['number'])
            if prev_block is None:
                break

            if latest_block['previous'] != prev_block['hash']:
                print(f"Chain breakdown: Previous block {prev_block['number']} doesn't match the latest block {latest_block['number']}")
                print(f"{latest_block['number']}: previous = {latest_block['previous']}")
                print(f"f{prev_block['number']}: hash = {prev_block['hash']}")
            latest_block = prev_block

    async def refill_rate_limit(self):
        while True:
            await asyncio.sleep(15)
            for _ in range(20):
                self.rate_limit.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Validate a blockchain.')
    parser.add_argument('--url', required=True, help='The base URL of the blockchain API.')
    args = parser.parse_args()
    
    validator = BlockchainValidator(args.url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(validator.validate_chain(), validator.refill_rate_limit()))

