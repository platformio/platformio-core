/**************************************************************************/
/*!
  @file     Adafruit_CC3000.cpp
  @author   KTOWN (Kevin Townsend for Adafruit Industries)
	@license  BSD (see license.txt)

	This is a library for the Adafruit CC3000 WiFi breakout board
	This library works with the Adafruit CC3000 breakout
	----> https://www.adafruit.com/products/1469

	Check out the links above for our tutorials and wiring diagrams
	These chips use SPI to communicate.

	Adafruit invests time and resources providing this open source code,
	please support Adafruit and open-source hardware by purchasing
	products from Adafruit!

	@section  HISTORY

	v1.0    - Initial release
*/
/**************************************************************************/
#include "Adafruit_CC3000.h"
#include "ccspi.h"

#include "utility/cc3000_common.h"
#include "utility/evnt_handler.h"
#include "utility/hci.h"
#include "utility/netapp.h"
#include "utility/nvmem.h"
#include "utility/security.h"
#include "utility/socket.h"
#include "utility/wlan.h"
#include "utility/debug.h"
#include "utility/sntp.h"

uint8_t g_csPin, g_irqPin, g_vbatPin, g_IRQnum, g_SPIspeed;

static const uint8_t dreqinttable[] = {
#if defined(__AVR_ATmega168__) || defined(__AVR_ATmega328P__) || defined (__AVR_ATmega328__) || defined(__AVR_ATmega8__) 
  2, 0,
  3, 1,
#elif defined(__AVR_ATmega1281__) || defined(__AVR_ATmega2561__) || defined(__AVR_ATmega2560__) || defined(__AVR_ATmega1280__) 
  2, 0,
  3, 1,
  21, 2, 
  20, 3,
  19, 4,
  18, 5,
#elif  defined(__AVR_ATmega32U4__) && defined(CORE_TEENSY)
  5, 0,
  6, 1,
  7, 2,
  8, 3,
#elif  defined(__AVR_AT90USB1286__) && defined(CORE_TEENSY)
  0, 0,
  1, 1,
  2, 2,
  3, 3,
  36, 4,
  37, 5,
  18, 6,
  19, 7,
#elif  defined(__arm__) && defined(CORE_TEENSY)
  0, 0, 1, 1, 2, 2, 3, 3, 4, 4,
  5, 5, 6, 6, 7, 7, 8, 8, 9, 9,
  10, 10, 11, 11, 12, 12, 13, 13, 14, 14,
  15, 15, 16, 16, 17, 17, 18, 18, 19, 19,
  20, 20, 21, 21, 22, 22, 23, 23, 24, 24,
  25, 25, 26, 26, 27, 27, 28, 28, 29, 29,
  30, 30, 31, 31, 32, 32, 33, 33,
#elif  defined(__AVR_ATmega32U4__) 
  7, 4,
  3, 0,
  2, 1,
  0, 2,
  1, 3,
#elif defined(__arm__) && defined(__SAM3X8E__) // Arduino Due  
  0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 
  5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 
  10, 10, 11, 11, 12, 12, 13, 13, 14, 14, 
  15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 
  20, 20, 21, 21, 22, 22, 23, 23, 24, 24, 
  25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 
  30, 30, 31, 31, 32, 32, 33, 33, 34, 34, 
  35, 35, 36, 36, 37, 37, 38, 38, 39, 39, 
  40, 40, 41, 41, 42, 42, 43, 43, 44, 44, 
  45, 45, 46, 46, 47, 47, 48, 48, 49, 49, 
  50, 50, 51, 51, 52, 52, 53, 53, 54, 54, 
  55, 55, 56, 56, 57, 57, 58, 58, 59, 59, 
  60, 60, 61, 61, 62, 62, 63, 63, 64, 64, 
  65, 65, 66, 66, 67, 67, 68, 68, 69, 69,
  70, 70, 71, 71,
#endif
};

/***********************/

uint8_t pingReportnum;
netapp_pingreport_args_t pingReport;

#define CC3000_SUCCESS                        (0)
#define CHECK_SUCCESS(func,Notify,errorCode)  {if ((func) != CC3000_SUCCESS) { CHECK_PRINTER CC3KPrinter->println(F(Notify)); return errorCode;}}

#define MAXSSID					  (32)
#define MAXLENGTHKEY 			(32)  /* Cleared for 32 bytes by TI engineering 29/08/13 */

#define MAX_SOCKETS 32  // can change this
boolean closed_sockets[MAX_SOCKETS] = {false, false, false, false};

/* *********************************************************************** */
/*                                                                         */
/* PRIVATE FIELDS (SmartConfig)                                            */
/*                                                                         */
/* *********************************************************************** */

class CC3000BitSet {
public:
  static const byte IsSmartConfigFinished = 0x01;
  static const byte IsConnected = 0x02;
  static const byte HasDHCP = 0x04;
  static const byte OkToShutDown = 0x08;

  void clear() {
    flags = 0;
  }

  bool test(const byte flag) {
    return (flags & flag) != 0;
  }

  void set(const byte flag) {
    flags |= flag;
  }

  void reset(const byte flag) {
    flags &= ~flag;
  }
private:
	volatile byte flags;
}cc3000Bitset;

volatile long ulSocket;
char _cc3000_prefix[] = { 'T', 'T', 'T' };
Print* CC3KPrinter; // user specified output stream for general messages and debug

/* *********************************************************************** */
/*                                                                         */
/* PRIVATE FUNCTIONS                                                       */
/*                                                                         */
/* *********************************************************************** */

/**************************************************************************/
/*!
    @brief    Scans for SSID/APs in the CC3000's range

    @note     This command isn't available when the CC3000 is configured
              in 'CC3000_TINY_DRIVER' mode

    @returns  False if an error occured!
*/
/**************************************************************************/
#ifndef CC3000_TINY_DRIVER
bool Adafruit_CC3000::scanSSIDs(uint32_t time)
{
  const unsigned long intervalTime[16] = { 2000, 2000, 2000, 2000,  2000,
    2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000 };

  if (!_initialised)
  {
    return false;
  }

  // We can abort a scan with a time of 0
  if (time)
  {
    CHECK_PRINTER {
      CC3KPrinter->println(F("Started AP/SSID scan\n\r"));
    }
  }

  // Set  SSID Scan params to includes channels above 11 
  CHECK_SUCCESS(
      wlan_ioctl_set_scan_params(time, 20, 100, 5, 0x1FFF, -120, 0, 300,
          (unsigned long * ) &intervalTime),
          "Failed setting params for SSID scan", false);

  return true;
}
#endif

