import serial
import serial.tools.list_ports


class AtCommand:
    def __init__(self):
        self.ser = None

    def open(self, port, rd_timeout=1):
        # Open searil port
        self.ser = serial.Serial(port, timeout=rd_timeout)

    def close(self):
        # Close searil port
        self.ser.close()

    def send_at(self, cmd):
        cmd_ex = cmd + '\r\n'
        print('Sending ' + cmd + ' ...')
        self.ser.write(cmd_ex.encode())

    def send_at_notn(self, cmd):
        cmd_ex = cmd
        print('Sending ' + cmd + ' ...')
        self.ser.write(cmd_ex.encode())

    def check_at_resp(self, exp_str, max_size=200):
        '''
        It reads AT response and checks if there is any error.
        All AT response string will be returned if no error, otherwise
        None will be returned.
        '''
        ret = self.ser.read_until(exp_str + '\r\n', max_size).decode()
        print('Received: ' + ret)
        if exp_str not in ret:
            print("Actual AT response is: ", ret,
                  "\nBut expected response is: ", exp_str)
            ret = None
        return ret

    def parse_at_resp(self, targ_str, at_resp):
        '''
        It extracts the line including target string, then return the string after target string
        at the same line.
        None will be returned in case of any error
        '''
        for cur_line in at_resp.split('\r\n'):
            if targ_str in cur_line:
                # Remove leading and trailing whitespace chars and target string
                return cur_line.replace(targ_str, '').strip()
        else:
            return None


# 查找端口函数
def findPort():
    ports = serial.tools.list_ports.comports()
    for each in ports:
        if 'Unisoc Usb Serial Port 0' in each.description:
            return each.device


# if __name__ == "__main__":
#     port = findPort()
#     if port is None:
#         print("Can't find the port!")
#         exit(1)
#     print("The port is: ", port)

#     test_at = AtCommand()
#     test_at.open(port)

#     # Pass case for check_at_resp
#     test_at.send_at('AT')
#     if test_at.check_at_resp('OK') == 'OK':
#         print("Pass case for check_at_resp")
#     # # Error case for check_at_resp
#     # test_at.send_at('AT+COPS?')
#     # print(test_at.check_at_resp('OK1'))
#     # # Pass case for parse_at_resp
#     # test_at.send_at('ATI')
#     # print(test_at.parse_at_resp('Revision:', test_at.check_at_resp('OK')))
#     # # Error case for parse_at_resp
#     # test_at.send_at('ATI')
#     # print(test_at.parse_at_resp('Revision1:', test_at.check_at_resp('OK')))

#     test_at.close()
