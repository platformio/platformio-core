// 
// 
// 

#include "sntp.h"

//Lists of pool servers


const char* ntp_us_pool_list[] =  {	"0.us.pool.ntp.org",
								"1.us.pool.ntp.org",
								"2.us.pool.ntp.org",
								"3.us.pool.ntp.org",
								"0.north-america.pool.ntp.org",
								"1.north-america.pool.ntp.org",
								"2.north-america.pool.ntp.org",
								"3.north-america.pool.ntp.org",
								NULL
							};

const char* ntp_global_pool_list[] =  {   "0.pool.ntp.org",
									"1.pool.ntp.org",
									"2.pool.ntp.org",
									"pool.ntp.org",
									NULL
								};

// ExtractNTPTime - convert ntp seconds into calendar time
//  Notes:
//		- 1900 was NOT a leap-year.
//		- This routine deals with the overflow of the 32-bit seconds value,
//		  which will happen on 02/07/2036 at 06:28:16.
//

#define SECS_DAY    (24L * 60 * 60)                   /* number of seconds in a day */
#define BASE_YEAR   (1900)                            /* NTP time starts at 1/1/1900 00:00:00 */

#define FIX_PT_DAYS_YEAR   ((365L * 256) + (256 / 4))
// It may not look that way, but this is (365.25 * 256)
// That is, it's (365 * 256) + (0.25 * 256) = (365.25 * 256). Why are we doing this?
// There are 365 days in a year. After you factor out seconds in the current day,
// you're left with days since 1/1/1900.  Dividing by 365 would therefore give you
// the number of years since 1900, if it wasn't for leap years. If you include
// leap-years, you get 365.25 days per year.  So, we have to divide ntp days by 365.25
// to get the proper year.  Instead of doing a floating point divide by 365.25, we do
// fixed point arithmetic, placing the binary-point at 8 bits (i.e., 256 decimal).
//There's only one small fly in this ointment - 1900 was not a leap year.
// Fortunately, we can compensate by adding 1 to the NTP days, as if 1900 WAS a
// leap-year.  When we divide days down to years, the extra day is lost in
// the roundoff. Problem solved.

//   days in each month: {jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec};
char    monthDays[12] = { 31,  28,  31,  30,  31,  30,  31,  31,  30,  31,  30,  31};


#ifdef CLOCK_DEBUG
	void dumpBlock1(char* buf, short len) 	/*rdl 2/16/2008*/
	{
		uint8_t* offset = (uint8_t*)buf;
		int16_t count = 0;
		int	lineCount = 0;
		char ascii[17] = "";
		char* pAscii = ascii;
	
	delay(10);
		if (CC3KPrinter != 0) { CC3KPrinter->print(F("Block: (addr ")); CC3KPrinter->print((uint16_t)buf, HEX); CC3KPrinter->print(F(", length ")); CC3KPrinter->print(len, HEX); }
	//	traceFn("Block: (addr %p, length 0x%04x)", buf, len);

		while (count < len)
		{
			if (CC3KPrinter != 0) { CC3KPrinter->println(); CC3KPrinter->print((uint16_t)offset,HEX); CC3KPrinter->print(F(": ")); }
	//		traceFn("\r\n  %p: ", offset);
			lineCount = 0;
			pAscii = (char*)&ascii;
			memset(ascii,' ',16);
			while ((count < len) && (lineCount < 8))
			{
				if ((*offset <= ' ') || (*offset == 0xFF)) *pAscii++ = '.'; else *pAscii++ = *offset; *pAscii++ = ' ';
				if (CC3KPrinter != 0) { CC3KPrinter->print((*offset)>>4,HEX); CC3KPrinter->print((*offset++)&0x0F,HEX); CC3KPrinter->print(F(" ")); }
	//			traceFn("0x%02bx ", *offset++);
				count++;
				lineCount++;
			}
			while (lineCount++ < 8)
			{
				if (CC3KPrinter != 0) { CC3KPrinter->print(F("     ")); }
	//			traceFn("     ");
			}
			if (CC3KPrinter != 0) { CC3KPrinter->print(F("  | ")); CC3KPrinter->print(ascii); CC3KPrinter->print(F("|")); }
	// 		traceFn("  | %s|", ascii);
	delay(10);
		}
		if (CC3KPrinter != 0) { CC3KPrinter->println(); }
	//	traceFn("\r\n");
	}
