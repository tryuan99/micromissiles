module switch_debouncer #(
    parameter CLK_FREQ_HZ = 100_000_000,
    parameter DEBOUNCE_TIME_MS = 20,
    parameter WIDTH = 1
)(
    input clk,
    input rst,
    input [WIDTH-1:0] in,
    output reg [WIDTH-1:0] out
);
    // Number of clock cycles in a debounce period.
    localparam integer MAX_COUNT = (CLK_FREQ_HZ / 1000) * DEBOUNCE_TIME_MS;
    localparam integer COUNTER_WIDTH = (MAX_COUNT > 0) ? $clog2(MAX_COUNT + 1) : 1;

    reg [COUNTER_WIDTH-1:0] counter [WIDTH-1:0];
    wire [WIDTH-1:0] sync_out;

    // Synchronize the asynchronous switch inputs into the local clock domain.
    synchronizer #(
        .WIDTH(WIDTH)
    ) input_synchronizer (
        .clk(clk),
        .rst(rst),
        .in(in),
        .out(sync_out)
    );

    // Debounce each switch.
    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin
            always @(posedge clk or posedge rst) begin
                if (rst) begin
                    counter[i] <= 0;
                    out[i] <= 0;
                end
                else begin
                    if (sync_out[i] != out[i]) begin
                        if (counter[i] == MAX_COUNT - 1) begin
                            out[i]     <= sync_out[i];
                            counter[i] <= 0;
                        end
                        else begin
                            counter[i] <= counter[i] + 1;
                        end
                    end
                    else begin
                        counter[i] <= 0;
                    end
                end
            end
        end
    endgenerate
endmodule
