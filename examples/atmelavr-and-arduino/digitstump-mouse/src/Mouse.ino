// DigiMouse test and usage documentation
// CAUTION!!!! This does click things!!!!!!!!
// Originally created by Sean Murphy (duckythescientist)

#include <DigiMouse.h>

void setup() {
  DigiMouse.begin(); //start or reenumerate USB - BREAKING CHANGE from old versions that didn't require this
}

void loop() {
  // If not using plentiful DigiMouse.delay(), make sure to call
  // DigiMouse.update() at least every 50ms
  
  // move across the screen
  // these are signed chars
  DigiMouse.moveY(10); //down 10
  DigiMouse.delay(500);
  DigiMouse.moveX(20); //right 20
  DigiMouse.delay(500);
  DigiMouse.scroll(5);
  DigiMouse.delay(500);
  
  // or DigiMouse.move(X, Y, scroll) works
  
  // three buttons are the three LSBs of an unsigned char
  DigiMouse.setButtons(1<<0); //left click
  DigiMouse.delay(500);
  DigiMouse.setButtons(0); //unclick all
  DigiMouse.delay(500);

  //or you can use these functions to click
  DigiMouse.rightClick();
  DigiMouse.delay(500);
  DigiMouse.leftClick();
  DigiMouse.delay(500);
  DigiMouse.middleClick();
  DigiMouse.delay(500);

  //for compatability with other libraries you can also use DigiMouse.move(X, Y, scroll, buttons)
}