#endif

//Calculates (time / 2) for NTP timestamp values (64-bit fixed point, normalized to 32-bit)
// ORIGINAL VALUE OF time IS DESTROYED, and replaced with result of calculation.
// performs a signed divide
void NTPdiv2(SNTP_Timestamp_t* time) 
{
	uint32_t carry = time->seconds & 1;          //this bit will shift from 'seconds' to 'fraction'
	time->fraction >>= 1;                     //divide 'fraction' by 2
	time->fraction |= carry << 31;            //OR in the low bit of 'seconds' as the high bit of 'fraction
	time->seconds >>= 1;                //signed divide of 'seconds' by 2
}

//Calculates (time1 + time2) for NTP timestamp values (64-bit fixed point, normalized to 32-bit)
// ORIGINAL VALUE OF time2 IS DESTROYED, and replaced with result of calculation.
// Returns overflow
uint8_t AddNTPtime(SNTP_Timestamp_t* time1, SNTP_Timestamp_t* time2)
{
	uint8_t carry = ((time2->fraction>>1)+(time1->fraction>>1) & 0x80000000)>>31;
	time2->fraction += time1->fraction;
	time2->seconds += carry;
	carry = ((time2->seconds>>1)+(time1->seconds>>1) & 0x80000000)>>31;
	time2->seconds += time1->seconds;
	return carry;       //if there's still a carry, then we have an overflow.
}

//Calculates (time2 - time1) for NTP timestamp values (64-bit fixed point, normalized to 32-bit)
// ORIGINAL VALUE OF time2 IS DESTROYED, and replaced with result of calculation.
// Returns underflow
uint8_t DiffNTPtime(SNTP_Timestamp_t* time1, SNTP_Timestamp_t* time2)
{
	uint8_t borrow = ((time2->fraction>>1)-(time1->fraction>>1) & 0x80000000)>>31;
	time2->fraction -= time1->fraction;
	time2->seconds -= borrow;
	borrow = ((time2->seconds>>1)-(time1->seconds>>1) & 0x80000000)>>31;
	time2->seconds -= time1->seconds;
	return borrow;      //if there's still a borrow, then we have an underflow.
}

