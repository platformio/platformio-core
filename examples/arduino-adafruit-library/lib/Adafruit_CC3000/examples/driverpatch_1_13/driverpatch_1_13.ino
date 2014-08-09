// Adafruit CC3000 Firmware V1.13 Upgrade Sketch
// Based on firmware patcher for MSP430 chips published by Texas Instruments.
//
// This sketch will upgrade CC3000 modules up to firmware version 1.13.
//
// You can find more details about the changes in the 1.13 firmware from TI at:
//   http://processors.wiki.ti.com/index.php/CC3000_Release_Notes
//
// In general the 1.13 release is a bug fix release with fixes for stability
// issues that caused the CC3000 to hang when under load.
//
// WARNING: Upgrade firmware at your own risk!  In general if the CC3000 is 
// currently working fine for your needs then hold off on the upgrade.
//
// Usage (read all the steps before strarting):
//   - Wire up your Arduino to the CC3000 just like you're running buildtest or
//     other examples.
//   - Adjust the ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_VBAT
//     defines below to match your wiring (just like running buildtest).
//   - Load the sketch on your Arduino and open the serial monitor at 115200 baud.
//   - You should see a prompt waiting for a key press to continue.  Enter text
//     and press enter to start the upgrade.
//   - You will see text printed as the firmware is upgraded.  The upgrade process
//     should be quick and take less than a minute.  
//   - You might see a message at the end that the firmware version or MAC address
//     couldn't be read--this can be ignored.
//   - Once the firmware upgrade is complete, run the buildtest sketch to check
//     the CC3000 functionality.
//   - During the firmware upgrade the CC3000 MAC address might be lost.  You can
//     write a new MAC address by uncommenting the appropriate line in the buildtest
//     example.  Make sure to save your MAC address before upgrading the firmware
//     if you'd like to keep it the same after

#include <Adafruit_CC3000.h>
#include <ccspi.h>
#include <SPI.h>
#include <string.h>
#include <EEPROM.h>

#include "utility/debug.h"
#include "utility/nvmem.h"
#include "driverpatchinc_1_13.h"

#define ADAFRUIT_CC3000_IRQ   3  // MUST be an interrupt pin!
#define ADAFRUIT_CC3000_CS    10
#define ADAFRUIT_CC3000_VBAT  5

Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT);

/**************************************************************************/
/*!
    @brief  Displays the driver mode (tiny of normal), and the buffer
            size if tiny mode is not being used

    @note   The buffer size and driver mode are defined in cc3000_common.h
*/
/**************************************************************************/
void displayDriverMode(void)
{
  #ifdef CC3000_TINY_DRIVER
    Serial.println(F("CC3000 is configure in 'Tiny' mode"));
  #else
    Serial.print(F("RX Buffer : "));
    Serial.print(CC3000_RX_BUFFER_SIZE);
    Serial.println(F(" bytes"));
    Serial.print(F("TX Buffer : "));
    Serial.print(CC3000_TX_BUFFER_SIZE);
    Serial.println(F(" bytes"));
  #endif
}

/**************************************************************************/
/*!
    @brief  Tries to read the CC3000's internal firmware patch ID
*/
/**************************************************************************/
void displayFirmwareVersion(void)
{
  #ifndef CC3000_TINY_DRIVER
  uint8_t major, minor;
  
  if(!cc3000.getFirmwareVersion(&major, &minor))
  {
    Serial.println(F("Unable to retrieve the firmware version!\r\n"));
  }
  else
  {
    Serial.print(F("Firmware V. : "));
    Serial.print(major); Serial.print(F(".")); Serial.println(minor);
  }
  #endif
}

/**************************************************************************/
/*!
    @brief  Tries to read the 6-byte MAC address of the CC3000 module
*/
/**************************************************************************/
boolean MACvalid = false;
// array to store MAC address from EEPROM
uint8_t cMacFromEeprom[MAC_ADDR_LEN];
void displayMACAddress(void)
{
  if(!cc3000.getMacAddress(cMacFromEeprom))
  {
    Serial.println(F("Unable to retrieve MAC Address!\r\n"));
    MACvalid = false;
  }
  else
  {
    Serial.print(F("MAC Address : "));
    cc3000.printHex((byte*)&cMacFromEeprom, 6);
    MACvalid = true;
  }
}



