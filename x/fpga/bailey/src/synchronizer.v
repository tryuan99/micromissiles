module synchronizer #(
    parameter WIDTH = 1,
    parameter RESET_VALUE = 0
)(
    input clk,
    input rst,
    input [WIDTH-1:0] in,
    output [WIDTH-1:0] out
);
    reg [WIDTH-1:0] sync_0;
    reg [WIDTH-1:0] sync_1;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            sync_0 <= {WIDTH{RESET_VALUE}};
            sync_1 <= {WIDTH{RESET_VALUE}};
        end
        else begin
            sync_0 <= in;
            sync_1 <= sync_0;
        end
    end

    assign out = sync_1;
endmodule
