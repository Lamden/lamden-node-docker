from unittest import TestCase
import asyncio

from utils.sync_blocks import SyncBlocksHandler

TESTNET_NODE_IPS = ['178.62.52.51', '128.199.9.156', '142.93.210.208']

class TestSyncBlocksHandler(TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.ip_list = []

    def tearDown(self):
        self.loop.close()

    def test_METHOD_ping_all_nodes__keeps_online_nodes(self):
        self.ip_list = TESTNET_NODE_IPS
        sync_block_handler = SyncBlocksHandler(start_block=0, node_ips=self.ip_list)

        self.loop.run_until_complete(sync_block_handler.ping_all_nodes())

        self.assertEqual(3, len(sync_block_handler.node_ips))


    def test_METHOD_ping_all_nodes__removes_offline_nodes(self):
        self.ip_list = TESTNET_NODE_IPS
        self.ip_list.append('0.0.0.0')
        sync_block_handler = SyncBlocksHandler(start_block=0, node_ips=self.ip_list)

        # Had 4 ips in list
        self.assertEqual(4, len(sync_block_handler.node_ips))

        self.loop.run_until_complete(sync_block_handler.ping_all_nodes())

        # Has dropped the offline node
        self.assertEqual(3, len(sync_block_handler.node_ips))
        self.assertFalse('0.0.0.0' in sync_block_handler.node_ips)

    def test_METHOD_validate_ip_list__keeps_valid_ips(self):
        self.ip_list = TESTNET_NODE_IPS
        self.ip_list.append('0.0.0.0')
        sync_block_handler = SyncBlocksHandler(start_block=0, node_ips=self.ip_list)

        # Had 4 ips in list
        self.assertEqual(4, len(sync_block_handler.node_ips))

        self.loop.run_until_complete(sync_block_handler.ping_all_nodes())

        # Has dropped the offline node
        self.assertEqual(3, len(sync_block_handler.node_ips))
        self.assertFalse('0.0.0.0' in sync_block_handler.node_ips)

    def test_METHOD_validate_ip_list__returns_true_if_all_ips_valid(self):
        self.ip_list = TESTNET_NODE_IPS
        self.ip_list.append('0.0.0.0')
        sync_block_handler = SyncBlocksHandler(start_block=0, node_ips=self.ip_list)

        # Had 4 ips in list
        self.assertEqual(4, len(sync_block_handler.node_ips))

        self.loop.run_until_complete(sync_block_handler.ping_all_nodes())

        # Has dropped the offline node
        self.assertEqual(3, len(sync_block_handler.node_ips))
        self.assertFalse('0.0.0.0' in sync_block_handler.node_ips)