int sntp::GetSystemClockAsNTPTime(SNTP_Timestamp_t* ntpSystemTime) 
{
	long  systemMillis;

	if (ntpSystemTime)
	{
		ntpSystemTime->seconds = millis() / 1000;
		systemMillis = millis() - (ntpSystemTime->seconds * 1000);
		systemMillis = (systemMillis << 10) / 1000;
		ntpSystemTime->fraction = systemMillis << 22;
	}

	#ifdef CLOCK_DEBUG
		if (CC3KPrinter != 0) { CC3KPrinter->print(F(" GetSystemClockAsNTPTime: ")); CC3KPrinter->print(ntpSystemTime->seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(ntpSystemTime->fraction,HEX); }
	#endif
	return 0;
}


SNTP_Timestamp_t* sntp::NTPGetTime(SNTP_Timestamp_t* ntpTime, bool local) 
{
	SNTP_Timestamp_t  ntpSystemTime;

	if (ntpTime)
	{
		GetSystemClockAsNTPTime(&ntpSystemTime);
		
		*ntpTime = m_NTPReferenceTime;
		
		#ifdef CLOCK_DEBUG
			if (CC3KPrinter != 0) { CC3KPrinter->print(F(" NTPGetTime m_NTPReferenceTime: ")); CC3KPrinter->print(ntpTime->seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(ntpTime->fraction,HEX); }
		#endif
		
		AddNTPtime(&ntpSystemTime, ntpTime);

		#ifdef CLOCK_DEBUG
			if (CC3KPrinter != 0) { CC3KPrinter->print(F(" NTPGetTime NTP Current UTC: ")); CC3KPrinter->print(ntpTime->seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(ntpTime->fraction,HEX); }
		#endif

		if (local)                                         //if true, add in local offset from UTC
		{
			AddNTPtime(m_cur_UTC_offset, ntpTime);
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F(" NTPGetTime NTP Current Local: ")); CC3KPrinter->print(ntpTime->seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(ntpTime->fraction,HEX); }
			#endif
		}
	}
	return ntpTime;
}

SNTP_Timestamp_t* sntp::NTPSetTime(SNTP_Timestamp_t* ntpTime, bool local) 
{
	SNTP_Timestamp_t  ntpSystemTime;

	if (ntpTime)
	{
		if (local)
		{
			DiffNTPtime(m_cur_UTC_offset, ntpTime); //take out local offset to set clock as UTC
		}

		GetSystemClockAsNTPTime(&ntpSystemTime);
		
		m_NTPReferenceTime = *ntpTime;
		DiffNTPtime(&ntpSystemTime, &m_NTPReferenceTime);

		m_timeIsSet = true;
	}
	return ntpTime;
}

NetTime_t *sntp::ExtractNTPTime(/*in*/ SNTP_Timestamp_t *ntpTime, /*out*/ NetTime_t *extractedTime)
{

	uint32_t time = ntpTime->seconds;
	uint32_t dayclock, dayno;
	int year;
	char month;
	int day;
	bool  dateOverflow = (0 == (time & 0x80000000));     //32-bit counter overflowed?
	
	extractedTime->millis = ((ntpTime->fraction >>22) * 1000) >>10;
	
	dayclock = time % SECS_DAY;               //seconds since midnight
	dayno = time / SECS_DAY;                  //days since 1/1/1900 (or since 2/7/2036)

	#ifdef CLOCK_DEEP_DEBUG
		if (CC3KPrinter != 0) { CC3KPrinter->print(F("dayclock = ")); CC3KPrinter->print(dayclock); CC3KPrinter->print(F("dayno = ")); CC3KPrinter->println(dayno); }
	#endif

	if (dateOverflow)                       //if the date overflowed, we'll effectively add the overflowed bit
	{                                       // back into dayno and dayclock.  They've got plenty of room for it now
		dayclock = (dayclock + 23296);        //new zero-point for dayclock is 06:28:16
		dayno +=  49710;                      //new zero-point for dayno is 02/07/2036
		dayno +=  (dayclock / SECS_DAY);      //           PLUS 6:28:16, or 49710 days, 23296 seconds since 1/1/1900 00:00:00
		dayclock %= SECS_DAY;                 // get rid of any overflow (we already added it to dayno in previous line)

		#ifdef CLOCK_DEEP_DEBUG
			if (CC3KPrinter != 0) { CC3KPrinter->print(F("    date overflow: dayclock =")); CC3KPrinter->print(dayclock); CC3KPrinter->print(F("dayno = ")); CC3KPrinter->println(dayno); }
		#endif

	}

	extractedTime->sec = dayclock % 60;            //seconds in current minute
	extractedTime->min = (dayclock % 3600) / 60;   //minutes in current hour
	extractedTime->hour = dayclock / 3600;         //hours in current day
	extractedTime->wday = (dayno + 1) % 7;         //days since Sunday (0..6). Biased since 1/1/1900 was a thursday

	dayno += 1;                                //No leap-year in 1900, as there should have been.  This throws off the
	// calculation of year = dayno / 365.25.  So we add one to line things back
	// up again, just for the year calculation.

	dayno <<= 8;                                    //fixed point arithmetic - multiply by 256 so we can do an integer divide by
	year = (dayno / FIX_PT_DAYS_YEAR) + BASE_YEAR;  // (365.25 * 256)instead of doing a floating-point divide by 365.25

	#ifdef CLOCK_DEEP_DEBUG
		if (CC3KPrinter != 0) { CC3KPrinter->print(year); CC3KPrinter->print(F("  = (")); CC3KPrinter->print(dayno); CC3KPrinter->print(F(" // ")); CC3KPrinter->print(FIX_PT_DAYS_YEAR); CC3KPrinter->print(F(") + ")); CC3KPrinter->println(BASE_YEAR); }
	#endif

	extractedTime->year = year;
	dayno = (dayno % FIX_PT_DAYS_YEAR) >> 8;

	extractedTime->yday = dayno;

	//if year is evenly divisible by 4, it's a leap-year, except for 1900. Change February days in table accordingly
	monthDays[1] = ((0 == (year & 3)) && (1900 != year))? 29 : 28;

	//Now, we're going to loop through the month table, subtracting days from dayno until dayno goes negative
	//    that will give us the current month
	day = (int)dayno;
	month = 0;
	while (0 <= day)
	day-= monthDays[month++];

	month -= 1;           //we need to return month as zero-based. Phooey!
	extractedTime->mon = month;
	extractedTime->mday = day + monthDays[month] + 1;        //Since we looped until days went negative, we need add back in days in current month

	extractedTime->isdst = 0;                                 //currently ignored.
	
	#ifdef CLOCK_DEEP_DEBUG
		dumpBlock1((char*)extractedTime, sizeof(NetTime_t));
	#endif

	return extractedTime;
}

//bool GetGatewayAddress(char* gatewayAddr)
//{
	//bool success = false;
	//tNetappIpconfigRetArgs ipconfig;
	//netapp_ipconfig(&ipconfig);
//
	///* If byte 1 is 0 we don't have a valid address */
	//if (ipconfig.aucIP[3] != 0)
	//{
		//snprintf(gatewayAddr, MAX_URL_NAME, "%d.%d.%d.%d",ipconfig.aucIP+11,ipconfig.aucIP+10,ipconfig.aucIP+9,ipconfig.aucIP+8);
		//success = true;
	//}
	//return success;
//}

sntp::sntp()
{
	m_localPool = ntp_us_pool_list;
	m_globalPool = ntp_global_pool_list;
	
	m_NTPReferenceTime.seconds = 0X80000000;	//initial base time for real-time clock (1/20/1968 03:14:08)
	m_NTPReferenceTime.fraction = 0;
	
	m_std_UTC_offset.seconds = 0;				//Local standard-time offset from UTC. Example: Eastern Standard is UTC - 5 hours
	m_std_UTC_offset.fraction = 0;
	m_dst_UTC_offset.seconds = 0;				//Local daylight-savings-time offset from UTC. Ex: Eastern Daylght is UTC - 4 hours
	m_dst_UTC_offset.fraction = 0;
	m_cur_UTC_offset = &m_std_UTC_offset;		//Current offset from UTC. Pointer to either std_UTC_offset or dst_UTC_offset
	m_twelveHour = false;						//use 12-hour time when true, 24-hour time when false
	m_enable_dst = false;						//enable daylight savings time
	
	//GetGatewayAddress((char*)&m_userServerStrings[1]);
	//m_userServers[0] = (char*)&m_userServerStrings[1];
}

sntp::sntp(char* ntp_server_url1, char* ntp_server_url2, short local_utc_offset, short dst_utc_offset, bool enable_dst)
{
	int user_server_count = 0;
	
	sntp();
	
	m_std_UTC_offset.seconds = (uint32_t)(60L * local_utc_offset);
	m_dst_UTC_offset.seconds = (uint32_t)(60L * dst_utc_offset);
	m_cur_UTC_offset = &m_dst_UTC_offset;
	m_enable_dst = enable_dst;
	if (ntp_server_url1)
	{
		strncpy((char*)&m_userServerStrings[user_server_count], ntp_server_url1, MAX_URL_NAME);
		m_userServers[user_server_count] = (char*)&m_userServerStrings[user_server_count];
		user_server_count++;
	}
	if (ntp_server_url2)
	{
		strncpy((char*)&m_userServerStrings[user_server_count], ntp_server_url2, MAX_URL_NAME);
		m_userServers[user_server_count] = (char*)&m_userServerStrings[user_server_count];
		user_server_count++;
	}
}
sntp::sntp(char* ntp_server_url1, short local_utc_offset)
{
	sntp(ntp_server_url1, NULL, local_utc_offset, 0, false);
}	
sntp::sntp(char* ntp_server_url1, char* ntp_server_url2, short local_utc_offset)
{
	sntp(ntp_server_url1, ntp_server_url2, local_utc_offset, 0, false);
}	
sntp::sntp(char* ntp_server_url1, short local_utc_offset, short dst_utc_offset, bool enable_dst)
{
	sntp(ntp_server_url1, NULL, local_utc_offset, dst_utc_offset, enable_dst);	
}

//To spread the load of NTP client request, ntp.org maintains DNS servers that will return a list of
// available NTP servers from a pool.  This routine gets a list of servers from the specified pool
// and returns it, along with a count of the servers in the list.
char sntp::GetNTPServerList(const char** ntp_pool_list, uint32_t* addrBuffer, int maxServerCount)
{
	uint32_t			 ntpServer= NULL;
	const char           **ntpPoolName;
	uint8_t              serverCount = 0;

	if ((ntp_pool_list) && (addrBuffer))
	{
		ntpPoolName = ntp_pool_list;
		while ((*ntpPoolName) && (!ntpServer))
		{
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F("Checking NTP server/pool address ")); CC3KPrinter->println(*ntpPoolName); }
			#endif

			gethostbyname(*ntpPoolName, strlen(*ntpPoolName), &ntpServer);

			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F("     returns ntpServer: ")); CC3KPrinter->println(ntpServer,HEX); }
			#endif

			ntpPoolName++;
		}
		if (ntpServer)
		{
			*addrBuffer = ntpServer;
			serverCount += 1;
		}

	}
	return serverCount;
}


