# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# This requires the 'arduplot'
#
import subprocess
import socket
from platformio.commands.device import DeviceMonitorFilter
from platformio.project.helpers import get_project_core_dir
from distutils.spawn import find_executable

PORT = 19200

class SerialPlotter(DeviceMonitorFilter):
    NAME = "serial_plotter"

    def __init__(self, *args, **kwargs):
        super(SerialPlotter, self).__init__(*args, **kwargs)
        self.buffer = ''
        self.arduplot = 'arduplot'
        self.plot = None
        self.plot_sock = ''
        self.plot = ''

    def __call__(self):
        if find_executable(self.arduplot) == None:
            print("\n\nThe 'arduplot' is not installed on this system")
            print("Please, install the 'arduplot' to run with -f serial_plotter\n")
            print("Run\n")
            print("\tpip install arduplot\n")
            exit(1)
        print('--- serialPlotter is starting')
        self.plot = subprocess.Popen(['arduplot', '-s', str(PORT)])
        try:
            self.plot_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.plot_sock.connect(('localhost', PORT))
        except socket.error:
            pass
        return self

    def __del__(self):
        if self.plot:
            self.plot.kill()
    
    def rx(self, text):
        self.buffer += text
        if '\n' in self.buffer:
            try:
                self.plot_sock.send(bytes(self.buffer, 'utf-8'))
            except BrokenPipeError:
                try:
                    self.plot_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.plot_sock.connect(('localhost', PORT))
                except socket.error:
                    print('--- serialPlotter is not started')
            self.buffer = ''
        return text