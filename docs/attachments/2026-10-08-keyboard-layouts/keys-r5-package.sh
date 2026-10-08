#!/bin/bash
# Revision 5 package test keys (QEMU qcodes = PC positions), Italian keymap.
V=tools/vmctl.py
$V key a shift-a caps_lock a shift-a shift_r-a caps_lock a
$V key equal shift-equal bracket_right shift-bracket_right alt_r-semicolon semicolon shift-semicolon kp_multiply y z
