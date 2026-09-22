#!/usr/bin/env python3
"""Exercise the production AROS directory adapter against native-path contracts.

Host test: only the OS getcwd/chdir boundary is replaced. Guest UI regression
steps and ABI-specific results are in the linked fileselector report.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'work/grafx2/src/io.c').read_text()
start = source.index('int Change_directory(const char * path)')
end = source.index('\nint Remove_path(', start)
function = source[start:end]
harness = r'''
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#define __AROS__ 1
#define GFX2_Log(...) ((void)0)
static const char *cwd;
static char destination[512];
static char *test_getcwd(char *buf, size_t size) {
  (void)buf; (void)size;
  return cwd ? strdup(cwd) : NULL;
}
static int test_chdir(const char *path) {
  assert(path != NULL);
  snprintf(destination, sizeof(destination), "%s", path);
  return 0;
}
#define getcwd test_getcwd
#define chdir test_chdir
'''
cases = r'''
static void parent(const char *from, const char *to) {
  cwd = from;
  destination[0] = 0;
  assert(Change_directory("/") == 0);
  if (strcmp(destination, to)) {
    fprintf(stderr, "parent(%s): expected %s, got %s\n", from, to, destination);
    exit(1);
  }
}
int main(void) {
  parent("AROS:Burntime", "AROS:");
  parent("AROS:GrafX2/data", "AROS:GrafX2");
  parent("Qemu Vvfat:Folder with spaces/data", "Qemu Vvfat:Folder with spaces");
  parent("AROS:", "AROS:");
  cwd = NULL;
  destination[0] = 0;
  assert(Change_directory("/") == -1);
  assert(destination[0] == 0);
  assert(Change_directory(NULL) == -1);
  assert(Change_directory("AROS:GrafX2") == 0);
  assert(strcmp(destination, "AROS:GrafX2") == 0);
  puts("PASS: native parent paths, volume root, getcwd failure, NULL and ordinary paths");
}
'''
with tempfile.TemporaryDirectory(prefix='grafx2-parent-test-') as temp:
    path = Path(temp)
    (path / 'test.c').write_text(harness + function + cases)
    subprocess.run(['cc', '-Wall', '-Wextra', str(path / 'test.c'), '-o', str(path / 'test')], check=True)
    subprocess.run([str(path / 'test')], check=True)
