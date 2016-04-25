module counter #(
        parameter N = 29          //-- Counter bits lentgh
  )(
        input wire clk,
        output wire [4:0] leds
);

reg [N-1:0] cont;
reg rstn = 0;

//-- Initialization
always @(posedge clk)
  rstn <= 1;

//-- counter, with synchronous reset
always @(posedge clk)
  if (!rstn)
    cont <= 0;
  else
    cont <= cont + 1;

//-- Connect the 5 most significant bits to the leds
assign leds = cont[N-1: N-6];

endmodule
