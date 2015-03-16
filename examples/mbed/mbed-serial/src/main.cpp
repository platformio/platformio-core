#include "mbed.h"

Serial pc(USBTX, USBRX); // tx, rx

int main() {
    pc.printf("Hello World!\n\r");
    while(1) {
        pc.putc(pc.getc() + 1); // echo input back to terminal
    }
}