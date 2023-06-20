import aiohttp
import asyncio
import json

class SyncBlocksHandler:
    def __init__(self, start_block: str = '0', node_ips: list = []):
        if len(node_ips) == 0:
            raise ValueError('Invalid node_ips list: list cannot be empty.')

        self.start_block = start_block
        self.node_ips = self.validate_ip_list(ip_list=node_ips)

    def validate_ip_list(self, ip_list:list = []):
        ips = [ip for ip in ip_list if self.validate_ip(ip)]

        if len(ips) == 0:
            print(ip_list)
            raise ValueError('Invalid node_ips list: No valid ips found.')

    def validate_ip(self, ip: str = ''):
        #splitting each ip
        octets = ip.split('.')
        #checking if ip has four octets
        if len(octets) != 4:
            return False

        for octet in octets:
            if not octet.isdigit():
                return False
            i = int(octet)

            #checking if each octet lies in the valid range 0-255
            if i < 0 or i > 255:
                return False

        return True

    async def ping_all_nodes(self):
        async with aiohttp.ClientSession() as session:
            ip_list = [ip for ip in await asyncio.gather(*[self.check_node(session, ip) for ip in self.node_ips]) if ip]

        if len(ip_list) == 0:
            print(ip_list)
            raise ValueError('Invalid node_ips list: Unable to ping any node in list.')
        
        self.node_ips = ip_list


    async def check_node(self, session, node_ip):
        try:
            async with session.get(f'http://{node_ip}:18080/ping', timeout=15) as response:
                if response.content_type == 'application/json':
                    data = await response.text()
                    json_data = json.loads(data)
                    if json_data.get('status') == 'online':
                        return node_ip
        except Exception as e:
            print(f"Failed to connect to {node_ip}: {e}")
        return None