/* *********************************************************************** */
/*                                                                         */
/* CONSTRUCTORS                                                            */
/*                                                                         */
/* *********************************************************************** */

/**************************************************************************/
/*!
    @brief  Instantiates a new CC3000 class
*/
/**************************************************************************/
Adafruit_CC3000::Adafruit_CC3000(uint8_t csPin, uint8_t irqPin, uint8_t vbatPin, uint8_t SPIspeed)
{
  _initialised = false;
  g_csPin = csPin;
  g_irqPin = irqPin;
  g_vbatPin = vbatPin;
  g_IRQnum = 0xFF;
  g_SPIspeed = SPIspeed;

  cc3000Bitset.clear();

  #if defined(UDR0) || defined(UDR1) || defined(CORE_TEENSY) || ( defined (__arm__) && defined (__SAM3X8E__) )
  CC3KPrinter = &Serial;
  #else
  CC3KPrinter = 0;
  // no default serial port found
  #endif
}

/* *********************************************************************** */
/*                                                                         */
/* PUBLIC FUNCTIONS                                                        */
/*                                                                         */
/* *********************************************************************** */

/**************************************************************************/
/*!
    @brief  Setups the HW
    
    @args[in] patchReq  
              Set this to true if we are starting a firmware patch,
              otherwise false for normal operation
    @args[in] useSmartConfig
              Set this to true if you want to use the connection details
              that were stored on the device from the SmartConfig process,
              otherwise false to erase existing profiles and start a
              clean connection
*/
/**************************************************************************/
bool Adafruit_CC3000::begin(uint8_t patchReq, bool useSmartConfigData, const char *_deviceName)
{
  if (_initialised) return true;

  #ifndef CORE_ADAX
  // determine irq #
  for (uint8_t i=0; i<sizeof(dreqinttable); i+=2) {
    if (g_irqPin == dreqinttable[i]) {
      g_IRQnum = dreqinttable[i+1];
    }
  }
  if (g_IRQnum == 0xFF) {
    CHECK_PRINTER {
      CC3KPrinter->println(F("IRQ pin is not an INT pin!"));
    }
    return false;
  }
  #else
  g_IRQnum = g_irqPin;
  // (almost) every single pin on Xmega supports interrupt
  #endif

  init_spi();
  
  DEBUGPRINT_F("init\n\r");
  wlan_init(CC3000_UsynchCallback,
            sendWLFWPatch, sendDriverPatch, sendBootLoaderPatch,
            ReadWlanInterruptPin,
            WlanInterruptEnable,
            WlanInterruptDisable,
            WriteWlanPin);
  DEBUGPRINT_F("start\n\r");

  wlan_start(patchReq);
  
  DEBUGPRINT_F("ioctl\n\r");
  // Check if we should erase previous stored connection details
  // (most likely written with data from the SmartConfig app)
  if (!useSmartConfigData)
  {
    // Manual connection only (no auto, profiles, etc.)
    wlan_ioctl_set_connection_policy(0, 0, 0);
    // Delete previous profiles from memory
    wlan_ioctl_del_profile(255);
  }
  else
  {
    // Auto Connect - the C3000 device tries to connect to any AP it detects during scanning:
    // wlan_ioctl_set_connection_policy(1, 0, 0)
    
    // Fast Connect - the CC3000 device tries to reconnect to the last AP connected to:
    // wlan_ioctl_set_connection_policy(0, 1, 0)

    // Use Profiles - the CC3000 device tries to connect to an AP from profiles:
    wlan_ioctl_set_connection_policy(0, 0, 1);
  }

  CHECK_SUCCESS(
    wlan_set_event_mask(HCI_EVNT_WLAN_UNSOL_INIT        |
                        //HCI_EVNT_WLAN_ASYNC_PING_REPORT |// we want ping reports
                        //HCI_EVNT_BSD_TCP_CLOSE_WAIT |
                        //HCI_EVNT_WLAN_TX_COMPLETE |
                        HCI_EVNT_WLAN_KEEPALIVE),
                        "WLAN Set Event Mask FAIL", false);

  _initialised = true;

  // Wait for re-connection if we're using SmartConfig data
  if (useSmartConfigData)
  {
    // Wait for a connection
    uint32_t timeout = 0;
    while(!cc3000Bitset.test(CC3000BitSet::IsConnected))
    {
      cc3k_int_poll();
      if(timeout > WLAN_CONNECT_TIMEOUT)
      {
        CHECK_PRINTER {
          CC3KPrinter->println(F("Timed out using SmartConfig data"));
        }
        return false;
      }
      timeout += 10;
      delay(10);
    }
    
    delay(1000);  
    if (cc3000Bitset.test(CC3000BitSet::HasDHCP))
    {
      mdnsAdvertiser(1, (char *) _deviceName, strlen(_deviceName));
    }
  }
    
  return true;
}

/**************************************************************************/
/*!
    @brief  Prints a hexadecimal value in plain characters

    @param  data      Pointer to the byte data
    @param  numBytes  Data length in bytes
*/
/**************************************************************************/
void Adafruit_CC3000::printHex(const byte * data, const uint32_t numBytes)
{
  if (CC3KPrinter == 0) return;

  uint32_t szPos;
  for (szPos=0; szPos < numBytes; szPos++)
  {
    CC3KPrinter->print(F("0x"));
    // Append leading 0 for small values
    if (data[szPos] <= 0xF)
      CC3KPrinter->print(F("0"));
    CC3KPrinter->print(data[szPos], HEX);
    if ((numBytes > 1) && (szPos != numBytes - 1))
    {
      CC3KPrinter->print(' ');
    }
  }
  CC3KPrinter->println();
}

