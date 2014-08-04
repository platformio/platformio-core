/**************************************************************************/
/*! 
  @file     Adafruit_CC3000_Server.h
  @author   Tony DiCola (tony@tonydicola.com)
  @license  BSD (see license.txt) 

  Adafruit CC3000 TCP server implementation based on the same interface as 
  the Arduino Ethernet library server class.

  See http://arduino.cc/en/Reference/Ethernet for documentation on the 
  Arduino Ethernet library and its server interface.

  The only difference between this implementation and the Ethernet library
  is that a special client reference facade is returned by the available()
  function, instead of a copy of a client like in the Ethernet library.  This
  is necessary to ensure the buffers that client instances contain aren't
  copied and get out of sync.

*/
/**************************************************************************/

#ifndef ADAFRUIT_CC3000_SERVER_H
#define ADAFRUIT_CC3000_SERVER_H

#include "Adafruit_CC3000.h"

#include "Print.h"
#include "Server.h"

// Assume 4 sockets available, 1 of which is used for listening, so at most 3 
// clients can be connected at once.
#define MAX_SERVER_CLIENTS 3 

// Facade that wraps a reference to a client instance into something that looks
// and acts like a client instance value.  This is done to mimic the semantics 
// of the Ethernet library, without running into problems allowing client buffers
// to be copied and get out of sync.
class Adafruit_CC3000_ClientRef : public Print {
 public:
  Adafruit_CC3000_ClientRef(Adafruit_CC3000_Client* client);
  // Return true if the referenced client is connected.  This is provided for
  // compatibility with Ethernet library code.
  operator bool();
  // Below are all the public methods of the client class:
  bool connected(void);
  size_t write(uint8_t c);

  size_t fastrprint(const char *str);
  size_t fastrprintln(const char *str);
  size_t fastrprint(char *str);
  size_t fastrprintln(char *str);
  size_t fastrprint(const __FlashStringHelper *ifsh);
  size_t fastrprintln(const __FlashStringHelper *ifsh);

  int16_t write(const void *buf, uint16_t len, uint32_t flags = 0);
  int16_t read(void *buf, uint16_t len, uint32_t flags = 0);
  uint8_t read(void);
  int32_t close(void);
  uint8_t available(void);

 private:
  // Hide the fact that users are really dealing with a pointer to a client
  // instance.  Note: this class does not own the contents of the client
  // pointer and should NEVER attempt to free/delete this pointer.
  Adafruit_CC3000_Client* _client;

};


class Adafruit_CC3000_Server : public Server {
public:
  // Construct a TCP server to listen on the specified port.
  Adafruit_CC3000_Server(uint16_t port);
  // Return a reference to a client instance which has data available to read.
  Adafruit_CC3000_ClientRef available();
  // Initialize the server and start listening for connections.
  virtual void begin();
  // Write data to all connected clients.  Buffer is a pointer to an array
  // of bytes, and size specifies how many bytes to write from the buffer.
  // Return the sum of bytes written to all clients.
  virtual size_t write(const uint8_t *buffer, size_t size);
  // Write a byte value to all connected clients.
  // Return the sum of bytes written to all clients.
  virtual size_t write(uint8_t value);
  // Make the overloads of write from the Print base class available.
  using Print::write;

private:
  // Store the clients in a simple array.
  Adafruit_CC3000_Client _clients[MAX_SERVER_CLIENTS];
  // The port this server will listen for connections on.
  uint16_t _port;
  // The id of the listening socket.
  uint16_t _listenSocket;

  // Accept new connections and update the connected clients.
  void acceptNewConnections();
};

#endif