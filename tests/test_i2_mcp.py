import json
import os
import sys
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class McpIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_read_only_careers_over_stdio(self):
        params = StdioServerParameters(
            command=sys.executable,
            args=['-m', 'services.mcp_server'],
            cwd=os.getcwd(),
        )
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as client:
                await client.initialize()
                available = await client.list_tools()
                self.assertEqual([tool.name for tool in available.tools], ['list_careers'])
                result = await client.call_tool('list_careers', {})
                self.assertFalse(result.isError)
                payload = result.structuredContent
                if payload is None:
                    payload = json.loads(result.content[0].text)
                if isinstance(payload, dict) and 'result' in payload:
                    payload = payload['result']
                self.assertEqual({item['id'] for item in payload}, {'1CMP', '1MAC'})
                self.assertTrue(all(item['name'] for item in payload))
                missing = await client.call_tool('sync_course_catalog', {})
                self.assertTrue(missing.isError)


if __name__ == '__main__':
    unittest.main()