/**************************************************************************/
/*!
    @brief  Prints a hexadecimal value in plain characters, along with
            the char equivalents in the following format

            00 00 00 00 00 00  ......

    @param  data      Pointer to the byte data
    @param  numBytes  Data length in bytes
*/
/**************************************************************************/
void Adafruit_CC3000::printHexChar(const byte * data, const uint32_t numBytes)
{
  if (CC3KPrinter == 0) return;

  uint32_t szPos;
  for (szPos=0; szPos < numBytes; szPos++)
  {
    // Append leading 0 for small values
    if (data[szPos] <= 0xF)
      CC3KPrinter->print('0');
    CC3KPrinter->print(data[szPos], HEX);
    if ((numBytes > 1) && (szPos != numBytes - 1))
    {
      CC3KPrinter->print(' ');
    }
  }
  CC3KPrinter->print("  ");
  for (szPos=0; szPos < numBytes; szPos++)
  {
    if (data[szPos] <= 0x1F)
      CC3KPrinter->print('.');
    else
      CC3KPrinter->print(data[szPos]);
  }
  CC3KPrinter->println();
}

/**************************************************************************/
/*!
    @brief  Helper function to display an IP address with dots
*/
/**************************************************************************/

void Adafruit_CC3000::printIPdots(uint32_t ip) {
  if (CC3KPrinter == 0) return;
  CC3KPrinter->print((uint8_t)(ip));
  CC3KPrinter->print('.');
  CC3KPrinter->print((uint8_t)(ip >> 8));
  CC3KPrinter->print('.');
  CC3KPrinter->print((uint8_t)(ip >> 16));
  CC3KPrinter->print('.');
  CC3KPrinter->print((uint8_t)(ip >> 24));  
}

/**************************************************************************/
/*!
    @brief  Helper function to display an IP address with dots, printing
            the bytes in reverse order
*/
/**************************************************************************/
void Adafruit_CC3000::printIPdotsRev(uint32_t ip) {
  if (CC3KPrinter == 0) return;
  CC3KPrinter->print((uint8_t)(ip >> 24));
  CC3KPrinter->print('.');
  CC3KPrinter->print((uint8_t)(ip >> 16));
  CC3KPrinter->print('.');
  CC3KPrinter->print((uint8_t)(ip >> 8));
  CC3KPrinter->print('.');
  CC3KPrinter->print((uint8_t)(ip));  
}

/**************************************************************************/
/*!
    @brief  Helper function to convert four bytes to a U32 IP value
*/
/**************************************************************************/
uint32_t Adafruit_CC3000::IP2U32(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
  uint32_t ip = a;
  ip <<= 8;
  ip |= b;
  ip <<= 8;
  ip |= c;
  ip <<= 8;
  ip |= d;

  return ip;
}

/**************************************************************************/
/*!
    @brief   Reboot CC3000 (stop then start)
*/
/**************************************************************************/
void Adafruit_CC3000::reboot(uint8_t patch)
{
  if (!_initialised)
  {
    return;
  }

  wlan_stop();
  delay(5000);
  wlan_start(patch);
}

/**************************************************************************/
/*!
    @brief   Stop CC3000
*/
/**************************************************************************/
void Adafruit_CC3000::stop(void)
{
  if (!_initialised)
  {
    return;
  }

  wlan_stop();
}

/**************************************************************************/
/*!
    @brief  Disconnects from the network

    @returns  False if an error occured!
*/
/**************************************************************************/
bool Adafruit_CC3000::disconnect(void)
{
  if (!_initialised)
  {
    return false;
  }

  long retVal = wlan_disconnect();

  return retVal != 0 ? false : true;
}

/**************************************************************************/
/*!
    @brief   Deletes all profiles stored in the CC3000

    @returns  False if an error occured!
*/
/**************************************************************************/
bool Adafruit_CC3000::deleteProfiles(void)
{
  if (!_initialised)
  {
    return false;
  }

  CHECK_SUCCESS(wlan_ioctl_set_connection_policy(0, 0, 0),
               "deleteProfiles connection failure", false);
  CHECK_SUCCESS(wlan_ioctl_del_profile(255),
               "Failed deleting profiles", false);

  return true;
}

/**************************************************************************/
/*!
    @brief    Reads the MAC address

    @param    address  Buffer to hold the 6 byte Mac Address

    @returns  False if an error occured!
*/
/**************************************************************************/
bool Adafruit_CC3000::getMacAddress(uint8_t address[6])
{
  if (!_initialised)
  {
    return false;
  }

  CHECK_SUCCESS(nvmem_read(NVMEM_MAC_FILEID, 6, 0, address),
                "Failed reading MAC address!", false);

  return true;
}

/**************************************************************************/
/*!
    @brief    Sets a new MAC address

    @param    address   Buffer pointing to the 6 byte Mac Address

    @returns  False if an error occured!
*/
/**************************************************************************/
bool Adafruit_CC3000::setMacAddress(uint8_t address[6])
{
  if (!_initialised)
  {
    return false;
  }

  if (address[0] == 0)
  {
    return false;
  }

  CHECK_SUCCESS(netapp_config_mac_adrress(address),
                "Failed setting MAC address!", false);

  wlan_stop();
  delay(200);
  wlan_start(0);

  return true;
}

/**************************************************************************/
/*!
    @brief    Set the CC3000 to use a static IP address when it's connected
              to the network.  Use the cc3000.IP2U32 function to specify the
              IP, subnet mask (typically 255.255.255.0), default gateway
              (typically 192.168.1.1), and DNS server (can use Google's DNS
              of 8.8.8.8 or 8.8.4.4).  Note that the static IP configuration
              will be saved in the CC3000's non-volatile storage and reused
              on next reconnect.  This means you only need to call this once
              and the CC3000 will remember the setting forever.  To revert
              back to use DHCP, call the cc3000.setDHCP function.

    @param    ip               IP address
    @param    subnetmask       Subnet mask
    @param    defaultGateway   Default gateway
    @param    dnsServer        DNS server

    @returns  False if an error occurred, true if successfully set.
*/
/**************************************************************************/
bool Adafruit_CC3000::setStaticIPAddress(uint32_t ip, uint32_t subnetMask, uint32_t defaultGateway, uint32_t dnsServer)
{
  // Reverse order of bytes in parameters so IP2U32 packed values can be used with the netapp_dhcp function.
  ip = (ip >> 24) | ((ip >> 8) & 0x0000FF00L) | ((ip << 8) & 0x00FF0000L) | (ip << 24);
  subnetMask = (subnetMask >> 24) | ((subnetMask >> 8) & 0x0000FF00L) | ((subnetMask << 8) & 0x00FF0000L) | (subnetMask << 24);
  defaultGateway = (defaultGateway >> 24) | ((defaultGateway >> 8) & 0x0000FF00L) | ((defaultGateway << 8) & 0x00FF0000L) | (defaultGateway << 24);
  dnsServer = (dnsServer >> 24) | ((dnsServer >> 8) & 0x0000FF00L) | ((dnsServer << 8) & 0x00FF0000L) | (dnsServer << 24);
  // Update DHCP state with specified values.
  if (netapp_dhcp(&ip, &subnetMask, &defaultGateway, &dnsServer) != 0) {
    return false;
  }
  // Reset CC3000 to use modified setting.
  wlan_stop();
  delay(200);
  wlan_start(0);
  return true;
}

