#define SQR(a) \
( a * a )

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
            #warning "Line number is 16"
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

#warning "Line number is 43"

void fooCallback(){

}