//Called by task to poll specific NTP server for current time.
bool  sntp::SNTP_GetTime(int	sntpSocket, uint32_t *ntpServerAddr) 
{
	sockaddr_in			socketAddr;
	socklen_t			sockLen;
	int32_t				recvTimeout = 30000;
	int8_t				byteCount;
	SNTP_Timestamp_t	tsDestination;
	bool				result = false;
	SNTP_Message_t		sntp_message;			 // sntp message buffer

	#ifdef CLOCK_DEBUG
		if (CC3KPrinter != 0) { CC3KPrinter->println(F("SNTP_GetTime")); }
	#endif
	
	// set the ntp server address and port
	memset(&socketAddr, 0, sizeof(sockaddr_in));
	socketAddr.sin_family = AF_INET;
	memcpy(&(socketAddr.sin_addr), ntpServerAddr, 4);
	socketAddr.sin_port = htons(SNTP_PORT);

	//Prepare the outgoing ntp request packet
	memset(&sntp_message, 0, sizeof(SNTP_Message_t));          //zero the outgoing message
	sntp_message.mode = client;                                // NTP client request
	sntp_message.VN = 3;                                       // NTP version 3
	NTPGetTime(&sntp_message.tsTransmit, false);             //transmitting at current UTC time

	#ifdef CLOCK_DEBUG
		if (CC3KPrinter != 0) { CC3KPrinter->print(F("SNTP sendto server ")); CC3KPrinter->println(socketAddr.sin_addr.s_addr,HEX); }
		dumpBlock1((char*)&sntp_message, sizeof(SNTP_Message_t));
	#endif

	sockLen = sizeof(sockaddr_in);
	byteCount = sendto(sntpSocket, &sntp_message, sizeof(SNTP_Message_t), 0, (sockaddr*)&socketAddr, sockLen);

	#ifdef CLOCK_DEBUG
		if (CC3KPrinter != 0) { CC3KPrinter->print(F("sendto transmitted ")); CC3KPrinter->print(byteCount,HEX); CC3KPrinter->println(F(" bytes")); }
	#endif
		
	if (sizeof(SNTP_Message_t) == byteCount)
	{
		#ifdef CLOCK_DEBUG
			if (CC3KPrinter != 0) { CC3KPrinter->println(F("Waiting for response")); }
		#endif

		setsockopt(sntpSocket, SOL_SOCKET, SOCKOPT_RECV_TIMEOUT, &recvTimeout, (socklen_t)sizeof(recvTimeout));
		sockLen = sizeof(sockaddr_in);
		byteCount = recvfrom(sntpSocket, &sntp_message, sizeof(SNTP_Message_t), 0, (sockaddr*)&socketAddr, &sockLen);

		//tsDestination = UTC time when we received reply
		NTPGetTime(&tsDestination, false);
			
		#ifdef CLOCK_DEBUG
			if (CC3KPrinter != 0) { CC3KPrinter->print(F("SNTP received ")); CC3KPrinter->print(byteCount); CC3KPrinter->println(F(" bytes")); }
		#endif
			
		//If we got a good response packet, go ahead and calculate the current time.
		// This is done according the the following equation:
		// ((Receive time - Originate Time) + (Transmit Time - Destination Time)) / 2
		if (sizeof(SNTP_Message_t) == byteCount)
		{
			//Change the byte order of the received timestamps to big-endian
			sntp_message.tsReceive.seconds  = htonl(sntp_message.tsReceive.seconds);
			sntp_message.tsReceive.fraction = htonl(sntp_message.tsReceive.fraction);
			sntp_message.tsTransmit.seconds  = htonl(sntp_message.tsTransmit.seconds);
			sntp_message.tsTransmit.fraction = htonl(sntp_message.tsTransmit.fraction);
			//we don't use tsReference for anything, so don't bother swapping it.
			// sntp_message.tsReference.seconds  = htonl(sntp_message.tsReference.seconds);
			// sntp_message.tsReference.fraction = htonl(sntp_message.tsReference.fraction);

				
			#ifdef CLOCK_DEBUG
				dumpBlock1((char*)&sntp_message, sizeof(SNTP_Message_t));
				if (CC3KPrinter != 0) { CC3KPrinter->println(F("Received at ")); }
				dumpBlock1((char*)&tsDestination, sizeof(tsDestination));
			#endif
			
			//Formula is: correction = ((tsReceive-tsOriginate)/2) + ((tsTransmit-tsDestination)/2)
			//
			//Server received request at tsReceive, we sent request at tsOriginate
			DiffNTPtime(&sntp_message.tsOriginate, &sntp_message.tsReceive);
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F(" (R - O): ")); CC3KPrinter->print(sntp_message.tsReceive.seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(sntp_message.tsReceive.fraction,HEX); }
			#endif
			NTPdiv2(&sntp_message.tsReceive);
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F(" (R - O)/2: ")); CC3KPrinter->print(sntp_message.tsReceive.seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(sntp_message.tsReceive.fraction,HEX); }
			#endif

			//Server sent reply at tsTransmit, we received reply at tsDestination
			DiffNTPtime(&tsDestination, &sntp_message.tsTransmit);
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F(" (T - D): ")); CC3KPrinter->print(sntp_message.tsTransmit.seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(sntp_message.tsTransmit.fraction,HEX); }
			#endif
			NTPdiv2(&sntp_message.tsTransmit);
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F(" (T - D)/2: ")); CC3KPrinter->print(sntp_message.tsTransmit.seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(sntp_message.tsTransmit.fraction,HEX); }
			#endif

			//Correction is returned in tsTransmit
			AddNTPtime(&sntp_message.tsReceive, &sntp_message.tsTransmit);

			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F(" Offset: ")); CC3KPrinter->print(sntp_message.tsTransmit.seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(sntp_message.tsTransmit.fraction,HEX); }
			#endif
			
			//Add correction to current ntp reference time
			AddNTPtime(&sntp_message.tsTransmit, &m_NTPReferenceTime); //adjust NTP reference time
			m_timeIsSet = true;
	
			#ifdef CLOCK_DEBUG
				NTPGetTime(&tsDestination, false);        //we'll display local time
				if (CC3KPrinter != 0) { CC3KPrinter->print(F(" time is ")); CC3KPrinter->print(tsDestination.seconds,HEX); CC3KPrinter->print(F(".")); CC3KPrinter->println(tsDestination.fraction,HEX); }
			#endif

			result = true;
		}
	}
	return result;
}

