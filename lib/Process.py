import ctypes
import win32gui, win32con
from time import sleep


class ProcessMemory:
    def __init__(self, process_name):
        self._exit = True
        self.name = process_name
        self.handle = 0
        self.pid = 0
        self.processes = self.enum_processes()
        self.process = self.open_process(self.name)
        print(f'Process: {self.name} | Handle: {self.handle} | pid: {hex(self.pid)}')

    @staticmethod
    def enum_processes():
        size = 128
        while True:
            lpid_process = (ctypes.c_uint * size)()
            cb = ctypes.sizeof(lpid_process)
            lpcb_needed = ctypes.c_uint()

            ctypes.windll.kernel32.K32EnumProcesses(ctypes.byref(lpid_process), cb, ctypes.byref(lpcb_needed))
            if lpcb_needed.value == cb:
                size *= 2
            else:
                return list(set(lpid_process))

    def open_process(self, process_name):
        dw_desired_access = (0x0400 | 0x0008 | 0x0010)
        b_inherit_handle = False
        dw_process_id = process_name

        for process in self.processes:
            self.handle = ctypes.windll.kernel32.OpenProcess(dw_desired_access, b_inherit_handle, process)
            if self.handle:
                h_process = self.handle
                n_size = 512
                lp_image_file_name = (ctypes.c_char * n_size)()

                ctypes.windll.kernel32.K32GetProcessImageFileNameA(h_process, lp_image_file_name, n_size)
                process_name = lp_image_file_name.value.decode('utf-8').split('\\')[::-1][0]
                if process_name == dw_process_id:
                    self.pid = process
                    return process_name

            ctypes.windll.kernel32.CloseHandle(self.handle)
        else:
            return
            # print(f'{self.name} process not found')
            # if self._exit:
            #     exit()

    def enum_modules(self):
        size = 128
        while True:
            h_process = self.handle
            lph_module = (ctypes.c_void_p * size)()
            cb = ctypes.sizeof(lph_module)
            lpcb_needed = ctypes.c_uint()

            ctypes.windll.kernel32.K32EnumProcessModulesEx(
                h_process,
                ctypes.byref(lph_module),
                cb,
                ctypes.byref(ctypes.c_ulong()),
                ctypes.c_ulong(3)
            )

            if lpcb_needed.value == cb:
                size *= 2
            else:
                return list(set(lph_module))

    def get_module_name(self, module):
        module_name = ctypes.c_buffer(260)

        ctypes.windll.kernel32.K32GetModuleBaseNameA(
            self.handle,
            ctypes.c_void_p(module),
            module_name,
            ctypes.sizeof(module_name)
        )

        return module_name.value.decode('utf-8')

    def get_module_address_by_name(self, name):
        modules = self.enum_modules()
        for module in modules:
            module_name = self.get_module_name(module)
            if module_name == name:
                # print(module_name, 'found at', hex(module)+'\n')
                return module
        else:
            # print(f'Module {name} not found\n')
            return False

    def __read(self, lp_base_address, read_buffer, lp_number_of_bytes_read):
        read_buffer = read_buffer

        h_process = self.handle
        lp_base_address = ctypes.c_void_p(lp_base_address)
        lp_buffer = ctypes.byref(read_buffer)
        n_size = ctypes.sizeof(read_buffer)
        lp_number_of_bytes_read = lp_number_of_bytes_read

        ctypes.windll.kernel32.ReadProcessMemory(h_process, lp_base_address, lp_buffer, n_size, lp_number_of_bytes_read)
        return read_buffer.value

    def read_byte(self, lp_base_address):
        read_buffer = ctypes.c_ubyte()
        lp_number_of_bytes_read = ctypes.c_ubyte(0)
        return self.__read(lp_base_address, read_buffer, lp_number_of_bytes_read)

    def read_2_bytes(self, lp_base_address):
        read_buffer = ctypes.c_uint16()
        lp_number_of_bytes_read = ctypes.c_uint16(0)
        return self.__read(lp_base_address, read_buffer, lp_number_of_bytes_read)

    def read_4_bytes(self, lp_base_address):
        read_buffer = ctypes.c_uint32()
        lp_number_of_bytes_read = ctypes.c_uint32(0)
        return self.__read(lp_base_address, read_buffer, lp_number_of_bytes_read)

    def read_8_bytes(self, lp_base_address):
        read_buffer = ctypes.c_ulonglong()
        lp_number_of_bytes_read = ctypes.c_ulonglong(0)
        return self.__read(lp_base_address, read_buffer, lp_number_of_bytes_read)

    def read_string(self, lp_base_address, string_size):
        string = ''
        for i in range(string_size):
            # char = self.read_byte(lp_base_address + i*2).to_bytes(1, 'little').decode('utf-8', 'replace')
            char = self.read_2_bytes(lp_base_address + i * 2).to_bytes(2, 'little').decode('utf-16', 'replace')
            if ord(char) == 0:
                break
            string += char
        # print('-'*50)
        return string

    def get_pointer(self, lp_base_address, offsets):
        temp_address = self.read_8_bytes(lp_base_address)
        pointer = 0x0
        if offsets:
            for offset in offsets:
                pointer = int(str(temp_address), 0) + int(str(offset), 0)
                temp_address = self.read_8_bytes(pointer)
            return pointer
        else:
            return lp_base_address


class ProcessWindow:
    def __init__(self, _class, title):
        self.hwnd = win32gui.FindWindow(_class, title)
        self.x, self.y, self.width, self.height = win32gui.GetWindowRect(self.hwnd)

    def activate(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(self.hwnd)
        sleep(.15)
        self.get_position()

    def get_position(self):
        self.x, self.y, self.width, self.height = win32gui.GetWindowRect(self.hwnd)
        return self.x, self.y


def test():
    lm = ProcessMemory('Lords Mobile.exe')
    lm.get_module_address_by_name('GameAssembly.dll')


if __name__ == '__main__':
    test()
