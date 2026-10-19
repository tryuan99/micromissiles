module bailey #(
    parameter CLK_FREQ_HZ = 100_000_000,
    parameter DEBOUNCE_TIME_MS = 20,
    parameter NUM_SWITCHES = 4,
    parameter NUM_BUTTONS = 4,
    parameter NUM_LEDS = 4,
    parameter NUM_ADC_SAMPLES = 128,
    parameter NUM_BITS_PER_CHANNEL = 16,
    parameter NUM_CHANNELS_PER_DOUT = 2
)(
    input CLK,
    input RESET,

    output UART_RXD_OUT,
    input UART_TXD_IN,

    input ADC_DOUT0,
    input ADC_DOUT1,
    input ADC_FS_ADC,
    input ADC_SCLK,
    output BEAMFORMER_TX_LOAD,
    output BEAMFORMER_TR,
    output ADC_CONV_START_N,
    input ADC_DATA_READY,

    output ADC_DOUT0_OUT,
    output ADC_DOUT1_OUT,

    input [NUM_SWITCHES-1:0] SWITCHES,
    input [NUM_BUTTONS-1:0] BUTTONS,
    output [NUM_LEDS-1:0] LEDS
);
    // ADC sample width.
    localparam integer SAMPLE_INDEX_WIDTH = (NUM_ADC_SAMPLES > 0) ? $clog2(NUM_ADC_SAMPLES + 1) : 1;

    // ADC DOUT bit width.
    localparam integer DOUT_WIDTH = NUM_BITS_PER_CHANNEL * NUM_CHANNELS_PER_DOUT;

    // ADC bit index width.
    localparam integer BIT_INDEX_WIDTH = (DOUT_WIDTH > 0) ? $clog2(DOUT_WIDTH + 1) : 1;

    // ADC control states.
    localparam ADC_CONTROL_STATE_IDLE = 1'b0;
    localparam ADC_CONTROL_STATE_READING = 1'b1;

    // ADC capture states.
    localparam ADC_CAPTURE_STATE_IDLE = 2'b00;
    localparam ADC_CAPTURE_STATE_FIRST = 2'b01;
    localparam ADC_CAPTURE_STATE_SAMPLING = 2'b10;

    wire clk;
    wire rst;
    wire [NUM_SWITCHES-1:0] switch_synchronizer_in;
    wire [NUM_SWITCHES-1:0] switch_synchronizer_out;
    wire [NUM_SWITCHES-1:0] switch_debouncer_in;
    wire [NUM_SWITCHES-1:0] switch_debouncer_out;
    wire [NUM_BUTTONS-1:0] button_synchronizer_in;
    wire [NUM_BUTTONS-1:0] button_synchronizer_out;
    wire [NUM_BUTTONS-1:0] button_debouncer_in;
    wire [NUM_BUTTONS-1:0] button_debouncer_out;

    // FPGA clock domain.
    reg adc_control_state;
    wire adc_trigger;
    reg adc_conv_start_n;
    reg [SAMPLE_INDEX_WIDTH-1:0] adc_sample_index;
    wire adc_sample_valid;

    // ADC clock domain.
    reg [1:0] adc_capture_state;
    reg [DOUT_WIDTH-1:0] adc_shift_dout0;
    reg [DOUT_WIDTH-1:0] adc_shift_dout1;
    reg [SAMPLE_INDEX_WIDTH-1:0] adc_capture_index;
    reg [BIT_INDEX_WIDTH-1:0] adc_capture_bit_index;

    reg [DOUT_WIDTH-1:0] adc_data;
    reg adc_data_ready;

    wire [DOUT_WIDTH-1:0] adc_fifo_wr_data;
    wire adc_fifo_wr_en;
    wire adc_fifo_full;
    wire [DOUT_WIDTH-1:0] adc_fifo_rd_data;
    wire adc_fifo_rd_en;
    wire adc_fifo_empty;

    // Clock and reset.
    assign clk = CLK;
    assign rst = ~RESET;

     // Switches.
    synchronizer #(
        .WIDTH(NUM_SWITCHES)
    ) switch_synchronizer (
        .clk(clk),
        .rst(rst),
        .in(switch_synchronizer_in),
        .out(switch_synchronizer_out)
    );

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

    assign switch_synchronizer_in = SWITCHES;
    assign switch_debouncer_in = switch_synchronizer_out;

    // Buttons.
    synchronizer #(
        .WIDTH(NUM_BUTTONS)
    ) button_synchronizer (
        .clk(clk),
        .rst(rst),
        .in(button_synchronizer_in),
        .out(button_synchronizer_out)
    );

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

    assign button_synchronizer_in = BUTTONS;
    assign button_debouncer_in = button_synchronizer_out;

    // ADC.
    assign adc_trigger = button_debouncer_out[0];

    // ADC control state machine for controlling the ADC and copying the samples from the FIFO to memory. This state machine lives in the FPGA's clock domain.
    always @(posedge clk or posedge rst) begin
        if (rst) begin
            adc_control_state <= ADC_CONTROL_STATE_IDLE;
            adc_conv_start_n <= 1;
            adc_sample_index <= 0;
        end
        else begin
            case (adc_control_state)
                ADC_CONTROL_STATE_IDLE: begin
                    if (adc_trigger) begin
                        // ADC conversion was triggered.
                        adc_control_state <= ADC_CONTROL_STATE_READING;
                        adc_conv_start_n <= 0;
                        adc_sample_index <= 0;
                    end
                end
                ADC_CONTROL_STATE_READING: begin
                    if (adc_sample_valid) begin
                        if (adc_sample_index == NUM_ADC_SAMPLES - 1) begin
                            adc_conv_start_n <= 1;
                            adc_sample_index <= 0;
                            adc_control_state <= ADC_CONTROL_STATE_IDLE;
                        end
                        else begin
                            adc_sample_index <= adc_sample_index + 1;
                        end
                    end
                end
                default: begin
                    adc_control_state <= ADC_CONTROL_STATE_IDLE;
                end
            endcase
        end
    end

    assign adc_sample_valid = (adc_control_state == ADC_CONTROL_STATE_READING) && !adc_fifo_empty;

    // ADC capture state machine for reading the samples from the ADC and buffering them in the FIFO. This state machine lives in the ADC's clock domain.
    always @(posedge ADC_SCLK or posedge rst) begin
        if (rst) begin
            adc_capture_state <= ADC_CAPTURE_STATE_IDLE;
            adc_shift_dout0 <= 0;
            adc_shift_dout1 <= 0;
            adc_capture_index <= 0;
            adc_capture_bit_index <= 0;

            adc_data <= 0;
            adc_data_ready <= 0;
        end
        else begin
            case (adc_capture_state)
                ADC_CAPTURE_STATE_IDLE: begin
                    adc_capture_bit_index <= 0;
                    adc_data_ready <= 0;

                    if (ADC_FS_ADC && ADC_DATA_READY) begin
                        adc_capture_state <= ADC_CAPTURE_STATE_FIRST;
                    end
                end
                ADC_CAPTURE_STATE_FIRST: begin
                    adc_data_ready <= 0;

                    // Ignore the first sample.
                    if (ADC_FS_ADC && ADC_DATA_READY) begin
                        adc_shift_dout0 <= {adc_shift_dout0[DOUT_WIDTH-2:0], ADC_DOUT0};
                        adc_shift_dout1 <= {adc_shift_dout1[DOUT_WIDTH-2:0], ADC_DOUT1};
                        adc_capture_bit_index <= adc_capture_bit_index + 1;
                        adc_capture_state <= ADC_CAPTURE_STATE_SAMPLING;
                    end
                end
                ADC_CAPTURE_STATE_SAMPLING: begin
                    if (ADC_DATA_READY) begin
                        if (adc_capture_bit_index == DOUT_WIDTH - 1) begin
                            // Write the captured samples to the FIFO.
                            if (!adc_fifo_full) begin
                                adc_data <= {adc_shift_dout0[DOUT_WIDTH-2:0], ADC_DOUT0};
                                adc_data_ready <= 1;
                            end

                            adc_shift_dout0 <= 0;
                            adc_shift_dout1 <= 0;
                            adc_capture_bit_index <= 0;

                            if (adc_capture_index == NUM_ADC_SAMPLES - 1) begin
                                adc_capture_index <= 0;
                                adc_capture_state <= ADC_CAPTURE_STATE_IDLE;
                            end
                            else begin
                                adc_capture_index <= adc_capture_index + 1;
                            end
                        end
                        else begin
                            adc_data_ready <= 0;
                            adc_shift_dout0 <= {adc_shift_dout0[DOUT_WIDTH-2:0], ADC_DOUT0};
                            adc_shift_dout1 <= {adc_shift_dout1[DOUT_WIDTH-2:0], ADC_DOUT1};
                            adc_capture_bit_index <= adc_capture_bit_index + 1;
                        end
                    end
                end
                default: begin
                    adc_capture_state <= ADC_CAPTURE_STATE_IDLE;
                end
            endcase
        end
    end

    fifo #(
        .DATA_WIDTH(DOUT_WIDTH),
        .ADDR_WIDTH(8)
    ) adc_fifo (
        .wr_clk(ADC_SCLK),
        .wr_rst(rst),
        .wr_en(adc_fifo_wr_en),
        .wr_data(adc_fifo_wr_data),
        .full(adc_fifo_full),
        .rd_clk(clk),
        .rd_rst(rst),
        .rd_en(adc_fifo_rd_en),
        .rd_data(adc_fifo_rd_data),
        .empty(adc_fifo_empty)
    );

    assign adc_fifo_wr_data = adc_data;
    assign adc_fifo_wr_en = adc_data_ready;
    assign adc_fifo_rd_en = adc_sample_valid;

    assign ADC_CONV_START_N = adc_conv_start_n;
    assign ADC_DOUT0_OUT = ADC_DOUT0;
    assign ADC_DOUT1_OUT = ADC_DOUT1;

    // LEDs.
    assign LEDS[0] = rst;
    assign LEDS[1] = ~adc_conv_start_n;
    assign LEDS[2] = ADC_DATA_READY;
    assign LEDS[3] = 1'b0;
endmodule