/**************************************************************************/
/*!
    @brief  Sets up the HW and the CC3000 module (called automatically
            on startup)
*/
/**************************************************************************/

uint8_t ucStatus_Dr, return_status = 0xFF;
uint8_t counter = 0;

// array to store RM parameters from EEPROM
unsigned char cRMParamsFromEeprom[128];


// 2 dim array to store address and length of new FAT
uint16_t aFATEntries[2][NVMEM_RM_FILEID + 1] = 
/*  address 	*/  {{0x50, 	0x1f0, 	0x1390, 0x0390, 0x2390, 0x4390, 0x6390, 0x63a0, 0x63b0,	0x63f0, 0x6430, 0x6830},
/*  length	*/   {0x1a0, 	0x1a0, 	0x1000, 0x1000, 0x2000, 0x2000, 0x10,   0x10,   0x40, 	0x40, 	0x400, 	0x200 }};
/* 0. NVS */
/* 1. NVS Shadow */
/* 2. Wireless Conf */
/* 3. Wireless Conf Shadow */
/* 4. BT (WLAN driver) Patches */
/* 5. WiLink (Firmware) Patches */
/* 6. MAC addr */
/* 7. Frontend Vars */
/* 8. IP config */
/* 9. IP config Shadow */
/* 10. Bootloader Patches */
/* 11. Radio Module params */
/* 12. AES128 for smart config */
/* 13. user file */
/* 14. user file */
/* 15. user file */


