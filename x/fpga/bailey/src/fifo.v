module fifo #(
    parameter DATA_WIDTH = 16,
    parameter ADDR_WIDTH = 4
)(
    input wr_clk,
    input wr_rst,
    input wr_en,
    input [DATA_WIDTH-1:0] wr_data,
    output full,

    input rd_clk,
    input rd_rst,
    input rd_en,
    output reg [DATA_WIDTH-1:0] rd_data,
    output empty
);
    // FIFO depth.
    localparam integer FIFO_DEPTH = 1 << ADDR_WIDTH;

    reg [DATA_WIDTH-1:0] buffer [0:FIFO_DEPTH-1];

    reg [ADDR_WIDTH:0] wr_bin = 0;
    reg [ADDR_WIDTH:0] wr_gray = 0;

    reg [ADDR_WIDTH:0] rd_bin = 0;
    reg [ADDR_WIDTH:0] rd_gray = 0;

    wire [ADDR_WIDTH:0] wr_bin_next;
    wire [ADDR_WIDTH:0] wr_gray_next;

    wire [ADDR_WIDTH:0] rd_bin_next;
    wire [ADDR_WIDTH:0] rd_gray_next;

    assign wr_bin_next  = wr_bin + (wr_en && !full);
    assign rd_bin_next  = rd_bin + (rd_en && !empty);

    assign wr_gray_next = (wr_bin_next >> 1) ^ wr_bin_next;
    assign rd_gray_next = (rd_bin_next >> 1) ^ rd_bin_next;

    reg [ADDR_WIDTH:0] rd_gray_sync1 = 0;
    reg [ADDR_WIDTH:0] rd_gray_sync2 = 0;
    reg [ADDR_WIDTH:0] wr_gray_sync1 = 0;
    reg [ADDR_WIDTH:0] wr_gray_sync2 = 0;

    always @(posedge wr_clk or posedge wr_rst) begin
        if (wr_rst) begin
            rd_gray_sync1 <= 0;
            rd_gray_sync2 <= 0;
        end
        else begin
            rd_gray_sync1 <= rd_gray;
            rd_gray_sync2 <= rd_gray_sync1;
        end
    end

    always @(posedge rd_clk or posedge rd_rst) begin
        if (rd_rst) begin
            wr_gray_sync1 <= 0;
            wr_gray_sync2 <= 0;
        end
        else begin
            wr_gray_sync1 <= wr_gray;
            wr_gray_sync2 <= wr_gray_sync1;
        end
    end

    always @(posedge wr_clk or posedge wr_rst) begin
        if (wr_rst) begin
            wr_bin  <= 0;
            wr_gray <= 0;
        end else begin
            if (wr_en && !full) begin
                buffer[wr_bin[ADDR_WIDTH-1:0]] <= wr_data;
            end

            wr_bin  <= wr_bin_next;
            wr_gray <= wr_gray_next;
        end
    end

    always @(posedge rd_clk or posedge rd_rst) begin
        if (rd_rst) begin
            rd_bin  <= 0;
            rd_gray <= 0;
            rd_data <= 0;
        end else begin
            if (rd_en && !empty) begin
                rd_data <= buffer[rd_bin[ADDR_WIDTH-1:0]];
            end

            rd_bin  <= rd_bin_next;
            rd_gray <= rd_gray_next;
        end
    end

    assign empty = (rd_gray == wr_gray_sync2);
    assign full  = (wr_gray == {~rd_gray_sync2[ADDR_WIDTH:ADDR_WIDTH-1], rd_gray_sync2[ADDR_WIDTH-2:0]});
endmodule
