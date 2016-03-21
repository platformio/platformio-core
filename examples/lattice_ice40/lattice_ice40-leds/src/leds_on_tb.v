//-------------------------------------------------------------------
//-- leds_on_tb.v
//-- Testbench
//-------------------------------------------------------------------
//-- BQ March 2016. Written by Juan Gonzalez (Obijuan)
//-------------------------------------------------------------------
`default_nettype none
`timescale 100 ns / 10 ns

module leds_on_tb();

//-- Simulation time: 1us (10 * 100ns)
parameter DURATION = 10;

//-- Clock signal. It is not used in this simulation
reg clk = 0;
always #0.5 clk = ~clk;

//-- Leds port
wire [7:0] lport;

//-- Instantiate the unit to test
leds_on UUT (.LPORT(lport));


initial begin

  //-- File were to store the simulation results
  $dumpfile("leds_on_tb.vcd");
  $dumpvars(0, leds_on_tb);

   #(DURATION) $display("End of simulation");
  $finish;
end

endmodule
