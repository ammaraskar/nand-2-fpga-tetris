ALL: my_design

my_design: counter.v counter_test.sv
	iverilog -o my_design counter.v counter_test.sv

.PHONY: clean
clean:
	rm -f my_design

.PHONY: test
test: my_design
	vvp my_design
