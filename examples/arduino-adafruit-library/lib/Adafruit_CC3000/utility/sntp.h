// sntp.h

#ifndef _SNTP_h
#define _SNTP_h
//  Notes on NTP packet format from IETF RFC-2030, SNTP Specification (http://www.ietf.org/rfc/rfc2030.txt?number=2030) :
//
//NTP Timestamp Format
//
//   SNTP uses the standard NTP timestamp format described in RFC-1305 and
//   previous versions of that document. In conformance with standard
//   Internet practice, NTP data are specified as integer or fixed-point
//   quantities, with bits numbered in big-endian fashion from 0 starting
//   at the left, or high-order, position. Unless specified otherwise, all
//   quantities are unsigned and may occupy the full field width with an
//   implied 0 preceding bit 0.
//
//   Since NTP timestamps are cherished data and, in fact, represent the
//   main product of the protocol, a special timestamp format has been
//   established. NTP timestamps are represented as a 64-bit unsigned
//   fixed-point number, in seconds relative to 0h on 1 January 1900. The
//   integer part is in the first 32 bits and the fraction part in the
//   last 32 bits. In the fraction part, the non-significant low order can
//   be set to 0.
//
//      It is advisable to fill the non-significant low order bits of the
//      timestamp with a random, unbiased bitstring, both to avoid
//      systematic roundoff errors and as a means of loop detection and
//      replay detection (see below). One way of doing this is to generate
//      a random bitstring in a 64-bit word, then perform an arithmetic
//      right shift a number of bits equal to the number of significant
//      bits of the timestamp, then add the result to the original
//      timestamp.
//
//
//
//
//Mills                        Informational                      [Page 6]
//
//RFC 2030             SNTPv4 for IPv4, IPv6 and OSI          October 1996
//
//
//   This format allows convenient multiple-precision arithmetic and
//   conversion to UDP/TIME representation (seconds), but does complicate
//   the conversion to ICMP Timestamp message representation, which is in
//   milliseconds. The maximum number that can be represented is
//   4,294,967,295 seconds with a precision of about 200 picoseconds,
//   which should be adequate for even the most exotic requirements.
//
//                        1                   2                   3
//    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
//   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//   |                           Seconds                             |
//   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//   |                  Seconds Fraction (0-padded)                  |
//   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//
//   Note that, since some time in 1968 (second 2,147,483,648) the most
//   significant bit (bit 0 of the integer part) has been set and that the
//   64-bit field will overflow some time in 2036 (second 4,294,967,296).
//   Should NTP or SNTP be in use in 2036, some external means will be
//   necessary to qualify time relative to 1900 and time relative to 2036
//   (and other multiples of 136 years). There will exist a 200-picosecond
//   interval, henceforth ignored, every 136 years when the 64-bit field
//   will be 0, which by convention is interpreted as an invalid or
//   unavailable timestamp.
//
//      As the NTP timestamp format has been in use for the last 17 years,
//      it remains a possibility that it will be in use 40 years from now
//      when the seconds field overflows. As it is probably inappropriate
//      to archive NTP timestamps before bit 0 was set in 1968, a
//      convenient way to extend the useful life of NTP timestamps is the
//      following convention: If bit 0 is set, the UTC time is in the
//      range 1968-2036 and UTC time is reckoned from 0h 0m 0s UTC on 1
//      January 1900. If bit 0 is not set, the time is in the range 2036-
//      2104 and UTC time is reckoned from 6h 28m 16s UTC on 7 February
//      2036. Note that when calculating the correspondence, 2000 is not a
//      leap year. Note also that leap seconds are not counted in the
//      reckoning.
//
//4. NTP Message Format
//
//   Both NTP and SNTP are clients of the User Datagram Protocol (UDP)
//   [POS80], which itself is a client of the Internet Protocol (IP)
//   [DAR81]. The structure of the IP and UDP headers is described in the
//   cited specification documents and will not be detailed further here.
//   The UDP port number assigned to NTP is 123, which should be used in
//   both the Source Port and Destination Port fields in the UDP header.
//   The remaining UDP header fields should be set as described in the
//   specification.
//
//
//
//Mills                        Informational                      [Page 7]
//
//RFC 2030             SNTPv4 for IPv4, IPv6 and OSI          October 1996
//
//
//   Below is a description of the NTP/SNTP Version 4 message format,
//   which follows the IP and UDP headers. This format is identical to
//   that described in RFC-1305, with the exception of the contents of the
//   reference identifier field. The header fields are defined as follows:
//
//                           1                   2                   3
//       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |LI | VN  |Mode |    Stratum    |     Poll      |   Precision   |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                          Root Delay                           |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                       Root Dispersion                         |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                     Reference Identifier                      |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                                                               |
//      |                   Reference Timestamp (64)                    |
//      |                                                               |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                                                               |
//      |                   Originate Timestamp (64)                    |
//      |                                                               |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                                                               |
//      |                    Receive Timestamp (64)                     |
//      |                                                               |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                                                               |
//      |                    Transmit Timestamp (64)                    |
//      |                                                               |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                 Key Identifier (optional) (32)                |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//      |                                                               |
//      |                                                               |
//      |                 Message Digest (optional) (128)               |
//      |                                                               |
//      |                                                               |
//      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//
//   As described in the next section, in SNTP most of these fields are
//   initialized with pre-specified data. For completeness, the function
//   of each field is briefly summarized below.
//
//
//   Leap Indicator (LI): This is a two-bit code warning of an impending
//   leap second to be inserted/deleted in the last minute of the current
//   day, with bit 0 and bit 1, respectively, coded as follows:
//
//      LI       Value     Meaning
//      -------------------------------------------------------
//      00       0         no warning
//      01       1         last minute has 61 seconds
//      10       2         last minute has 59 seconds)
//      11       3         alarm condition (clock not synchronized)
//
//   Version Number (VN): This is a three-bit integer indicating the
//   NTP/SNTP version number. The version number is 3 for Version 3 (IPv4
//   only) and 4 for Version 4 (IPv4, IPv6 and OSI). If necessary to
//   distinguish between IPv4, IPv6 and OSI, the encapsulating context
//   must be inspected.
//
//   Mode: This is a three-bit integer indicating the mode, with values
//   defined as follows:
//
//      Mode     Meaning
//      ------------------------------------
//      0        reserved
//      1        symmetric active
//      2        symmetric passive
//      3        client
//      4        server
//      5        broadcast
//      6        reserved for NTP control message
//      7        reserved for private use
//
//   In unicast and anycast modes, the client sets this field to 3
//   (client) in the request and the server sets it to 4 (server) in the
//   reply. In multicast mode, the server sets this field to 5
//   (broadcast).
//
//   Stratum: This is a eight-bit unsigned integer indicating the stratum
//   level of the local clock, with values defined as follows:
//
//      Stratum  Meaning
//      ----------------------------------------------
//      0        unspecified or unavailable
//      1        primary reference (e.g., radio clock)
//      2-15     secondary reference (via NTP or SNTP)
//      16-255   reserved
//
//
//   Poll Interval: This is an eight-bit signed integer indicating the
//   maximum interval between successive messages, in seconds to the
//   nearest power of two. The values that can appear in this field
//   presently range from 4 (16 s) to 14 (16284 s); however, most
//   applications use only the sub-range 6 (64 s) to 10 (1024 s).
//
//   Precision: This is an eight-bit signed integer indicating the
//   precision of the local clock, in seconds to the nearest power of two.
//   The values that normally appear in this field range from -6 for
//   mains-frequency clocks to -20 for microsecond clocks found in some
//   workstations.
//
//   Root Delay: This is a 32-bit signed fixed-point number indicating the
//   total roundtrip delay to the primary reference source, in seconds
//   with fraction point between bits 15 and 16. Note that this variable
//   can take on both positive and negative values, depending on the
//   relative time and frequency offsets. The values that normally appear
//   in this field range from negative values of a few milliseconds to
//   positive values of several hundred milliseconds.
//
//   Root Dispersion: This is a 32-bit unsigned fixed-point number
//   indicating the nominal error relative to the primary reference
//   source, in seconds with fraction point between bits 15 and 16. The
//   values that normally appear in this field range from 0 to several
//   hundred milliseconds.
//
//   Reference Identifier: This is a 32-bit bitstring identifying the
//   particular reference source. In the case of NTP Version 3 or Version
//   4 stratum-0 (unspecified) or stratum-1 (primary) servers, this is a
//   four-character ASCII string, left justified and zero padded to 32
//   bits. In NTP Version 3 secondary servers, this is the 32-bit IPv4
//   address of the reference source. In NTP Version 4 secondary servers,
//   this is the low order 32 bits of the latest transmit timestamp of the
//   reference source. NTP primary (stratum 1) servers should set this
//   field to a code identifying the external reference source according
//   to the following list. If the external reference is one of those
//   listed, the associated code should be used. Codes for sources not
//   listed can be contrived as appropriate.
//
//
//      Code     External Reference Source
//      ----------------------------------------------------------------
//      LOCL     uncalibrated local clock used as a primary reference for
//               a subnet without external means of synchronization
//      PPS      atomic clock or other pulse-per-second source
//               individually calibrated to national standards
//      ACTS     NIST dialup modem service
//      USNO     USNO modem service
//      PTB      PTB (Germany) modem service
//      TDF      Allouis (France) Radio 164 kHz
//      DCF      Mainflingen (Germany) Radio 77.5 kHz
//      MSF      Rugby (UK) Radio 60 kHz
//      WWV      Ft. Collins (US) Radio 2.5, 5, 10, 15, 20 MHz
//      WWVB     Boulder (US) Radio 60 kHz
//      WWVH     Kaui Hawaii (US) Radio 2.5, 5, 10, 15 MHz
//      CHU      Ottawa (Canada) Radio 3330, 7335, 14670 kHz
//      LORC     LORAN-C radionavigation system
//      OMEG     OMEGA radionavigation system
//      GPS      Global Positioning Service
//      GOES     Geostationary Orbit Environment Satellite
//
//   Reference Timestamp: This is the time at which the local clock was
//   last set or corrected, in 64-bit timestamp format.
//
//   Originate Timestamp: This is the time at which the request departed
//   the client for the server, in 64-bit timestamp format.
//
//   Receive Timestamp: This is the time at which the request arrived at
//   the server, in 64-bit timestamp format.
//
//   Transmit Timestamp: This is the time at which the reply departed the
//   server for the client, in 64-bit timestamp format.
//
//   Authenticator (optional): When the NTP authentication scheme is
//   implemented, the Key Identifier and Message Digest fields contain the
//   message authentication code (MAC) information defined in Appendix C
//   of RFC-1305.