/**************************************************************************/
/*!
    @brief    Set the CC3000 to use request an IP and network configuration
              using DHCP.  Note that this DHCP state will be saved in the 
              CC3000's non-volatile storage and reused on next reconnect.
              This means you only need to call this once and the CC3000 will 
              remember the setting forever.  To switch to use a static IP,
              call the cc3000.setStaticIPAddress function.

    @returns  False if an error occurred, true if successfully set.
*/
/**************************************************************************/
bool Adafruit_CC3000::setDHCP()
{
  return setStaticIPAddress(0,0,0,0);
}

/**************************************************************************/
/*!
    @brief   Reads the current IP address

    @returns  False if an error occured!
*/
/**************************************************************************/
bool Adafruit_CC3000::getIPAddress(uint32_t *retip, uint32_t *netmask, uint32_t *gateway, uint32_t *dhcpserv, uint32_t *dnsserv)
{
  if (!_initialised) return false;
  if (!cc3000Bitset.test(CC3000BitSet::IsConnected)) return false;
  if (!cc3000Bitset.test(CC3000BitSet::HasDHCP)) return false;

  tNetappIpconfigRetArgs ipconfig;
  netapp_ipconfig(&ipconfig);

  /* If byte 1 is 0 we don't have a valid address */
  if (ipconfig.aucIP[3] == 0) return false;

  memcpy(retip, ipconfig.aucIP, 4);
  memcpy(netmask, ipconfig.aucSubnetMask, 4);
  memcpy(gateway, ipconfig.aucDefaultGateway, 4);
  memcpy(dhcpserv, ipconfig.aucDHCPServer, 4);
  memcpy(dnsserv, ipconfig.aucDNSServer, 4);

  return true;
}

/**************************************************************************/
/*!
    @brief    Gets the two byte ID for the firmware patch version

    @note     This command isn't available when the CC3000 is configured
              in 'CC3000_TINY_DRIVER' mode

    @returns  False if an error occured!
*/
/**************************************************************************/
#ifndef CC3000_TINY_DRIVER
bool Adafruit_CC3000::getFirmwareVersion(uint8_t *major, uint8_t *minor)
{
  uint8_t fwpReturn[2];

  if (!_initialised)
  {
    return false;
  }

  CHECK_SUCCESS(nvmem_read_sp_version(fwpReturn),
                "Unable to read the firmware version", false);

  *major = fwpReturn[0];
  *minor = fwpReturn[1];

  return true;
}
#endif

/**************************************************************************/
/*!
    @Brief   Prints out the current status flag of the CC3000

    @note     This command isn't available when the CC3000 is configured
              in 'CC3000_TINY_DRIVER' mode
*/
/**************************************************************************/
#ifndef CC3000_TINY_DRIVER
status_t Adafruit_CC3000::getStatus()
{
  if (!_initialised)
  {
    return STATUS_DISCONNECTED;
  }

  long results = wlan_ioctl_statusget();

  switch(results)
  {
    case 1:
      return STATUS_SCANNING;
      break;
    case 2:
      return STATUS_CONNECTING;
      break;
    case 3:
      return STATUS_CONNECTED;
      break;
    case 0:
    default:
      return STATUS_DISCONNECTED;
      break;
  }
}
#endif

/**************************************************************************/
/*!
    @brief    Calls listSSIDs and then displays the results of the SSID scan

              For the moment we only list these via CC3KPrinter->print since
              this can consume a lot of memory passing all the data
              back with a buffer

    @note     This command isn't available when the CC3000 is configured
              in 'CC3000_TINY_DRIVER' mode

    @returns  False if an error occured!
*/
/**************************************************************************/
#ifndef CC3000_TINY_DRIVER

ResultStruct_t SSIDScanResultBuff;


uint16_t Adafruit_CC3000::startSSIDscan() {
  uint16_t   index = 0;

  if (!_initialised)
  {
    return false;
  }

  // Setup a 4 second SSID scan
  if (!scanSSIDs(4000))
  {
    // Oops ... SSID scan failed
    return false;
  }

  // Wait for results
  delay(4500);

  CHECK_SUCCESS(wlan_ioctl_get_scan_results(0, (uint8_t* ) &SSIDScanResultBuff),
                "SSID scan failed!", false);

  index = SSIDScanResultBuff.num_networks;
  return index;
}

void Adafruit_CC3000::stopSSIDscan(void) {

  // Stop scanning
  scanSSIDs(0);
}

uint8_t Adafruit_CC3000::getNextSSID(uint8_t *rssi, uint8_t *secMode, char *ssidname) {
    uint8_t valid = (SSIDScanResultBuff.rssiByte & (~0xFE));
    *rssi = (SSIDScanResultBuff.rssiByte >> 1);
    *secMode = (SSIDScanResultBuff.Sec_ssidLen & (~0xFC));
    uint8_t ssidLen = (SSIDScanResultBuff.Sec_ssidLen >> 2);
    strncpy(ssidname, (char *)SSIDScanResultBuff.ssid_name, ssidLen);
    ssidname[ssidLen] = 0;

    CHECK_SUCCESS(wlan_ioctl_get_scan_results(0, (uint8_t* ) &SSIDScanResultBuff),
                  "Problem with the SSID scan results", false);
    return valid;
}
#endif