bool sntp::UpdateNTPTime()
{
	bool				portIsBound = false;
	int					sntpSocket;
	sockaddr_in			socketAddr;
	uint16_t			localPort;
	NTP_Pool_t			ntp_pool_list;         // list of NTP server pools
	NTP_Server_List_t	*pServerList;          // pointer to list of ntp servers returned by a server pool
	NTP_Server_List_t	ntp_server_list;       // local buffer for list of ntp servers returned by a server pool
	uint8_t				ntp_server_count;      // number of ntp servers in ntp_server_list
	bool				checkLocal;            // true if we haven't searched the local NTP server list.
	bool				checkGlobal;           // true if we haven't searched the global NTP server list.

	#ifdef CLOCK_DEBUG
		if (CC3KPrinter != 0) { CC3KPrinter->println(F("sntp.update")); }
	#endif
	
	sntpSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (sntpSocket >= 0)               //got one?
	{
		while (!portIsBound)
		{	//set up the sockAddr
			  
			memset(&socketAddr, 0, sizeof(sockaddr_in));					//zero it
			localPort = (uint16_t)random(0xC000, 0xFFFF);					//generate random port number in range C000-FFFF
			socketAddr.sin_family = AF_INET;								//IP version 4
			socketAddr.sin_addr.s_addr = 0;								//local socket address
			socketAddr.sin_port = htons(localPort);                     //well-known NTP port number, assigned by IANA
			// bind the socket to the local port
			portIsBound = (0 == bind(sntpSocket, (sockaddr*)&socketAddr, sizeof(sockaddr_in)));
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F("local: ")); CC3KPrinter->print(socketAddr.sin_addr.s_addr, HEX); CC3KPrinter->print(F(": ")); CC3KPrinter->println(socketAddr.sin_port, HEX); }
			#endif
		}

		if (portIsBound)
		{
			#ifdef CLOCK_DEBUG
				if (CC3KPrinter != 0) { CC3KPrinter->print(F("Init SNTP bind socket ")); CC3KPrinter->print(sntpSocket); CC3KPrinter->print(F("to port ")); CC3KPrinter->print(socketAddr.sin_port); CC3KPrinter->println(F(" succeeded")); }
			#endif

			m_change_DST = 0;
			m_timeIsSet = false;
				
			while (!m_timeIsSet)      //stay here until we either get a time, or run out of servers
			{
				//start with user's NTP servers.  These may not be pool servers, so they'll only get one IP address from DNS
				ntp_pool_list = m_userServers;            //start with user's ntp server list
        m_localPool = ntp_us_pool_list;
        m_globalPool = ntp_global_pool_list;
				checkLocal = (NULL !=  m_localPool);   	// if that craps out, we'll try the local server-pool list
				checkGlobal = (NULL != m_globalPool);		//if that craps out, we'll try the global server-pool list
        #ifdef CLOCK_DEEP_DEBUG
          if (CC3KPrinter != 0) 
          { 
            CC3KPrinter->print(F("m_localPool: ")); CC3KPrinter->print(*m_localPool); CC3KPrinter->print(F("checkLocal: ")); CC3KPrinter->println(checkLocal);
            CC3KPrinter->print(F("m_globalPool: ")); CC3KPrinter->print(*m_globalPool); CC3KPrinter->print(F("checkGlobal: ")); CC3KPrinter->println(checkGlobal);
          }
        #endif
        #ifdef CLOCK_DEBUG
					if (CC3KPrinter != 0) { CC3KPrinter->print(F("try user's ntp server list: ")); CC3KPrinter->println((uint32_t)*ntp_pool_list); }
				#endif

				memset(&ntp_server_list, 0, sizeof(NTP_Server_List_t));
				pServerList = &ntp_server_list;           //server ip addresses returned here

				while ((!m_timeIsSet) && (pServerList))
				{
					//try to get a server list.
					ntp_server_count = GetNTPServerList(ntp_pool_list, (uint32_t*)pServerList, MAX_NTP_SERVERS); // Just returns if pServerList is NULL
					#ifdef CLOCK_DEEP_DEBUG
						dumpBlock1((char*)pServerList, ntp_server_count * sizeof(uint32_t));
					#endif

					int i = 0;
					while ((!m_timeIsSet) && (i++ < ntp_server_count) && (pServerList))
					{
						uint32_t serverAddr = htonl(*(uint32_t*)pServerList++);
						m_timeIsSet = SNTP_GetTime(sntpSocket, &serverAddr);
					}

					if (!m_timeIsSet)
					{
						pServerList = &ntp_server_list;           //reset pServerList pointer

						if (checkLocal)
						{
							ntp_pool_list = m_localPool;    //try local ntp server pool list ('local' means 'regional', e.g., US, North America, etc)
							checkLocal = false;
							#ifdef CLOCK_DEBUG
								if (CC3KPrinter != 0) { CC3KPrinter->print(F("try local ntp_pool_list: ")); CC3KPrinter->println((uint32_t)*ntp_pool_list); }
							#endif
						}
						else
						{
							if (checkGlobal)
							{
								ntp_pool_list = m_globalPool;   //now try global (i.e., default) ntp server pool list
								checkGlobal = false;
								#ifdef CLOCK_DEBUG
								if (CC3KPrinter != 0) { CC3KPrinter->print(F("try global ntp_pool_list: ")); CC3KPrinter->println((uint32_t)*ntp_pool_list); }
								#endif
							}
							else
							{
								pServerList = NULL;                  //rats.  came up empty.  This will get us out of the loop
								ntp_server_count = 0;
								
							} //else not checkGlobal
						} //else not checkLocal
					} //if (!m_timeIsSet)
				} //while ((!m_timeIsSet) && (pServerList))

				if (m_timeIsSet)
				{
//						//If necessary, make change to/from Daylight Savings Time
//						// NOTE: m_change_DST will have been set on the previous iteration of the loop, so that
//						// we update the time AFTER we wake up. This is because the timer will have been adjusted
//						// to wake up when the time-change happens
//						// 'm_change_DST' is tri-state: 0 or no change, +1 for spring change, -1 for fall change.
//						UpdateDST(m_change_DST);
//					  
//						//Now, see if the time change will happen before the next scheduled wake-up.
//						// If so, shorten  sleep-time so we wake up at the time-change
//						TaskLock(&Clock.lock);
//						m_change_DST = Check_DST(NTPGetTime(&m_tempTS, false), &m_sleepTime);   //if necessary, shortens m_sleepTime so we wake up at the time-change
//						TaskUnlock(&Clock.lock);                                          //  Also makes sure current DST settings are correct.
//					  
//						strBufLen = 32;
//						Trace("The time is now %s\r\n", FormatFullNTPtime(NTPGetTime(&m_tempTS, true), strBuf, &strBufLen, true));
//
//
				}
			}	// while (!m_timeIsSet)
			closesocket(sntpSocket);
			sntpSocket = -1;
		} //if (portIsBound)
		else //socket bind failed
		{
			if (CC3KPrinter != 0) { CC3KPrinter->print(F("Init SNTP bind socket ")); CC3KPrinter->print(sntpSocket); CC3KPrinter->print(F("to port ")); CC3KPrinter->print(SNTP_PORT); CC3KPrinter->println(F("failed")); }
			closesocket(sntpSocket);
			sntpSocket = -1;
		}
	} //if (sntpSocket >= 0)
	else    // didn't get a socket
	{
		if (CC3KPrinter != 0) { CC3KPrinter->println(F("Failed to get a socket")); }
	}
	#ifdef CLOCK_DEBUG
		if (CC3KPrinter != 0)
		{
			CC3KPrinter->println(F("exit sntp.update"));
			CC3KPrinter->print(F("m_std_UTC_offset.seconds: ")); CC3KPrinter->println(m_std_UTC_offset.seconds, HEX);
			CC3KPrinter->print(F("m_dst_UTC_offset.seconds: ")); CC3KPrinter->println(m_dst_UTC_offset.seconds, HEX);
		}
	#endif
	return m_timeIsSet;
}



//sntp SNTP;

