ifndef __ITERATE__
__ITERATE__ := 1

NAME := iterate

ITERATE_LOCAL := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VERILOG_SOURCES += $(ITERATE_LOCAL)/../systemverilog/$(NAME).sv
VERILOG_SOURCES += $(ITERATE_LOCAL)/../systemverilog/page/$(NAME)_page.sv
VERILOG_SOURCES += $(ITERATE_LOCAL)/../systemverilog/page/$(NAME)_page_i.sv

include $(ITERATE_LOCAL)/../../deps/range_i/src/cocotb/include.mk
include $(ITERATE_LOCAL)/../../deps/value_i/src/cocotb/include.mk

endif