/**************************************************************************/
/*!
    @brief    Starts the smart config connection process

    @note     This command isn't available when the CC3000 is configured
              in 'CC3000_TINY_DRIVER' mode

    @returns  False if an error occured!
*/
/**************************************************************************/
#ifndef CC3000_TINY_DRIVER
bool Adafruit_CC3000::startSmartConfig(const char *_deviceName, const char *smartConfigKey)
{
  bool enableAES = smartConfigKey != NULL;
  cc3000Bitset.clear();

  uint32_t   timeout = 0;

  if (!_initialised) {
    return false;
  }

  // Reset all the previous configurations
  CHECK_SUCCESS(wlan_ioctl_set_connection_policy(WIFI_DISABLE, WIFI_DISABLE, WIFI_DISABLE),
                "Failed setting the connection policy", false);
  
  // Delete existing profile data
  CHECK_SUCCESS(wlan_ioctl_del_profile(255),
                "Failed deleting existing profiles", false);

  // CC3KPrinter->println("Disconnecting");
  // Wait until CC3000 is disconnected
  while (cc3000Bitset.test(CC3000BitSet::IsConnected)) {
    cc3k_int_poll();
    CHECK_SUCCESS(wlan_disconnect(),
                  "Failed to disconnect from AP", false);
    delay(10);
    hci_unsolicited_event_handler();
  }

  // Reset the CC3000
  wlan_stop();
  delay(1000);
  wlan_start(0);

  // create new entry for AES encryption key
  CHECK_SUCCESS(nvmem_create_entry(NVMEM_AES128_KEY_FILEID,16),
                "Failed create NVMEM entry", false);
  
  if (enableAES)
  {
    // write AES key to NVMEM
    CHECK_SUCCESS(aes_write_key((unsigned char *)(smartConfigKey)),
                  "Failed writing AES key", false);  
  }  
  //CC3KPrinter->println("Set prefix");
  // Wait until CC3000 is disconnected
  CHECK_SUCCESS(wlan_smart_config_set_prefix((char *)&_cc3000_prefix),
                "Failed setting the SmartConfig prefix", false);

  //CC3KPrinter->println("Start config");
  // Start the SmartConfig start process
  CHECK_SUCCESS(wlan_smart_config_start(enableAES),
                "Failed starting smart config", false);

  // Wait for smart config process complete (event in CC3000_UsynchCallback)
  while (!cc3000Bitset.test(CC3000BitSet::IsSmartConfigFinished))
  {
    cc3k_int_poll();
    // waiting here for event SIMPLE_CONFIG_DONE
    timeout+=10;
    if (timeout > 60000)   // ~60s
    {
      return false;
    }
    delay(10); // ms
    //  CC3KPrinter->print('.');
  }

  CHECK_PRINTER {
	CC3KPrinter->println(F("Got smart config data"));
  }
  if (enableAES) {
    CHECK_SUCCESS(wlan_smart_config_process(),
                 "wlan_smart_config_process failed",
                 false);
  }
  
  // ******************************************************
  // Decrypt configuration information and add profile
  // ToDo: This is causing stack overflow ... investigate
  // CHECK_SUCCESS(wlan_smart_config_process(),
  //             "Smart config failed", false);
  // ******************************************************

  // Connect automatically to the AP specified in smart config settings
  CHECK_SUCCESS(wlan_ioctl_set_connection_policy(WIFI_DISABLE, WIFI_DISABLE, WIFI_ENABLE),
                "Failed setting connection policy", false);
  
  // Reset the CC3000
  wlan_stop();
  delay(1000);
  wlan_start(0);
  
  // Mask out all non-required events
  CHECK_SUCCESS(wlan_set_event_mask(HCI_EVNT_WLAN_KEEPALIVE |
                HCI_EVNT_WLAN_UNSOL_INIT 
                //HCI_EVNT_WLAN_ASYNC_PING_REPORT |
                //HCI_EVNT_WLAN_TX_COMPLETE
                ),
                "Failed setting event mask", false);  

  // Wait for a connection
  timeout = 0;
  while(!cc3000Bitset.test(CC3000BitSet::IsConnected))
  {
    cc3k_int_poll();
    if(timeout > WLAN_CONNECT_TIMEOUT) // ~20s
    {
      CHECK_PRINTER {
        CC3KPrinter->println(F("Timed out waiting to connect"));
      }
      return false;
    }
    timeout += 10;
    delay(10);
  }
  
  delay(1000);  
  if (cc3000Bitset.test(CC3000BitSet::HasDHCP))
  {
    mdnsAdvertiser(1, (char *) _deviceName, strlen(_deviceName));
  }
  
  return true;
}

#endif

/**************************************************************************/
/*!
    Connect to an unsecured SSID/AP(security)

    @param  ssid      The named of the AP to connect to (max 32 chars)
    @param  ssidLen   The size of the ssid name

    @returns  False if an error occured!
*/
/**************************************************************************/
bool Adafruit_CC3000::connectOpen(const char *ssid)
{
  if (!_initialised) {
    return false;
  }

  #ifndef CC3000_TINY_DRIVER
    CHECK_SUCCESS(wlan_ioctl_set_connection_policy(0, 0, 0),
                 "Failed to set connection policy", false);
    delay(500);
    CHECK_SUCCESS(wlan_connect(WLAN_SEC_UNSEC,
					(const char*)ssid, strlen(ssid),
					0 ,NULL,0),
					"SSID connection failed", false);
  #else
    wlan_connect(ssid, ssidLen);
  #endif

  return true;
}

//*****************************************************************************
//
//! CC3000_UsynchCallback
//!
//! @param  lEventType Event type
//! @param  data
//! @param  length
//!
//! @return none
//!
//! @brief  The function handles asynchronous events that come from CC3000
//!         device and operates a led for indicate
//
//*****************************************************************************
void CC3000_UsynchCallback(long lEventType, char * data, unsigned char length)
{
  if (lEventType == HCI_EVNT_WLAN_ASYNC_SIMPLE_CONFIG_DONE)
  {
    cc3000Bitset.set(CC3000BitSet::IsSmartConfigFinished);
  }

  if (lEventType == HCI_EVNT_WLAN_UNSOL_CONNECT)
  {
    cc3000Bitset.set(CC3000BitSet::IsConnected);
  }

  if (lEventType == HCI_EVNT_WLAN_UNSOL_DISCONNECT)
  {
	cc3000Bitset.reset(CC3000BitSet::IsConnected | CC3000BitSet::HasDHCP);
  }
  
  if (lEventType == HCI_EVNT_WLAN_UNSOL_DHCP)
  {
    cc3000Bitset.set(CC3000BitSet::HasDHCP);
  }

  if (lEventType == HCI_EVENT_CC3000_CAN_SHUT_DOWN)
  {
    cc3000Bitset.set(CC3000BitSet::OkToShutDown);
  }

  if (lEventType == HCI_EVNT_WLAN_ASYNC_PING_REPORT)
  {
    //PRINT_F("CC3000: Ping report\n\r");
    pingReportnum++;
    memcpy(&pingReport, data, length);
  }

  if (lEventType == HCI_EVNT_BSD_TCP_CLOSE_WAIT) {
    uint8_t socketnum;
    socketnum = data[0];
    //PRINT_F("TCP Close wait #"); printDec(socketnum);
    if (socketnum < MAX_SOCKETS)
      closed_sockets[socketnum] = true;
  }
}

