import asyncio
import time


async def interview_candidate(name, t1, d1, t2, d2):
    print(f"{name} started the 1 task.")
    await asyncio.sleep(t1 / 100)
    print(f"{name} moved on to the defense of the 1 task.")
    await asyncio.sleep(d1 / 100)
    print(f"{name} completed the 1 task.")
    print(f"{name} is resting.")
    await asyncio.sleep(5 / 100)

    print(f"{name} started the 2 task.")
    await asyncio.sleep(t2 / 100)
    print(f"{name} moved on to the defense of the 2 task.")
    await asyncio.sleep(d2 / 100)
    print(f"{name} completed the 2 task.")


async def interviews(*candidates):
    tasks = [asyncio.create_task(interview_candidate(*c)) for c in candidates]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    data = [('Ivan', 5, 2, 7, 2), ('John', 3, 4, 5, 1), ('Sophia', 4, 2, 5, 1)]
    t0 = time.time()
    asyncio.run(interviews(*data))
    print(time.time() - t0)
