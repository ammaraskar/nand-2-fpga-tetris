.PHONY: clean test
clean:
test:

hello.vpp: hello.v
	iverilog -o hello.vpp hello.v
