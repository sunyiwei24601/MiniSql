from struct import Struct
import struct
import json
f = open("tmp\sample.db", "wb")
record_nums = 5
relation_name = "sample"
current_number_of_pages = 2
first_free_page_num = 1
location_of_pages = {0:0, 1:4096}
information = {
    'record_nums': record_nums,
    'relation_name': relation_name,
    'current_number_of_pages': current_number_of_pages,
    #"first_free_page_num" : first_free_page_num,
    "location_of_pages": location_of_pages,
    # 'record_size': 15,
}

information_bytes = json.dumps(information).encode()

def extend_to_a_page(s, page_size=4096):
    if len(s) >= 4096:
        return s[:4096]
    else:
        return s + b" " * 10

information_bytes = extend_to_a_page(information_bytes)
f.write(information_bytes)


relations = [[0, 1, 'Sun'.encode(), 2.5],
             [1, 2, 'Yes'.encode(), 3.5],
             [2, 3, 'NOP'.encode(), 4.5],
             [3, 4, 'You'.encode(), 4.3],
             [4, 5, 'Tim'.encode(), 2.3]]
attributes_type = ['i', 'i', '4s', 'f']
struct_format = '>'+''.join(attributes_type)
structer = Struct(struct_format)
record_len = structer.size

page_records_nums = 5
page_num = 10




page = struct.pack(">ii", page_num, page_records_nums)
for relation in relations:
    page += structer.pack(*relation)
page = extend_to_a_page(page)
f.write(page)



f.close()

