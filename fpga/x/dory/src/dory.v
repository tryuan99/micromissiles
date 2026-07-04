module dory #(
    parameter CLK_FREQ_HZ = 100_000_000,
    parameter CHIRP_TO_CHIRP_TIME_US = 120,
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
    // DDS states.
    localparam DDS_STATE_IDLE = 2'b00;
    localparam DDS_STATE_WAIT = 2'b01;
    localparam DDS_STATE_RAMP = 2'b10;

    wire clk;
    wire rst;
    wire [NUM_SWITCHES-1:0] switch_debouncer_in;
    wire [NUM_SWITCHES-1:0] switch_debouncer_out;
    wire [NUM_BUTTONS-1:0] button_debouncer_in;
    wire [NUM_BUTTONS-1:0] button_debouncer_out;
    reg[1:0] dds_state;
    wire dds_trigger;
    wire dds_drctl;
    wire dds_drover;
    wire dds_min_ramp_done;
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
    counter #(
        .CLK_FREQ_HZ(CLK_FREQ_HZ),
        .PERIOD_US(CHIRP_TO_CHIRP_TIME_US),
        .WIDTH_US(1)
    ) dds_trigger_counter (
        .clk(clk),
        .rst(rst),
        .out(dds_trigger)
    );

    // The chirp is either triggered by the chirp-to-chirp time trigger or the button.
    assign dds_drctl = dds_trigger | button_debouncer_out[0];

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
            dds_state <= DDS_STATE_IDLE;
        end
        else begin
            case (dds_state)
                DDS_STATE_IDLE: begin
                    if (dds_drctl) begin
                        // DDS ramp has started.
                        dds_state <= DDS_STATE_WAIT;
                    end
                end
                DDS_STATE_WAIT: begin
                    if (!dds_drover) begin
                        // DDS over signal was de-asserted.
                        dds_state <= DDS_STATE_RAMP;
                    end
                end
                DDS_STATE_RAMP: begin
                    if (dds_drover) begin
                        // DDS ramp has finished.
                        dds_state <= DDS_STATE_IDLE;
                    end
                end
                default: begin
                    dds_state <= DDS_STATE_IDLE;
                end
            endcase
        end
    end

    assign DDS_DRCTL = dds_drctl;
    assign DDS_DRHOLD = button_debouncer_out[1];
    assign DDS_OSK = (dds_state == DDS_STATE_RAMP);

    // Enables.
    assign vco_rf_en = switch_debouncer_out[0];
    assign mixer_en = switch_debouncer_out[1];

    assign VCO_RF_EN = vco_rf_en;
    assign MIXER_EN = mixer_en;

    // LEDs.
    assign LEDS[0] = rst;
    assign LEDS[1] = vco_rf_en;
    assign LEDS[2] = mixer_en;
    assign LEDS[3] = (dds_state != DDS_STATE_IDLE);
endmodule
