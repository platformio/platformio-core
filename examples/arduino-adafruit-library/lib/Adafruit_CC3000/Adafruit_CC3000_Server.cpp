/**************************************************************************/
/*! 
  @file     Adafruit_CC3000_Server.cpp
  @author   Tony DiCola (tony@tonydicola.com)
  @license  BSD (see license.txt) 

  Adafruit CC3000 TCP server implementation based on the same interface as 
  the Arduino Ethernet library server class.

  See http://arduino.cc/en/Reference/Ethernet for documentation on the 
  Arduino Ethernet library and its server interface.

*/
/**************************************************************************/
#include "Adafruit_CC3000_Server.h"

#include "utility/socket.h"

#define CC3K_PRINTLN_F(text) CHECK_PRINTER { if(CC3KPrinter != NULL) { CC3KPrinter->println(F(text)); } }

#define HANDLE_NULL(client, value) { if (client == NULL) return value; }


/**************************************************************************/
/*
  Adafruit_CC3000_ClientRef implementation
*/
/**************************************************************************/

Adafruit_CC3000_ClientRef::Adafruit_CC3000_ClientRef(Adafruit_CC3000_Client* client)
  : _client(client) 
{ }

// Return true if the referenced client is connected.  This is provided for
// compatibility with Ethernet library code.
Adafruit_CC3000_ClientRef::operator bool() {
  return connected();
}
// Below are wrappers around the public client functions.  These hide the fact that users
// are dealing with a reference to a client instance and allow code to be written using
// value semantics like in the Ethernet library.
bool Adafruit_CC3000_ClientRef::connected(void) {
  HANDLE_NULL(_client, false);
  return _client->connected();
}

size_t Adafruit_CC3000_ClientRef::write(uint8_t c) {
  HANDLE_NULL(_client, 0);
  return _client->write(c);
}

size_t Adafruit_CC3000_ClientRef::fastrprint(const char *str) {
  HANDLE_NULL(_client, 0);
  return _client->fastrprint(str);
}

size_t Adafruit_CC3000_ClientRef::fastrprintln(const char *str) {
  HANDLE_NULL(_client, 0);
  return _client->fastrprintln(str);
}

size_t Adafruit_CC3000_ClientRef::fastrprint(char *str) {
  HANDLE_NULL(_client, 0);
  return _client->fastrprint(str);
}

size_t Adafruit_CC3000_ClientRef::fastrprintln(char *str) {
  HANDLE_NULL(_client, 0);
  return _client->fastrprintln(str);
}

size_t Adafruit_CC3000_ClientRef::fastrprint(const __FlashStringHelper *ifsh) {
  HANDLE_NULL(_client, 0);
  return _client->fastrprint(ifsh);
}

size_t Adafruit_CC3000_ClientRef::fastrprintln(const __FlashStringHelper *ifsh) {
  HANDLE_NULL(_client, 0);
  return _client->fastrprintln(ifsh);
}

int16_t Adafruit_CC3000_ClientRef::write(const void *buf, uint16_t len, uint32_t flags) {
  HANDLE_NULL(_client, 0);
  return _client->write(buf, len, flags);
}

int16_t Adafruit_CC3000_ClientRef::read(void *buf, uint16_t len, uint32_t flags) {
  HANDLE_NULL(_client, 0);
  return _client->read(buf, len, flags);
}

uint8_t Adafruit_CC3000_ClientRef::read(void) {
  HANDLE_NULL(_client, 0);
  return _client->read();
}

int32_t Adafruit_CC3000_ClientRef::close(void) {
  HANDLE_NULL(_client, 0);
  return _client->close();
}

uint8_t Adafruit_CC3000_ClientRef::available(void) {
  HANDLE_NULL(_client, 0);
  return _client->available();
}


/**************************************************************************/
/*
  Adafruit_CC3000_Server implementation
*/
/**************************************************************************/

// Construct a TCP server to listen on the specified port.
Adafruit_CC3000_Server::Adafruit_CC3000_Server(uint16_t port)
  : _port(port)
  , _listenSocket(-1)
{ }

