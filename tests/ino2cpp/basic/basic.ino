typedef struct Item item;
struct Item {
   byte  foo[50];
   int   bar;
   void (*noob)(item*);
};

// test callback
class Foo {

    public:
        Foo(void (*function)()) {
            #warning "Line number is 13"
        }

        bool childFunc() {

        }

};

Foo foo(&fooCallback);

//

void setup() {
    struct Item item1;
    myFunction(&item1);
}


void loop() {

}

void myFunction(struct Item *item) {

}

void fooCallback(){

}
