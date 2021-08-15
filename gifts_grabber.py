from lib.Process import ProcessMemory, ProcessWindow
from time import sleep
import re
from lib import Mouse, new_db
import datetime
from mss import mss
import winreg
from lib.configs import *


def generator():
    start = 0
    while True:
        yield start
        if start == 0:
            start = 4
        else:
            start -= 2


def get_pointers():
    if load_configs()['autosync']:
        pointers = Pointers.get_pointers()
    else:
        pointers = Pointers.get_pointers_offline()

    return pointers['gift_0_timer'], pointers['clock'], pointers['gift_amount']


getting_type = 1

base_pointers, clock_pointers, gifts_pointers = get_pointers()
bonuses_pointers = gifts_pointers.copy()
bonuses_pointers[-2] += 8
configs = load_configs()

levels = {'Comun': 1, 'Comum': 1, 'Incomum': 2,  'Raro': 3, 'Épico': 4, 'Lendário': 5,
          'Branco': 1, 'Verde': 2, 'Azul': 3, 'Roxo': 4, 'Dourado': 5,
          'Common': 1, 'Uncommon': 2, 'Rare': 3, 'Epic': 4, 'Legendary': 5}
name_color = (233, 231, 147)
screen_coords = {
    "guild_gifts": (670, 270),
    "bonus_gifts": (1070, 270),
    "delete_opened_gifts": (970, 180),
    "announcement": (590, 584),
    "open_all_gifs": (1121, 185),
}


sct = mss()
# window = ProcessWindow('UnityWndClass', 'Lords Mobile')
# process = ProcessMemory('Lords Mobile.exe')


def get_game_resolution():
    handle = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\IGG\Lords Mobile')
    width, height = 0, 0
    count = 0
    while (not width) or (not height):
        key, value, _ = winreg.EnumValue(handle, count)
        if 'width' in key.lower():
            width = value
        if 'height' in key.lower():
            height = value
        count += 1
    return width, height


def click(coord=None):
    if not coord:
        pass
    else:
        x, y = screen_coords.get(coord)
        Mouse.left_click(window.x + x, window.y + y)


def pixel_search(x1, y1, width, height, color, threshold):
    area = {"left": x1, "top": y1, "width": width, "height": height}
    img = sct.grab(area).pixels

    for x in img:
        for y in x:
            test1 = abs(color[0] - y[0])
            test2 = abs(color[1] - y[1])
            test3 = abs(color[2] - y[2])

            if test1 <= threshold and test2 <= threshold and test3 <= threshold:
                return True
    else:
        return False


def get_4_gifts(start, slot, remainder=0):
    result = []
    for i in range(4):
        if remainder and i >= remainder:
            return result
        if remainder:
            y = window.y + start + (4 - remainder + i)*111+49
        else:
            y = window.y + start + i*111+49
        x = window.x + 600
        sleep(.005)

        # if there's an announcement on screen wait for it to go away
        # bg = get_pixel_brightness('announcement')
        # while bg < 60 and i == 2 and start < 312:
        #     print('stuck')
        #     bg = get_pixel_brightness('announcement')

        has_name = pixel_search(x, y, 20, 12, name_color, 15)

        _slot = (slot + i) % 6
        gift = get_gift_details(_slot, has_name)
        print(gift)
        result.append(gift)
    print()
    return result


def calculate_timestamp(timestamp, time):
    hours, minutes, seconds = [int(i) for i in time.split(':')]
    hours *= 60*60
    minutes *= 60

    timestamp -= (86400 - (seconds+hours+minutes))
    return timestamp


