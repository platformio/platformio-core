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

template<class T> T Add(T n1, T n2) {
    return n1 + n2;
}

void setup() {
    struct Item item1;
    myFunction(&item1);
}

void loop() {

}

void myFunction(struct Item *item) {

}

#warning "Line number is 46"

void fooCallback(){

}

extern "C" {
void some_extern(const char *fmt, ...);
};

void some_extern(const char *fmt, ...) {

}

// юнікод
