module dory #(
    parameter CLK_FREQ_HZ = 100_000_000,
    parameter DEBOUNCE_TIME_MS = 20,
    parameter NUM_SWITCHES = 4,
    parameter NUM_BUTTONS = 4,
    parameter NUM_LEDS = 4
)(
    input CLK,
    input RESET,

    output UART_RXD_OUT,
    input UART_TXD_IN,

    output DDS_DRCTL,
    output DDS_DRHOLD,
    input DDS_DROVER,
    output DDS_OSK,
    output VCO_RF_EN,
    output MIXER_EN,

    input [NUM_SWITCHES-1:0] SWITCHES,
    input [NUM_BUTTONS-1:0] BUTTONS,
    output [NUM_LEDS-1:0] LEDS
);
    wire clk;
    wire rst;
    wire [NUM_SWITCHES-1:0] switch_debouncer_in;
    wire [NUM_SWITCHES-1:0] switch_debouncer_out;
    wire [NUM_BUTTONS-1:0] button_debouncer_in;
    wire [NUM_BUTTONS-1:0] button_debouncer_out;
    reg dds_state;
    wire dds_drctl;
    wire dds_drover;
    wire vco_rf_en;
    wire mixer_en;

    // Clock and reset.
    assign clk = CLK;
    assign rst = ~RESET;

    // Switches.
    debouncer #(
        .CLK_FREQ_HZ(CLK_FREQ_HZ),
        .DEBOUNCE_TIME_MS(DEBOUNCE_TIME_MS),
        .WIDTH(NUM_SWITCHES)
    ) switch_debouncer (
        .clk(clk),
        .rst(rst),
        .in(switch_debouncer_in),
        .out(switch_debouncer_out)
    );

    assign switch_debouncer_in = SWITCHES;

    // Buttons.
    debouncer #(
        .CLK_FREQ_HZ(CLK_FREQ_HZ),
        .DEBOUNCE_TIME_MS(DEBOUNCE_TIME_MS),
        .WIDTH(NUM_BUTTONS)
    ) button_debouncer (
        .clk(clk),
        .rst(rst),
        .in(button_debouncer_in),
        .out(button_debouncer_out)
    );

    assign button_debouncer_in = BUTTONS;

    // DDS.
    assign dds_drctl = button_debouncer_out[0];

    synchronizer #(
        .WIDTH(1)
    ) dds_drover_synchronizer (
        .clk(clk),
        .rst(rst),
        .in(DDS_DROVER),
        .out(dds_drover)
    );

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            dds_state <= 0;
        end
        else begin
            if (!dds_state && dds_drctl) begin
                // DDS ramp has begun.
                dds_state <= 1;
            end
            else if (dds_state && dds_drover) begin
                dds_state <= 0;
            end
        end
    end

    assign DDS_DRCTL = dds_drctl;
    assign DDS_DRHOLD = button_debouncer_out[1];
    assign DDS_OSK = dds_state;

    // Enables.
    assign vco_rf_en = switch_debouncer_out[0];
    assign mixer_en = switch_debouncer_out[1];

    assign VCO_RF_EN = vco_rf_en;
    assign MIXER_EN = mixer_en;

    // LEDs.
    assign LEDS[0] = rst;
    assign LEDS[1] = vco_rf_en;
    assign LEDS[2] = mixer_en;
    assign LEDS[3] = dds_state;
endmodule
