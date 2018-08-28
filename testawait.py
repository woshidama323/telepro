import asyncio
async def test(i):
	print("test_1",i)
	await asyncio.sleep(1)
	print("test_2",i)
loop=asyncio.get_event_loop()
tasks=[test(i) for i in range(5)]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
