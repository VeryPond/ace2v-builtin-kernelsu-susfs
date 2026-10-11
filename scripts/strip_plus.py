#!/usr/bin/env python3
p = "/root/autodl-tmp/op/kernel/scripts/setlocalversion"
s = open(p).read()
before = s
s = s.replace("printf '%s' -dirty", "printf '%s' ''")
s = s.replace('res="$res${scm:++}"', 'res="$res"')
if s != before:
    open(p, "w").write(s)
    print("patched setlocalversion")
else:
    print("setlocalversion already clean")
