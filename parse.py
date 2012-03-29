#!/usr/bin/env python
import pprint

def parse_int(f):
    byte = f.read(1)
    num = 0
    while byte and byte != b'e':
        num = num * 10 + int(byte) - int(b'0')
        byte = f.read(1)
    return num

def parse_byte_string(f, firstByte):
    num = int(firstByte) - int(b'0')
    byte = f.read(1)
    while byte and byte != b':':
        num = num * 10 + int(byte) - int(b'0')
        byte = f.read(1)
    return f.read(num)

def parse_dict(f):
    print("Starting dict")
    state_stack.append({})
    isKey.append(True)

def parse_list(f):
    print("Starting list")
    state_stack.append([])

def add_data(struct, data):
    if type(struct) is dict:
        if isKey[-1]:
            key_stack.append(data)
        else:
            key = key_stack.pop()
            struct[key] = data
        isKey[-1] = not isKey[-1]
                
    elif type(struct) is list:
        struct.append(data)

    else:
        print("Ooops...")

state_stack = []
key_stack = []
isKey = []
lastObject = None

pp = pprint.PrettyPrinter()

with open("test2.torrent", "rb") as f:
    byte = f.read(1)
    while byte:
        if byte == b'd':
            parse_dict(f)

        elif byte == b'i':
            cur_struct = state_stack[-1]
            num = parse_int(f)
            add_data(cur_struct, num)
            print("Got integer: " + str(num))

        elif byte == b'l':
            parse_list(f)

        elif byte == b'e':
            data = state_stack.pop()
            if type(data) is dict:
                isKey.pop()
            if len(state_stack) == 0:
                lastObject = data
                print("Ending" + str(type(data)))
            else:
                cur_struct = state_stack[-1]
                add_data(cur_struct, data)
                print("Ending" + str(type(cur_struct)))

        elif byte >= b'0' and byte <= b'9':
            cur_struct = state_stack[-1]
            data = parse_byte_string(f, byte)

            add_data(cur_struct, data)

            print("Got byte string: " + str(data))

        else:
            print("That's probably not right...")
        
        byte = f.read(1)

pp.pprint(lastObject)
