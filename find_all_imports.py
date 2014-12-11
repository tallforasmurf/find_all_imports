'''
    $ find_all_imports.py target_script.py

Find all the imports used by target_script.py.

The target_script will be executed; the user must exercise
its features so as to trigger any dynamic imports it might do.
Then terminate it normally, for example File>Quit for a GUI
app, or ^d input to a command-line program.

'''

# sys and os will always appear in the output. If the target_script
# does not actually import them (unlikely) they could be removed
# from the output manually.

import sys
import os

# Define the target script

script_name = sys.argv[1]
script_basename = os.path.basename(script_name)

# Record the modules needed to get this script going to this point.

module_list_base = sys.modules.copy()

# Import the target script and record what it imported.
# This is the full import list, provided neither the script nor
# anything it calls, perform dynamic imports at run-time.

script_module = __import__(script_basename)

module_list_static_import = sys.modules.copy()

# Execute the target script to capture dynamic imports.
# Import what we need to perform the following steps.
# "marshal" is a built-in. We remove imp and importlib from
# the list later.

import imp
import importlib
import marshal

# Create a code object by un-marshalling the cached .pyc if any
cache_code = None
if hasattr(script_module,'__cached__') and script_module.__cached__ :
    bytecode_file = open(script_module.__cached__,'rb')
    magic = bytecode_file.read(4)
    if magic == imp.get_magic() :
        timestamp = bytecode_file.read(4)
        padding = bytecode_file.read(4)
        bytecode_blob = bytecode_file.read()
        cache_code = marshal.loads(bytecode_blob)
    bytecode_file.close()

if cache_code is None :
    # No .pyc, create code object via compiling source
    script_file = script_module.__file__
    source_file = open(script_file,'r',encoding='UTF-8')
    source_blob = source_file.read()
    source_file.close()
    cache_code = compile(source_blob,'<string>','exec')

# Now get rid of the sys.modules entries for things we imported
# to do that compile. If the executed app uses them, they will
# be reloaded and go back into the list.

del sys.modules['imp']
del sys.modules['importlib']
del sys.modules['importlib._bootstrap']
del sys.modules['importlib.machinery']

# Actually execute the code of the target script.
# The user should be sure to exercise all features that might
# lead to dynamic imports. Then quit the app normally.

exec(cache_code)

# Snapshot the total of imports after execution

module_list_dynamic_import = sys.modules.copy()

def dict_diff(da, db):
    '''
    Subtract one dict from another: da-db
    Return a dict containing only
    members of da that are not in db.
    '''
    ka = set(da.keys())
    kb = set(db.keys())
    return { k:da[k] for k in (ka - kb) }

def print_module_dict(da):
    '''
    Print the names and filepaths of modules in a dict
    similar to sys.modules.
    '''
    for k in sorted(da.keys()):
        f = '(builtin)'
        if hasattr(da[k], '__file__') :
            f = da[k].__file__
        print( k, f)

print('\n==== Essential base modules =====\n')
print_module_dict(module_list_base)
print('\n==== Static imports by script',script_name,'====\n')
print_module_dict( dict_diff(module_list_static_import,module_list_base) )
print('\n==== Modules added by executing script',script_name,'====\n')
print_module_dict( dict_diff(module_list_dynamic_import, module_list_static_import) )
