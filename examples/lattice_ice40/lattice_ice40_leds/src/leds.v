//-- File: src/led.v
module leds(output wire D1,
            output wire D2,
            output wire D3,
            output wire D4,
            output wire D5);

//-- icestick Red leds
assign D1 = 1'b1;
assign D2 = 1'b1;
assign D3 = 1'b1;
assign D4 = 1'b1;

//-- Green led
assign D5 = 1;

endmodule
