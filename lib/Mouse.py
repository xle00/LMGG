import win32api, win32con
from time import sleep

width, height = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)



def set_pos(x, y):
    win32api.SetCursorPos((x, y))


def get_pos():
    return win32api.GetCursorPos()


def wheel(clicks, x=None, y=None, interval=0.001):
    wheelturns = abs(clicks)
    if x and y:
        set_pos(x, y)

    for _ in range(wheelturns):
        if clicks > 0:
            win32api.mouse_event(0x0800, 0, 0, -1, 0)
        elif clicks < 0:
            win32api.mouse_event(0x0800, 0, 0, 1, 0)
        sleep(interval)


def left_click(x=None, y=None, lenght=0.005):
    if not x and not y:
        x, y = get_pos()
    set_pos(x, y)
    win32api.mouse_event(0x02, 0, 0, 0, 0)
    sleep(lenght)
    win32api.mouse_event(0x04, 0, 0, 0, 0)


def mouse_drag(pos1, pos2):
    start_x = pos1[0] * 65535 // width
    start_y = pos1[1] * 65535 // height
    dst_x = pos2[0] * 65535 // width
    dst_y = pos2[1] * 65535 // height

    set_pos(pos1[0], pos1[1])
    #sleep(1)
    win32api.mouse_event(0x02, 0, 0, 0, 0)
    #sleep(1)

    try:
        moves_x = (range(start_x, dst_x, int(round((dst_x-start_x)/20))))
    except ValueError:
        moves_x = [start_x]*20
    try:
        moves_y = (range(start_y, dst_y, int(round((dst_y - start_y)/20))))
    except ValueError:
        moves_y = [start_y]*20

    for x, y in zip(moves_x, moves_y):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


if __name__ == '__main__':
    mouse_drag((640,512), (640, 560))
