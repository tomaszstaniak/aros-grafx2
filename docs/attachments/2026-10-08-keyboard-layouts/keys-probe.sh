#!/bin/bash
# Same physical key sequence for every probe run (QEMU qcodes are PC positions).
V=tools/vmctl.py
$V key a shift-a shift_r-a caps_lock a shift-a caps_lock a
$V key equal shift-equal bracket_right shift-bracket_right
$V key alt_r-semicolon alt-semicolon alt_r-bracket_left shift-8 shift-6 y z
$V key kp_multiply kp_subtract kp_add kp_divide f1 left ctrl-a meta_l-a
$V key esc esc
