import asyncio


async def udobr(plant):
    print(f"7 Application of fertilizers for {plant}")
    await asyncio.sleep(3 / 1000)
    print(f"7 Fertilizers for the {plant} have been introduced")


async def borb_vred(plant):
    print(f"8 Treatment of {plant} from pests")
    await asyncio.sleep(5 / 1000)
    print(f"8 The {plant} is treated from pests")


async def grow_plant(plant, soak, grow, adapt):
    print(f"0 Beginning of sowing the {plant} plant")
    print(f"1 Soaking of the {plant} started")

    # Параллельно подкормка и обработка от вредителей
    fert_task = asyncio.create_task(udobr(plant))
    pest_task = asyncio.create_task(borb_vred(plant))

    await asyncio.sleep(soak / 1000)
    print(f"2 Soaking of the {plant} is finished")

    print(f"3 Shelter of the {plant} is supplied")
    await asyncio.sleep(grow / 1000)
    print(f"4 Shelter of the {plant} is removed")

    print(f"5 The {plant} has been transplanted")
    await asyncio.sleep(adapt / 1000)
    print(f"6 The {plant} has taken root")

    await fert_task
    await pest_task

    print(f"9 The seedlings of the {plant} are ready")


async def sowing(*plants):
    tasks = []
    for plant in plants:
        name, soak, grow, adapt = plant
        tasks.append(asyncio.create_task(grow_plant(name, soak, grow, adapt)))
    await asyncio.gather(*tasks)


data = [('carrot', 7, 18, 2), ('cabbage', 2, 6, 10), ('onion', 5, 12, 7)]
asyncio.run(sowing(*data))