#if defined(ARDUINO) && ARDUINO >= 100
	#include "Arduino.h"
#else
	#include "WProgram.h"
#endif

#include "utility/socket.h"
#include "utility/netapp.h"

//#define CLOCK_DEBUG
//#define CLOCK_DEEP_DEBUG
//
#define SNTP_PORT	  ((uint16_t)123)   /* well-known NTP port number, assigned by IANA */

#define	MAX_URL_NAME		 31

#define MAX_NTP_SERVERS		  2

#define NUMBER_OF_TIME_ZONES 34


typedef enum SNTP_LI_t	{	no_warning = 0,
							sixty_One,
							fifty_Nine,
							alarm
						} SNTP_LI_t;

typedef enum SNTP_Mode_t {	reserved = 0,
							sym_active,
							sym_passive,
							client,
							server,
							broadcast,
							reserved_control,
							reserved_private
						 } SNTP_Mode_t;

typedef struct SNTP_Stratum_t
{
	uint8_t primary       : 1;
	uint8_t secondary     : 3;
	uint8_t reserved      : 4;
}SNTP_Stratum_t;

typedef struct SNTP_Timestamp_t
{
	uint32_t  seconds;
	int32_t  fraction;
}SNTP_Timestamp_t;

typedef struct SNTP_Message_t
{
	SNTP_Mode_t          mode          : 3;
	uint8_t              VN            : 3;
	SNTP_LI_t            LI            : 2;
	SNTP_Stratum_t       stratum;
	char                 poll;
	char                 precision;
	long                 delay;
	uint32_t             dispersion;
	uint32_t             referenceID;
	SNTP_Timestamp_t     tsReference;
	SNTP_Timestamp_t     tsOriginate;
	SNTP_Timestamp_t     tsReceive;
	SNTP_Timestamp_t     tsTransmit;
	//   uint32_t               key;                  //optional field - ignore
	//   uint8_t                messageDigest[128];   //optional field - ignore
}SNTP_Message_t;

