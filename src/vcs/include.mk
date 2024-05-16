ITERATE_LOCAL := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

include $(ITERATE_LOCAL)/../../deps/range_i/gen/vcs/include.mk
include $(ITERATE_LOCAL)/../../deps/value_i/gen/vcs/include.mk

VERILOG_SOURCES += \
	$(ITERATE_LOCAL)/../sverilog/iterate.sv