// Return a reference to a client instance which has data available to read.
Adafruit_CC3000_ClientRef Adafruit_CC3000_Server::available() {
  acceptNewConnections();
  // Find the first client which is ready to read and return it.
  for (int i = 0; i < MAX_SERVER_CLIENTS; ++i) {
    if (_clients[i].connected() && _clients[i].available() > 0) {
      return Adafruit_CC3000_ClientRef(&_clients[i]);
    }
  }
  // Couldn't find a client ready to read, so return a client that is not 
  // connected to signal no clients are available for reading (convention
  // used by the Ethernet library).
  return Adafruit_CC3000_ClientRef(NULL);
}

// Initialize the server and start listening for connections.
void Adafruit_CC3000_Server::begin() {
  // Set the CC3000 inactivity timeout to 0 (never timeout).  This will ensure 
  // the CC3000 does not close the listening socket when it's idle for more than 
  // 60 seconds (the default timeout).  See more information from:
  // http://e2e.ti.com/support/low_power_rf/f/851/t/292664.aspx
  unsigned long aucDHCP       = 14400;
  unsigned long aucARP        = 3600;
  unsigned long aucKeepalive  = 30;
  unsigned long aucInactivity = 0;
  cc3k_int_poll();
  if (netapp_timeout_values(&aucDHCP, &aucARP, &aucKeepalive, &aucInactivity) != 0) {
    CC3K_PRINTLN_F("Error setting inactivity timeout!");
    return;
  }
  // Create a TCP socket
  cc3k_int_poll();
  int16_t soc = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  if (soc < 0) {
    CC3K_PRINTLN_F("Couldn't create listening socket!");
    return;
  }
  // Set the socket's accept call as non-blocking.
  cc3k_int_poll();
  char arg = SOCK_ON; // nsd: looked in TI example code and they pass this as a 'short' in one example, and 'char' in two others. 'char' seems as likely work, and has no endianess issue
  if (setsockopt(soc, SOL_SOCKET, SOCKOPT_ACCEPT_NONBLOCK, &arg, sizeof(arg)) < 0) {
    CC3K_PRINTLN_F("Couldn't set socket as non-blocking!");
    return;
  }
  // Bind the socket to a TCP address.
  sockaddr_in address;
  address.sin_family = AF_INET;
  address.sin_addr.s_addr = htonl(0);     // Listen on any network interface, equivalent to INADDR_ANY in sockets programming.
  address.sin_port = htons(_port);        // Listen on the specified port.
  cc3k_int_poll();
  if (bind(soc, (sockaddr*) &address, sizeof(address)) < 0) {
    CC3K_PRINTLN_F("Error binding listen socket to address!");
    return;
  }
  // Start listening for connections.
  // The backlog parameter is 0 as it is not supported on TI's CC3000 firmware.
  cc3k_int_poll();
  if (listen(soc, 0) < 0) {
    CC3K_PRINTLN_F("Error opening socket for listening!");
    return;
  }
  _listenSocket = soc;
}

// Write data to all connected clients.  Buffer is a pointer to an array
// of bytes, and size specifies how many bytes to write from the buffer.
// Return the sum of bytes written to all clients.
size_t Adafruit_CC3000_Server::write(const uint8_t *buffer, size_t size) {
  size_t written = 0;
  for (int i = 0; i < MAX_SERVER_CLIENTS; ++i) {
    if (_clients[i].connected()) {
      written += _clients[i].write(buffer, size);
    }
  }
  return written;
}

// Write a byte value to all connected clients.
// Return the sum of bytes written to all clients.
size_t Adafruit_CC3000_Server::write(uint8_t value) {
  return write(&value, 1);
}

// Accept new connections and update the connected clients.
void Adafruit_CC3000_Server::acceptNewConnections() {
  // For any unconnected client, see if new connections are pending and accept
  // them as a new client.
  for (int i = 0; i < MAX_SERVER_CLIENTS; ++i) {
    if (!_clients[i].connected()) {
      // Note: Because the non-blocking option was set for the listening
      // socket this call will not block and instead return SOC_IN_PROGRESS (-2) 
      // if there are no pending client connections. Also, the address of the 
      // connected client is not needed, so those parameters are set to NULL.
      cc3k_int_poll();
      int soc = accept(_listenSocket, NULL, NULL);
      if (soc > -1) {
        _clients[i] = Adafruit_CC3000_Client(soc);
      }
      // else either there were no sockets to accept or an error occured.
    }
  }
}
