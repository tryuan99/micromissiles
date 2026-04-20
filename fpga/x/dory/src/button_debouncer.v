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
    localparam integer COUNTER_WIDTH = (MAX_COUNT > 0) ? $clog2(MAX_COUNT + 1) : 1;

    reg [COUNTER_WIDTH-1:0] counter [WIDTH-1:0];
    reg [WIDTH-1:0] state;
    reg [WIDTH-1:0] state_prev;
    wire [WIDTH-1:0] sync_out;

    // Synchronize the asynchronous button inputs into the local clock domain.
    synchronizer #(
        .WIDTH(WIDTH)
    ) input_synchronizer (
        .clk(clk),
        .rst(rst),
        .in(in),
        .out(sync_out)
    );

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
                    if (sync_out[i] != state[i]) begin
                        if (counter[i] == MAX_COUNT - 1) begin
                            state[i]   <= sync_out[i];
                            counter[i] <= 0;
                        end
                        else begin
                            counter[i] <= counter[i] + 1;
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