void setup(void)
{
  Serial.begin(115200);
  Serial.println(F("Hello, CC3000!\n")); 

  Serial.println(F("Hit any key & return to start"));
  while (!Serial.available());
 
  pinMode(9, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  digitalWrite(9, LOW);
  digitalWrite(8, LOW);
  digitalWrite(7, LOW);
  digitalWrite(6, LOW);
  
  displayDriverMode();
  displayFreeRam();
  
  /* Initialise the module */
  Serial.println(F("\nInitialising the CC3000 ..."));
  if (!cc3000.begin(2)) // init with NO patches!
  {
    Serial.println(F("Unable to initialise the CC3000! Check your wiring?"));
    while(1);
  }
  
  displayFirmwareVersion();
  displayMACAddress();
  
  return_status = 1;
  uint8_t index;
  uint8_t *pRMParams;
  
  while ((return_status) && (counter < 3)) {
	// read RM parameters
	// read in 16 parts to work with tiny driver
		
	return_status = 0;
	pRMParams = cRMParamsFromEeprom;
		
	for (index = 0; index < 16; index++) {
	  return_status |= nvmem_read(NVMEM_RM_FILEID, 8, 8*index, pRMParams); 
          Serial.print(F("\n\rRead NVRAM $")); Serial.print(8*index); Serial.print("\t");
          for(uint8_t x=0; x<8; x++) {
             Serial.print("0x"); Serial.print(pRMParams[x], HEX); Serial.print(", ");
          }
       	  pRMParams += 8;
	}
	counter++;
  }
  // if RM file is not valid, load the default one
  if (counter == 3) {
        Serial.println(F("\n\rLoad default params"));
    	pRMParams = (uint8_t *)cRMdefaultParams;
  } else {
        Serial.println(F("\n\rLoad EEPROM params"));
	pRMParams = cRMParamsFromEeprom;
      if (EEPROM.read(0) == 0xFF) {
        for (uint8_t e=0; e<128; e++) {
           EEPROM.write(e, cRMParamsFromEeprom[e]);
        }
        Serial.println(F("Backed up to eeprom!"));
      }
  }
  

  return_status = 1;

  while (return_status)	{
	// write new FAT
	return_status = fat_write_content(aFATEntries[0], aFATEntries[1]);
        Serial.print(F("Wrote FAT entries: ")); Serial.println(return_status, DEC);
  }

  //Serial.println(F("Stopping..."));
  //cc3000.stop();
  
  //Serial.println(F("\nInitialising the CC3000 ..."));

  //if (!cc3000.begin(2)) // no patches!
  //{
  //  Serial.println(F("Unable to initialise the CC3000! Check your wiring?"));
  //  while(1);
  //}
  
  return_status = 1;
	
  Serial.println(F("Write params"));

  while (return_status) {
    // write RM parameters
    // write in 4 parts to work with tiny driver
		
    return_status = 0;

    for (index = 0; index < 4; index++) {
      return_status |= nvmem_write(NVMEM_RM_FILEID, 32, 32*index, (pRMParams + 32*index)); 
      Serial.println(F("Wrote 32 bytes to NVRAM"));
    }
  }
  Serial.println(F("Wrote params"));
	
  return_status = 1;
	
  // write back the MAC address, only if exist
  if (MACvalid) {
	// zero out MCAST bit if set
	cMacFromEeprom[0] &= 0xfe;
	while (return_status) {
		return_status = nvmem_set_mac_address(cMacFromEeprom);
	}
  }
	
  ucStatus_Dr = 1;
  Serial.println(F("Writing driver patch"));

  while (ucStatus_Dr) {
	//writing driver patch to EEPRROM - PROTABLE CODE
	// Note that the array itself is changing between the different Service Packs    
	ucStatus_Dr = nvmem_write_patch(NVMEM_WLAN_DRIVER_SP_FILEID, drv_length, wlan_drv_patch);        
  }
	

  Serial.println(F("Wrote driver patch"));

  Serial.println(F("Starting w/o patches"));
	
  //if (!cc3000.begin(2))
  //{
  //  Serial.println(F("Unable to initialise the CC3000! Check your wiring?"));
  //  while(1);
  //}

  Serial.println(F("Writing firmware"));	

  unsigned char ucStatus_FW = 1;

  while (ucStatus_FW) {
	//writing FW patch to EAPRROM  - PROTABLE CODE
    	//Note that the array itself is changing between the different Service Packs   
    	ucStatus_FW = nvmem_write_patch(NVMEM_WLAN_FW_SP_FILEID, fw_length, fw_patch);
  }

  Serial.println(F("Starting w/patches"));

  cc3000.reboot();
  /*
  if (!)
  {
    Serial.println(F("Unable to initialise the CC3000! Check your wiring?"));
    while(1);
  }
  */
  Serial.println(F("Patched!"));
  displayFirmwareVersion();
  displayMACAddress();
}


//*****************************************************************************
//
//! fat_write_content
//!
//! \param[in] file_address  array of file address in FAT table:\n
//!						 this is the absolute address of the file in the EEPROM.
//! \param[in] file_length  array of file length in FAT table:\n
//!						 this is the upper limit of the file size in the EEPROM.
//!
//! \return on succes 0, error otherwise
//!
//! \brief  parse the FAT table from eeprom 
//
//*****************************************************************************
uint8_t fat_write_content(uint16_t *file_address, uint16_t *file_length)
{
	uint16_t  index = 0;
	uint8_t   ucStatus;
	uint8_t   fatTable[48];
	uint8_t*  fatTablePtr = fatTable;
	uint8_t LS[3]  = "LS";

	// first, write the magic number
	ucStatus = nvmem_write(16, 2, 0, LS); 
	
	for (; index <= NVMEM_RM_FILEID; index++)
	{
		// write address low char and mark as allocated
		*fatTablePtr++ = (uint8_t)(file_address[index] & 0xff) | _BV(0);
		
		// write address high char
		*fatTablePtr++ = (uint8_t)((file_address[index]>>8) & 0xff);
		
		// write length low char
		*fatTablePtr++ = (uint8_t)(file_length[index] & 0xff);
		
		// write length high char
		*fatTablePtr++ = (uint8_t)((file_length[index]>>8) & 0xff);		
	}
	
	// second, write the FAT
	// write in two parts to work with tiny driver
	ucStatus = nvmem_write(16, 24, 4, fatTable); 
	ucStatus = nvmem_write(16, 24, 24+4, &fatTable[24]); 
	
	// third, we want to erase any user files
	memset(fatTable, 0, sizeof(fatTable));
	ucStatus = nvmem_write(16, 16, 52, fatTable); 
	
	return ucStatus;
}


void loop(void)
{
  delay(1000);
}
