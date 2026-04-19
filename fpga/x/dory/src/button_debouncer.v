module button_debouncer #(
    parameter CLK_FREQ_HZ = 100_000_000,
    parameter DEBOUNCE_TIME_MS = 20,
    parameter WIDTH = 1
)(
    input clk,
    input rst,
    input [WIDTH-1:0] in,
    output [WIDTH-1:0] out
);
    // Number of clock cycles in a debounce period.
    localparam integer MAX_COUNT = (CLK_FREQ_HZ / 1000) * DEBOUNCE_TIME_MS;

    reg [$clog2(MAX_COUNT)-1:0] counter [WIDTH-1:0];
    reg [WIDTH-1:0] sync_0;
    reg [WIDTH-1:0] sync_1 ;
    reg [WIDTH-1:0] state;
    reg [WIDTH-1:0] state_prev;

    // 2-stage synchronizer to avoid metastability.
    always @(posedge clk) begin
        sync_0 <= in;
        sync_1 <= sync_0;
    end

    // Debounce each button.
    genvar i;
    generate
        for (i = 0; i < WIDTH; i = i + 1) begin : debounce
            always @(posedge clk or posedge rst) begin
                if (rst) begin
                    counter[i]    <= 0;
                    state[i]      <= 0;
                    state_prev[i] <= 0;
                end
                else begin
                    if (sync_1[i] != state[i]) begin
                        counter[i] <= counter[i] + 1;
                        if (counter[i] >= MAX_COUNT) begin
                            state[i]   <= sync_1[i];
                            counter[i] <= 0;
                        end
                    end
                    else begin
                        counter[i] <= 0;
                    end
                    state_prev[i] <= state[i];
                end
            end
        end
    endgenerate

    // Edge detect.
    assign out = state & ~state_prev;
endmodule
