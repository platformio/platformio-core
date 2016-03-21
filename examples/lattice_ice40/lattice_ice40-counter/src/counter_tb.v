`timescale 100 ns / 10 ns
`default_nettype none

module counter_tb;

localparam N = 6;  //-- Counter bits length

reg clk = 0;

wire [4:0] leds;

//-- Clock generator
always
  # 0.5 clk <= ~clk;

  counter #(
             .N(N)
  )  CONT0 (
             .clk(clk),
             .leds(leds)
  );

initial begin

      //-- File where to store the simulation
      $dumpfile("counter_tb.vcd");
      $dumpvars(0, counter_tb);

      #200 $display("END of the simulation");
      $finish;
    end


endmodule
