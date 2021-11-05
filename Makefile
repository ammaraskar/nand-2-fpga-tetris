TOPLEVEL_LANG = verilog
VERILOG_SOURCES = counter.v
TOPLEVEL = dff
MODULE = counter_test
SIM = icarus

include $(shell cocotb-config --makefiles)/Makefile.sim
