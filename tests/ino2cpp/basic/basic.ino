struct MyItem {
   byte  foo[50];
   int   bar;
};

void setup() {
    struct MyItem item1;
    myFunction(&item1);


}

#warning "Line number is 13"

void loop() {

}

void myFunction(struct MyItem *item) {

}
