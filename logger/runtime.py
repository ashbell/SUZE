from timeit import timeit
import re

def find(string, text):
    if string.find(text) > -1:
        pass

def re_find(string, text):
    if re.match(text, string):
        pass

def best_find(string, text):
    if text in string:
       pass

print timeit("find(string, text)", "from __main__ import find; string='lookforme'; text='look'")  
print timeit("re_find(string, text)", "from __main__ import re_find; string='lookforme'; text='look'")  
print timeit("best_find(string, text)", "from __main__ import best_find; string='lookforme'; text='look'")