def get_gift_details(n, has_name):
    global getting_type
    module, base_offset, *offsets = base_pointers
    offsets = offsets.copy()
    # This determines which is slot it is reading from
    offsets[4] += (n * 8)

    module_address = process.get_module_address_by_name(module)
    base_address = module_address + base_offset

    # read the time
    address = process.get_pointer(base_address, offsets)
    time = process.read_string(address, 8)
    # print(time)
    if not time:
        return []
    else:
        in_game_time = get_value(clock_pointers)
        gift_timestamp = calculate_timestamp(in_game_time, time)
        gift_date_time = datetime.datetime.fromtimestamp(gift_timestamp)

    # read the name
    offsets[3] += 5*8
    address = process.get_pointer(base_address, offsets)
    if has_name:
        name = process.read_string(address, 50)
        try:
            name = re.search(r'(Presente de) ([\d\wáãâéêíõóôúû ]+)', name).groups()[-1]
        except AttributeError:
            name = re.search(r'(Gift from) ([\d\wáãâéêíõóôúû ]+)', name).groups()[-1]
    else:
        name = '* Anônimo *'

    # read the gift
    offsets[3] -= 8
    address = process.get_pointer(base_address, offsets)
    gift = process.read_string(address, 100)
    # print(gift)
    if getting_type == 1:
        try:
            level = re.search(r'>([A-Za-zÉáé]+)<', gift, re.UNICODE).groups()[0]
            level = levels.get(level, 0)
            monster = re.search(r'([\d\w ]*)\[<color=#[\d\w]+>[\w]+</color>]([\d\w ]*)', gift)
            if monster:
                monster = monster.groups()
            else:
                monster = re.search(r'([\d\w ]*)\[<color=#[\d\w]+>[\w]+</color>([\d\w ]*)', gift)
                monster = monster.groups()

            monster = [m.strip() for m in monster if m]
            monster = ' '.join(monster)
            # print(level, monster)
        except AttributeError:
            # if 'Caixa' in gift or 'Aliança' in gift:
            level = 0
            monster = gift
            # else:
            # return [date, time, level, monster, name, getting_type]
    else:
        try:
            level = re.search(r'>([A-Za-zÉáé]+)<', gift, re.UNICODE).groups()[0]
            level = levels.get(level, 0)
            monster = re.search(r'([\d\w ]*)\[<color=#[\d\w]+>[\w]+</color>]([\d\w ]*)', gift).groups()
            monster = [m.strip() for m in monster if m]
            monster = ' '.join(monster)
            # print(level, monster)
        except AttributeError:
            monster = gift
            for color, lvl in levels.items():
                if color in gift:
                    level = lvl
                    break
            else:
                level = 0

    year = gift_date_time.year
    month = gift_date_time.month
    day = gift_date_time.day
    seconds = (gift_date_time.hour*60*60)+(gift_date_time.minute*60)+gift_date_time.second


    return [year, month, day, seconds, level, monster, name, getting_type, configs['reset_time']]


def get_pixel_brightness(coord):
    x, y = screen_coords.get('announcement')
    area = {"left": x, "top": y, "width": 1, "height": 1}
    img = sct.grab(area)
    # noinspection PyTypeChecker
    pixel = list(img.pixels[0][0])
    pixel = sum(pixel)/3
    return pixel


def get_gifts(gift_type):
    # gift_type = 1 for monster gifts
    # gift_type = 2 for bonuses
    global getting_type
    first_slot_on_screen = generator()
    getting_type = gift_type
    sleep(.5)

    # select correct gifts and delete the already opened ones
    if getting_type == 1:
        click('guild_gifts')
        sleep(.5)
        click('delete_opened_gifts')
        pointers = gifts_pointers
    elif getting_type == 2:
        click('bonus_gifts')
        sleep(.5)
        click('delete_opened_gifts')
        pointers = bonuses_pointers
    else:
        return

    # get the number of gifts to get
    sleep(.5)
    gifts_amount = get_value(pointers)
    print(gifts_amount)
    result = []
    if gifts_amount <= 0:
        return

    if gifts_amount > 4:
        remainder = gifts_amount % 4

        for i in range(gifts_amount//4):
            mod = i % 5
            scrolls = 13 if mod != 4 else 14

            sleep(.1)
            start = 298 if mod == 0 else 298 + (mod*7-2)

            first_slot = next(first_slot_on_screen)
            result += get_4_gifts(start, first_slot)

            Mouse.wheel(scrolls, window.x + 670, window.y + 400)
            new_ga = get_value(pointers)
            remainder += new_ga - gifts_amount
            gifts_amount = new_ga

        Mouse.wheel(5, window.x + 670, window.y + 400)
        sleep(1)
        remainder += get_value(pointers) - gifts_amount
        if remainder:
            print(f'remainder {remainder}')
            last_ones = get_4_gifts(287, next(first_slot_on_screen), remainder)
            result += last_ones
    else:
        result += get_4_gifts(298, 0)

    return result


def get_value(pointers):
    module, base_offset, *offsets = pointers
    module_address = process.get_module_address_by_name(module)
    address = process.get_pointer(module_address + base_offset, offsets)
    value = process.read_4_bytes(address)
    return value


def main():
    # Check if the game is in the right resolution
    width, height = get_game_resolution()
    if width != 1280 or height != 720:
        print(f'Resolução Errada: {width}x{height}. Use 1280x720')
        return

    # Bring window to front
    window.activate()
    sleep(.1)
    window.get_position()

    gifts = get_gifts(1)
    # click('open_all_gifs')
    sleep(.5)

    bonuses = get_gifts(2)
    if gifts:
        new_db.add_data(gifts)
    if bonuses:
        new_db.add_data(bonuses)
        # click('open_all_gifs')
        sleep(2)


if __name__ == '__main__':
    main()