/**************************************************************************/
/*!
    Connect to an SSID/AP(security)

    @note     This command isn't available when the CC3000 is configured
              in 'CC3000_TINY_DRIVER' mode

    @returns  False if an error occured!
*/
/**************************************************************************/
#ifndef CC3000_TINY_DRIVER
bool Adafruit_CC3000::connectSecure(const char *ssid, const char *key, int32_t secMode)
{
  if (!_initialised) {
    return false;
  }
  
  if ( (secMode < 0) || (secMode > 3)) {
    CHECK_PRINTER {
		CC3KPrinter->println(F("Security mode must be between 0 and 3"));
	}
    return false;
  }

  if (strlen(ssid) > MAXSSID) {
    CHECK_PRINTER {
      CC3KPrinter->print(F("SSID length must be < "));
      CC3KPrinter->println(MAXSSID);
    }
    return false;
  }

  if (strlen(key) > MAXLENGTHKEY) {
    CHECK_PRINTER {
      CC3KPrinter->print(F("Key length must be < "));
      CC3KPrinter->println(MAXLENGTHKEY);
    }
    return false;
  }

  CHECK_SUCCESS(wlan_ioctl_set_connection_policy(0, 0, 0),
                "Failed setting the connection policy",
                false);
  delay(500);
  CHECK_SUCCESS(wlan_connect(secMode, (char *)ssid, strlen(ssid),
                             NULL,
                             (unsigned char *)key, strlen(key)),
                "SSID connection failed", false);

  /* Wait for 'HCI_EVNT_WLAN_UNSOL_CONNECT' in CC3000_UsynchCallback */

  return true;
}
#endif

// Connect with timeout
bool Adafruit_CC3000::connectToAP(const char *ssid, const char *key, uint8_t secmode, uint8_t attempts) {
  if (!_initialised) {
    return false;
  }

  int16_t timer;

  // If attempts is zero interpret that as no limit on number of retries.
  bool retryForever = attempts == 0;

  do {
    // Stop if the max number of attempts have been tried.
    if (!retryForever) {
      if (attempts == 0) {
        return checkConnected();
      }
      attempts -= 1;
    }

    cc3k_int_poll();
    /* MEME: not sure why this is absolutely required but the cc3k freaks
       if you dont. maybe bootup delay? */
    // Setup a 4 second SSID scan
    scanSSIDs(4000);
    // Wait for results
    delay(4500);
    scanSSIDs(0);
    
    /* Attempt to connect to an access point */
    CHECK_PRINTER {
      CC3KPrinter->print(F("\n\rConnecting to ")); 
      CC3KPrinter->print(ssid);
      CC3KPrinter->print(F("..."));
    }
    if ((secmode == 0) || (strlen(key) == 0)) {
      /* Connect to an unsecured network */
      if (! connectOpen(ssid)) {
        CHECK_PRINTER {
			    CC3KPrinter->println(F("Failed!"));
		    }
        continue;
      }
    } else {
      /* NOTE: Secure connections are not available in 'Tiny' mode! */
#ifndef CC3000_TINY_DRIVER
      /* Connect to a secure network using WPA2, etc */
      if (! connectSecure(ssid, key, secmode)) {
        CHECK_PRINTER {
			    CC3KPrinter->println(F("Failed!"));
		    }
        continue;
      }
#endif
    }
	  
    timer = WLAN_CONNECT_TIMEOUT;

    /* Wait around a bit for the async connected signal to arrive or timeout */
    CHECK_PRINTER {
		  CC3KPrinter->print(F("Waiting to connect..."));
	  }
    while ((timer > 0) && !checkConnected())
    {
      cc3k_int_poll();
      delay(10);
      timer -= 10;
    }
    if (timer <= 0) {
      CHECK_PRINTER {
		    CC3KPrinter->println(F("Timed out!"));
	    }
    }
  } while (!checkConnected());

  return true;
}


#ifndef CC3000_TINY_DRIVER
uint16_t Adafruit_CC3000::ping(uint32_t ip, uint8_t attempts, uint16_t timeout, uint8_t size) {
  if (!_initialised) return 0;
  if (!cc3000Bitset.test(CC3000BitSet::IsConnected)) return 0;
  if (!cc3000Bitset.test(CC3000BitSet::HasDHCP)) return 0;

  uint32_t revIP = (ip >> 24) | ((ip >> 8) & 0xFF00) | ((ip & 0xFF00) << 8) | (ip << 24);

  pingReportnum = 0;
  pingReport.packets_received = 0;

  //if (CC3KPrinter != 0) {
  //  CC3KPrinter->print(F("Pinging ")); printIPdots(revIP); CC3KPrinter->print(" ");
  //  CC3KPrinter->print(attempts); CC3KPrinter->println(F(" times"));
  //}
  
  netapp_ping_send(&revIP, attempts, size, timeout);
  delay(timeout*attempts*2);
  //if (CC3KPrinter != 0) CC3KPrinter->println(F("Req report"));
  //netapp_ping_report();
  //if (CC3KPrinter != 0) { CC3KPrinter->print(F("Reports: ")); CC3KPrinter->println(pingReportnum); }

  if (pingReportnum) {
    /*
    if (CC3KPrinter != 0) {
      CC3KPrinter->print(F("Sent: ")); CC3KPrinter->println(pingReport.packets_sent);
      CC3KPrinter->print(F("Recv: ")); CC3KPrinter->println(pingReport.packets_received);
      CC3KPrinter->print(F("MinT: ")); CC3KPrinter->println(pingReport.min_round_time);
      CC3KPrinter->print(F("MaxT: ")); CC3KPrinter->println(pingReport.max_round_time);
      CC3KPrinter->print(F("AvgT: ")); CC3KPrinter->println(pingReport.avg_round_time);
    }
    //*/
    return pingReport.packets_received;
  } else {
    return 0;
  }
}

