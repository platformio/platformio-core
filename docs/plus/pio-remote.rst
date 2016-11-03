..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. |PIORemote| replace:: **PIO Remote™**
.. |PIOCloud| replace:: PlatformIO Cloud

.. _pio_remote:

PIO Remote™
===========

**Your devices are always with you!**

.. versionadded:: 3.2 (`PlatformIO Plus <https://pioplus.com>`__)

|PIORemote| allows you to work remotely with devices from
*Anywhere In The World*. No matter where are you now! Run small and
cross-platform :ref:`pio_remote_agent` on a host machine and you will be able to
list active devices (wireless + wired), to upload firmware **Over-The-Air (OTA)**,
to process remote unit tests, or to start remote debugging session via OTA
Serial Port Monitor.

Using PIO Remote™ you can share your devices with friends or team. In
combination with Cloud IDE, you can create awesome things at any time when
inspiration comes to you.

You should have :ref:`cmd_account` to work with |PIORemote|.
A registration is **FREE**.

Features
--------

* :ref:`ide_cloud`
* :ref:`OTA Device Manager <cmd_remote_device>`
* :ref:`OTA Serial Port Monitor <cmd_remote_device_monitor>`
* :ref:`OTA Firmware Updates <cmd_remote_run>`
* Continuous Deployment
* Continuous Delivery
* Remote Unit Testing

Technology
----------

|PIORemote| is an own `PlatformIO Plus <https://pioplus.com/>`__ technology for
**Over-The-Air (OTA)** remote operations without external dependencies to
operation system or its software based on `client-server architecture <https://en.wikipedia.org/wiki/Client–server_model>`_.
The Server component (|PIOCloud|) plays a role of coupling link between
:ref:`pio_remote_agent` and client (end-developer, continuous integration
system, etc.).
When you start :ref:`pio_remote_agent`, it connects over the Internet with
|PIOCloud| and listen for the actions/commands which you can send in Client
role from anywhere in the world.

|PIORemote| is multi-agents and multi-clients system. A single agent can be
shared with multiple clients, where different clients can use the same agent.
This approach allows to work with distributed hardware located in the different
places, networks, etc.

This technology allows to work with remote devices in generic form as you
do that with local devices using PlatformIO ecosystem. The only one difference
is a prefix "remote" before each generic PlatformIO command. For example,
listing of local and remote devices will look like :ref:`cmd_device_list` and
:ref:`cmd_remote_device_list`.

.. _pio_remote_agent:

|PIORemote| Agent
-----------------

Start |PIORemote| Agent (using :ref:`cmd_remote_agent_start` command) on a
local host machine and work remotely with your devices **WITHOUT** extra
software, 3-rd party services, SSH, VPN, tunneling or
opening incoming network ports.

|PIORemote| supports wired and wireless devices. Wired devices should be
connected physically to host machine where |PIORemote| Agent is started,
where wireless devices should be visible for |PIORemote| Agent to provide
network operations Over-The-Air.

To list active |PIORemote| Agents, please use :ref:`cmd_remote_agent_list`
command.

User Guide (CLI)
----------------

.. toctree::
    :maxdepth: 3

    platformio account <../userguide/account/index>
    platformio remote <../userguide/remote/index>


