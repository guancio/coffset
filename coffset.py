#!/usr/bin/python


def dump_field(type_name, field_name):
    print "// dumping %s.%s" % (type_name, field_name)
    curr_field = {}
    (inp, outp) = os.popen2("arm-none-eabi-gdb build/sth_ovp_arm9.elf --batch -ex \"print (int)&(((%s*)0)->%s)\"" % (type_name, field_name))
    txt = outp.read()
    curr_field["offset"] = int(txt.split()[-1])
         
    (inp, outp) = os.popen2("arm-none-eabi-gdb build/sth_ovp_arm9.elf --batch -ex \"whatis ((%s*)0)->%s\"" % (type_name, field_name))
    txt = outp.read()
    txt = txt.strip().split(" = ")[-1]
    curr_field["type"] = txt.split()[0]
    curr_field["pointer"] = (txt.find("*") > 0)
    curr_field["len"] = 0
    if txt.find("[") > 0:
        curr_field["len"] = int(txt.split("[")[1].split("]")[0])
         
    (inp, outp) = os.popen2("arm-none-eabi-gdb build/sth_ovp_arm9.elf --batch -ex \"print sizeof(((%s*)0)->%s)\"" % (type_name, field_name))
    txt = outp.read()
    curr_field["size"] = int(txt.split()[-1])
    return curr_field


def dump_type(type_name):
    print "// dumping %s" % (type_name)
    curr_type = {}
    (inp, outp) = os.popen2("arm-none-eabi-gdb build/sth_ovp_arm9.elf --batch -ex \"ptype %s\"" % type_name)
    txt = outp.read()
    if txt.find("(*)") >= 0:
        return "fpointer"
    if txt.find("type = enum") >= 0:
        return "enum"
    if txt.strip() == "type = %s" % type_name:
        return "primitive"
    if txt.find("{") < 0:
        return txt.split("=")[-1].strip()
    print "/* ptype output \n%s\n*/" % txt.strip()
    txt = txt.split("{")[-1].split("}")[0]
    fields = txt.split(";")
    fields = [f.strip() for f in fields if f.strip() != '']
    fields = [f.split()[-1] for f in fields]
    # removes array annotation
    fields = [f.split("[")[0] for f in fields]
    # removes fpoint annotations
    fields = [f.split(")")[0].split("(")[-1] for f in fields]
    # removes pointers annotations
    fields = [f.split("*")[-1] for f in fields]
     
    for field_name in fields:
        curr_field = dump_field(type_name, field_name)
        curr_type[field_name] = curr_field

    return curr_type


import os
(inp, outp) = os.popen2("arm-none-eabi-gdb build/sth_ovp_arm9.elf --batch -ex \"info types\"")
res = outp.read()
pos = res.find("typedef")
res = res[pos:]
res = res.split(";")
res = [r for r in res if r.find("typedef") >= 0]
types = [r.split()[-1] for r in res]

st_types = {}

#type_name = "virtual_machine"
print "/*\n%s\n*/"%str(types)
for type_name in types:
    if st_types.has_key(type_name):
        continue
    curr_type = dump_type(type_name)
    st_types[type_name] = curr_type

import json
print json.dumps(st_types, sort_keys=True, indent=4)