#endif

#ifndef CC3000_TINY_DRIVER
uint16_t Adafruit_CC3000::getHostByName(char *hostname, uint32_t *ip) {
  if (!_initialised) return 0;
  if (!cc3000Bitset.test(CC3000BitSet::IsConnected)) return 0;
  if (!cc3000Bitset.test(CC3000BitSet::HasDHCP)) return 0;

  int16_t r = gethostbyname(hostname, strlen(hostname), ip);
  //if (CC3KPrinter != 0) { CC3KPrinter->print("Errno: "); CC3KPrinter->println(r); }
  return r;
}
#endif

/**************************************************************************/
/*!
    Checks if the device is connected or not

    @returns  True if connected
*/
/**************************************************************************/
bool Adafruit_CC3000::checkConnected(void)
{
  return cc3000Bitset.test(CC3000BitSet::IsConnected);
}

/**************************************************************************/
/*!
    Checks if the DHCP process is complete or not

    @returns  True if DHCP process is complete (IP address assigned)
*/
/**************************************************************************/
bool Adafruit_CC3000::checkDHCP(void)
{
  return cc3000Bitset.test(CC3000BitSet::HasDHCP);
}

/**************************************************************************/
/*!
    Checks if the smart config process is finished or not

    @returns  True if smart config is finished
*/
/**************************************************************************/
bool Adafruit_CC3000::checkSmartConfigFinished(void)
{
  return cc3000Bitset.test(CC3000BitSet::IsSmartConfigFinished);
}

#ifndef CC3000_TINY_DRIVER
/**************************************************************************/
/*!
    Gets the IP config settings (if connected)

    @returns  True if smart config is finished
*/
/**************************************************************************/
bool Adafruit_CC3000::getIPConfig(tNetappIpconfigRetArgs *ipConfig)
{
  if (!_initialised)      return false;
  if (!cc3000Bitset.test(CC3000BitSet::IsConnected)) return false;
  if (!cc3000Bitset.test(CC3000BitSet::HasDHCP))      return false;
  
  netapp_ipconfig(ipConfig);
  return true;
}
#endif


/**************************************************************************/
/*!
    @brief  Quick socket test to pull contents from the web
*/
/**************************************************************************/
Adafruit_CC3000_Client Adafruit_CC3000::connectTCP(uint32_t destIP, uint16_t destPort)
{
  sockaddr      socketAddress;
  int32_t       tcp_socket;

  // Create the socket(s)
  //if (CC3KPrinter != 0) CC3KPrinter->print(F("Creating socket ... "));
  tcp_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
  if (-1 == tcp_socket)
  {
    CHECK_PRINTER {
		CC3KPrinter->println(F("Failed to open socket"));
	}
    return Adafruit_CC3000_Client();
  }
  //CC3KPrinter->print(F("DONE (socket ")); CC3KPrinter->print(tcp_socket); CC3KPrinter->println(F(")"));

  closed_sockets[tcp_socket] = false; // Clear any previous closed event

  // Try to open the socket
  memset(&socketAddress, 0x00, sizeof(socketAddress));
  socketAddress.sa_family = AF_INET;
  socketAddress.sa_data[0] = (destPort & 0xFF00) >> 8;  // Set the Port Number
  socketAddress.sa_data[1] = (destPort & 0x00FF);
  socketAddress.sa_data[2] = destIP >> 24;
  socketAddress.sa_data[3] = destIP >> 16;
  socketAddress.sa_data[4] = destIP >> 8;
  socketAddress.sa_data[5] = destIP;

  CHECK_PRINTER {
    CC3KPrinter->print(F("\n\rConnect to "));
    printIPdotsRev(destIP);
    CC3KPrinter->print(':');
    CC3KPrinter->println(destPort);
  }

  //printHex((byte *)&socketAddress, sizeof(socketAddress));
  //if (CC3KPrinter != 0) CC3KPrinter->print(F("Connecting socket ... "));
  if (-1 == connect(tcp_socket, &socketAddress, sizeof(socketAddress)))
  {
    CHECK_PRINTER {
		CC3KPrinter->println(F("Connection error"));
	}
    closesocket(tcp_socket);
    return Adafruit_CC3000_Client();
  }
  //if (CC3KPrinter != 0) CC3KPrinter->println(F("DONE"));
  return Adafruit_CC3000_Client(tcp_socket);
}


Adafruit_CC3000_Client Adafruit_CC3000::connectUDP(uint32_t destIP, uint16_t destPort)
{
  sockaddr      socketAddress;
  int32_t       udp_socket;

  // Create the socket(s)
  // socket   = SOCK_STREAM, SOCK_DGRAM, or SOCK_RAW 
  // protocol = IPPROTO_TCP, IPPROTO_UDP or IPPROTO_RAW
  //if (CC3KPrinter != 0) CC3KPrinter->print(F("Creating socket... "));
  udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
  if (-1 == udp_socket)
  {
    CHECK_PRINTER {
		CC3KPrinter->println(F("Failed to open socket"));
	}
    return Adafruit_CC3000_Client();
  }
  //if (CC3KPrinter != 0) { CC3KPrinter->print(F("DONE (socket ")); CC3KPrinter->print(udp_socket); CC3KPrinter->println(F(")")); }

  // Try to open the socket
  memset(&socketAddress, 0x00, sizeof(socketAddress));
  socketAddress.sa_family = AF_INET;
  socketAddress.sa_data[0] = (destPort & 0xFF00) >> 8;  // Set the Port Number
  socketAddress.sa_data[1] = (destPort & 0x00FF);
  socketAddress.sa_data[2] = destIP >> 24;
  socketAddress.sa_data[3] = destIP >> 16;
  socketAddress.sa_data[4] = destIP >> 8;
  socketAddress.sa_data[5] = destIP;

  CHECK_PRINTER {
    CC3KPrinter->print(F("Connect to "));
    printIPdotsRev(destIP);
    CC3KPrinter->print(':');
    CC3KPrinter->println(destPort);
  }

  //printHex((byte *)&socketAddress, sizeof(socketAddress));
  if (-1 == connect(udp_socket, &socketAddress, sizeof(socketAddress)))
  {
    CHECK_PRINTER {
		CC3KPrinter->println(F("Connection error"));
	}
    closesocket(udp_socket);
    return Adafruit_CC3000_Client();
  }

  return Adafruit_CC3000_Client(udp_socket);
}