typedef const char** NTP_Pool_t;							//Name of NTP server pool
typedef uint32_t  NTP_Server_List_t[MAX_NTP_SERVERS];   //list of ntp server addresses (as returned by NTP server pool)

/**
* Structure for NTP calendar time.
*
*/
typedef struct NetTime_t
{
	uint16_t millis; ///< Milliseconds after the second (0..999)
	uint8_t	 sec;    ///< Seconds after the minute (0..59)
	uint8_t	 min;    ///< Minutes after the hour (0..59)
	uint8_t	 hour;   ///< Hours since midnight (0..23)
	uint8_t	 mday;   ///< Day of the month (1..31)
	uint8_t	 mon;    ///< Months since January (0..11)
	uint16_t year;   ///< Year.
	uint8_t	 wday;	 ///< Days since Sunday (0..6)
	uint16_t yday;   ///< Days since January 1 (0..365)
	bool	 isdst;  ///< Daylight savings time flag, currently not supported
}NetTime_t;


class sntp
{
  public:
	sntp();
 	sntp(char* ntp_server_url1, short local_utc_offset);
 	sntp(char* ntp_server_url1, char* ntp_server_url2, short local_utc_offset);
 	sntp(char* ntp_server_url1, short local_utc_offset, short dst_utc_offset, bool enable_dst);
	sntp(char* ntp_server_url1, char* ntp_server_url2, short local_utc_offset, short dst_utc_offset, bool enable_dst);
	
