//--------------------------------------------------------------------
//-- IceZUM Alhambra test
//-- Hello world example
//-- Turn on all the yellow leds
//--------------------------------------------------------------------
//-- (c) BQ March, 2016. Written by Juan Gonzalez (obijuan)
//--------------------------------------------------------------------
//-- Releases under the GPL v2+ license
//--------------------------------------------------------------------

module leds_on(output wire [7:0] LPORT);

//-- Turn on all the leds
assign LPORT = 8'hFF;

endmodule