/**********************************************************************/
Adafruit_CC3000_Client::Adafruit_CC3000_Client(void) {
  _socket = -1;
}

Adafruit_CC3000_Client::Adafruit_CC3000_Client(uint16_t s) {
  _socket = s; 
  bufsiz = 0;
  _rx_buf_idx = 0;
}

Adafruit_CC3000_Client::Adafruit_CC3000_Client(const Adafruit_CC3000_Client& copy) {
  // Copy all the members to construct this client.
  _socket = copy._socket;
  bufsiz = copy.bufsiz;
  _rx_buf_idx = copy._rx_buf_idx;
  memcpy(_rx_buf, copy._rx_buf, RXBUFFERSIZE);
}

void Adafruit_CC3000_Client::operator=(const Adafruit_CC3000_Client& other) {
  // Copy all the members to assign a new value to this client.
  _socket = other._socket;
  bufsiz = other.bufsiz;
  _rx_buf_idx = other._rx_buf_idx;
  memcpy(_rx_buf, other._rx_buf, RXBUFFERSIZE);
}

bool Adafruit_CC3000_Client::connected(void) { 
  if (_socket < 0) return false;

  if (! available() && closed_sockets[_socket] == true) {
    //if (CC3KPrinter != 0) CC3KPrinter->println("No more data, and closed!");
    closesocket(_socket);
    closed_sockets[_socket] = false;
    _socket = -1;
    return false;
  }

  else return true;  
}

int16_t Adafruit_CC3000_Client::write(const void *buf, uint16_t len, uint32_t flags)
{
  return send(_socket, buf, len, flags);
}


size_t Adafruit_CC3000_Client::write(uint8_t c)
{
  int32_t r;
  r = send(_socket, &c, 1, 0);
  if ( r < 0 ) return 0;
  return r;
}

size_t Adafruit_CC3000_Client::fastrprint(const __FlashStringHelper *ifsh)
{
  char _tx_buf[TXBUFFERSIZE];
  uint8_t idx = 0;

  const char PROGMEM *p = (const char PROGMEM *)ifsh;
  size_t n = 0;
  while (1) {
    unsigned char c = pgm_read_byte(p++);
    if (c == 0) break;
    _tx_buf[idx] = c;
    idx++;
    if (idx >= TXBUFFERSIZE) {
      // lets send it!
      n += send(_socket, _tx_buf, TXBUFFERSIZE, 0);
      idx = 0;
    }
  }
  if (idx > 0) {
    // Send any remaining data in the transmit buffer.
    n += send(_socket, _tx_buf, idx, 0);
  }

  return n;
}

size_t Adafruit_CC3000_Client::fastrprintln(const __FlashStringHelper *ifsh)
{
  size_t r = 0;
  r = fastrprint(ifsh);
  r+= fastrprint(F("\r\n"));
  return r;
}

size_t Adafruit_CC3000_Client::fastrprintln(const char *str)
{
  size_t r = 0;
  size_t len = strlen(str);
  if (len > 0) {
    if ((r = write(str, len, 0)) <= 0) return 0;
  }
  if ((r += write("\r\n", 2, 0)) <= 0) return 0;  // meme fix
  return r;
}

size_t Adafruit_CC3000_Client::fastrprint(const char *str)
{
  size_t len = strlen(str);
  if (len > 0) {
    return write(str, len, 0);
  }
  else {
    return 0;
  }
}

size_t Adafruit_CC3000_Client::fastrprint(char *str)
{
  size_t len = strlen(str);
  if (len > 0) {
    return write(str, len, 0);
  }
  else {
    return 0;
  }
}

size_t Adafruit_CC3000_Client::fastrprintln(char *str) {
  size_t r = 0;
  r = fastrprint(str);
  r+= fastrprint(F("\r\n"));
  return r;
}

int16_t Adafruit_CC3000_Client::read(void *buf, uint16_t len, uint32_t flags) 
{
  return recv(_socket, buf, len, flags);

}

int32_t Adafruit_CC3000_Client::close(void) {
  int32_t x = closesocket(_socket);
  _socket = -1;
  return x;
}

uint8_t Adafruit_CC3000_Client::read(void) 
{
  while ((bufsiz <= 0) || (bufsiz == _rx_buf_idx)) {
    cc3k_int_poll();
    // buffer in some more data
    bufsiz = recv(_socket, _rx_buf, sizeof(_rx_buf), 0);
    if (bufsiz == -57) {
      close();
      return 0;
    }
    //if (CC3KPrinter != 0) { CC3KPrinter->println("Read "); CC3KPrinter->print(bufsiz); CC3KPrinter->println(" bytes"); }
    _rx_buf_idx = 0;
  }
  uint8_t ret = _rx_buf[_rx_buf_idx];
  _rx_buf_idx++;
  //if (CC3KPrinter != 0) { CC3KPrinter->print("("); CC3KPrinter->write(ret); CC3KPrinter->print(")"); }
  return ret;
}

uint8_t Adafruit_CC3000_Client::available(void) {
  // not open!
  if (_socket < 0) return 0;

  if ((bufsiz > 0) // we have some data in the internal buffer
      && (_rx_buf_idx < bufsiz)) {  // we havent already spit it all out
    return (bufsiz - _rx_buf_idx);
  }

  // do a select() call on this socket
  timeval timeout;
  fd_set fd_read;

  memset(&fd_read, 0, sizeof(fd_read));
  FD_SET(_socket, &fd_read);

  timeout.tv_sec = 0;
  timeout.tv_usec = 5000; // 5 millisec

  int16_t s = select(_socket+1, &fd_read, NULL, NULL, &timeout);
  //if (CC3KPrinter != 0) } CC3KPrinter->print(F("Select: ")); CC3KPrinter->println(s); }
  if (s == 1) return 1;  // some data is available to read
  else return 0;  // no data is available
}

void Adafruit_CC3000::setPrinter(Print* p) {
  CC3KPrinter = p;
}
