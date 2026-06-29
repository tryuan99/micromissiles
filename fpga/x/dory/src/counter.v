module counter #(
    parameter CLK_FREQ_HZ = 100_000_000,
    parameter PERIOD_US = 100
)(
    input clk,
    input rst,
    output out
);
    localparam MAX_COUNT = (CLK_FREQ_HZ / 1_000_000) * PERIOD_US;
    localparam COUNTER_WIDTH = $clog2(MAX_COUNT);

    reg [COUNTER_WIDTH-1:0] count;
    reg pulse;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            count <= {COUNTER_WIDTH{1'b0}};
            pulse <= 1'b0;
        end
        else begin
            if (count == (MAX_COUNT - 1)) begin
                count <= {COUNTER_WIDTH{1'b0}};
                pulse <= 1'b1;
            end
            else begin
                count <= count + 1'b1;
                pulse <= 1'b0;
            end
        end
    end

    assign out = pulse;
endmodule
