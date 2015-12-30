#include "mbed.h"
#include "EthernetInterface.h"
#include "HTTPClient.h"

EthernetInterface eth;
HTTPClient http;
char str[512];

int main()
{
    eth.init(); //Use DHCP

    eth.connect();

    //GET data
    printf("\nTrying to fetch page...\n");
    int ret = http.get("https://developer.mbed.org/media/uploads/donatien/hello.txt", str, 128);
    if (!ret)
    {
      printf("Page fetched successfully - read %d characters\n", strlen(str));
      printf("Result: %s\n", str);
    }
    else
    {
      printf("Error - ret = %d - HTTP return code = %d\n", ret, http.getHTTPResponseCode());
    }

    //POST data
    HTTPMap map;
    HTTPText inText(str, 512);
    map.put("Hello", "World");
    map.put("test", "1234");
    printf("\nTrying to post data...\n");
    ret = http.post("http://httpbin.org/post", map, &inText);
    if (!ret)
    {
      printf("Executed POST successfully - read %d characters\n", strlen(str));
      printf("Result: %s\n", str);
    }
    else
    {
      printf("Error - ret = %d - HTTP return code = %d\n", ret, http.getHTTPResponseCode());
    }

    //PUT data
    strcpy(str, "This is a PUT test!");
    HTTPText outText(str);
    //HTTPText inText(str, 512);
    printf("\nTrying to put resource...\n");
    ret = http.put("http://httpbin.org/put", outText, &inText);
    if (!ret)
    {
      printf("Executed PUT successfully - read %d characters\n", strlen(str));
      printf("Result: %s\n", str);
    }
    else
    {
      printf("Error - ret = %d - HTTP return code = %d\n", ret, http.getHTTPResponseCode());
    }

    //DELETE data
    //HTTPText inText(str, 512);
    printf("\nTrying to delete resource...\n");
    ret = http.del("http://httpbin.org/delete", &inText);
    if (!ret)
    {
      printf("Executed DELETE successfully - read %d characters\n", strlen(str));
      printf("Result: %s\n", str);
    }
    else
    {
      printf("Error - ret = %d - HTTP return code = %d\n", ret, http.getHTTPResponseCode());
    }

    eth.disconnect();

    while(1) {
    }
}
