# Modeled after https://github.com/cocotb/cocotb/blob/master/examples/Makefile
GATES := nand not and or xor mux demux not16 and16 or16 mux16 mux4way16

.PHONY: $(GATES)

.PHONY: all
all: $(GATES)

$(GATES):
	@cd $@ && $(MAKE)

.PHONY: clean
clean:
	$(foreach GATE, $(GATES), $(MAKE) -C $(GATE) clean;)

regression:
	$(foreach GATE, $(GATES), $(MAKE) -C $(GATE) regression;)
