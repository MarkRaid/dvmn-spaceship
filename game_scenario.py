from helper import asleep
from constants import TIC_TIMEOUT

FIRST_YEAR = 1957
YEAR_OF_APPEARANCE_OF_WEAPON = 2020

PHRASES = {
    1957: "First Sputnik",
    1961: "Gagarin flew!",
    1969: "Armstrong got on the moon!",
    1971: "First orbital space station Salute-1",
    1981: "Flight of the Shuttle Columbia",
    1998: 'ISS start building',
    2011: 'Messenger launch to Mercury',
    2020: "Take the plasma gun! Shoot the garbage!",
}

current_year = FIRST_YEAR


async def time_flow():
    global current_year

    while True:
        await asleep(int(1.5/TIC_TIMEOUT))
        current_year += 1


def get_garbage_delay_tics(year):
    if year < 1961:
        return None
    elif year < 1969:
        return 20
    elif year < 1981:
        return 14
    elif year < 1995:
        return 10
    elif year < 2010:
        return 8
    elif year < 2020:
        return 6
    else:
        return 2