	virtual ~sntp() {};
		
	NetTime_t			*ExtractNTPTime(/*in*/ SNTP_Timestamp_t *ntpTime, /*out*/ NetTime_t *extractedTime);

	bool				UpdateNTPTime();
	SNTP_Timestamp_t*	NTPGetTime(SNTP_Timestamp_t* ntpTime, bool local);
	SNTP_Timestamp_t*	NTPSetTime(SNTP_Timestamp_t* ntpTime, bool local);
	int					GetSystemClockAsNTPTime(SNTP_Timestamp_t* ntpSystemTime);
	
  private:
	char				GetNTPServerList(const char** ntp_pool_list, uint32_t* addrBuffer, int maxServerCount);
	bool				SNTP_GetTime(int sntpSocket, uint32_t *ntpServerAddr);

	NetTime_t			m_timeStruct;

	uint8_t				m_change_DST;					// 0 if no daylight savings time change, +1 if spring change, -1 if fall change

	SNTP_Timestamp_t	m_NTPReferenceTime;				//base time for real-time clock real time = this + millisecond ticker
	SNTP_Timestamp_t	m_std_UTC_offset;				//Local standard-time offset from UTC. Example: Eastern Standard is UTC - 5 hours
	SNTP_Timestamp_t	m_dst_UTC_offset;				//Local daylight-savings-time offset from UTC. Ex: Eastern Daylght is UTC - 4 hours
	SNTP_Timestamp_t*	m_cur_UTC_offset;				//Current offset from UTC. Pointer to either std_UTC_offset or dst_UTC_offset
	bool				m_twelveHour;					//use 12-hour time when true, 24-hour time when false
	bool  		        m_enable_dst;					//enable daylight savings time
	SNTP_Timestamp_t	m_dst_start;					// next date when DST starts
	SNTP_Timestamp_t	m_dst_end;						// next date when DST ends
	uint32_t			m_pollTime;						// in seconds, how often to poll NTP to update clock
	NTP_Pool_t			m_localPool;					//list of pool servers for current geographical location
	NTP_Pool_t			m_globalPool;					//list of global pool servers if no local servers respond
	uint8_t				m_userServerCount;				//number of NTP servers provded by user (not pool servers)
	const char*			m_userServers[MAX_NTP_SERVERS];	//list of NTP or NTP pool servers provided by user (pointers to userServerStrings)
	char				m_userServerStrings[MAX_NTP_SERVERS][MAX_URL_NAME+1]; //storage for user's NTP server URL strings

    bool				m_timeIsSet;					//false = current time is not set

};

//extern sntp SNTP;
extern Print* CC3KPrinter;

#endif

