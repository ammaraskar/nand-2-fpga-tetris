# Modeled after https://github.com/cocotb/cocotb/blob/master/examples/Makefile
GATES := ram16k program_counter register

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
