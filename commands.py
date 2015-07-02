# import this into lldb with a command like
# command script import bind.py
import lldb
import shlex
import optparse
import pdb
from string import ascii_lowercase
import re
import sys

varNum = 0

def freshVar():
    global varNum
    print('VarNum = ' + str(varNum))
    newVar = ascii_lowercase[varNum % 26] + str(varNum // 26)
    varNum += 1
    return newVar

#----------------------------------------bind command---------------------------------------------
def bind(debugger, command, result, dict):
    # Use the Shell Lexer to properly parse up command options just like a
    # shell would
    name = freshVar()
    print('$' + name + ' is now bound to ' + command)
    debugger.HandleCommand ('expression Value_t *** $' + name + ' = (Value_t***) ' + command)

#----------------------------------------Break label command---------------------------------------------
def breakLab(debugger, command, result, dict):
    args = shlex.split(command)

    if len(args) < 1:
        print('Not enough arguments, usage: breakLab <label> [<condition>]')

    interpreter = lldb.debugger.GetCommandInterpreter()
    interpreter.HandleCommand('image lookup --symbol ' + args[0], result)
    res = re.search('0x[0-9a-z]*', str(result))
    if res is None:
        print('Could not find address of label \"' + args[0] + '\"')
        return
    else:
        address = res.group(0)
    if len(args) == 2:
        print('breakpoint set --address ' + address + ' --condition \'' + args[1] + '\'')
        interpreter.HandleCommand('breakpoint set --address ' + address + ' --condition \'' + args[1] + '\'', result)
    else:
        print('b ' + address)
        interpreter.HandleCommand('b ' + address, result)

#watchpoint command add -s p 1 
#The first argument is the heap object to watch and the second is an offset into that heap object
def mantWatch(debugger, command, result, dict):
    args = shlex.split(command)

    interpreter = lldb.debugger.GetCommandInterpreter()
    print("Setting watchpoint on " + args[0] + " + " + args[1] + "")


    interpreter.HandleCommand('command script add -f %s.updateWatchpoints updateWatchpoints' % __name__, result)
    print('command script add -f %s.updateWatchpoints updateWatchpoints' % __name__)
    print('---------')
    print(result)
    print('---------')

#examine a location in memory
def examine(debugger, command, result, dict):
    args = shlex.split(command)

    if len(args) != 2:
        print('incorrect number of arguments\nusage: examine <address> <number of bytes>')
        return

    interpreter = lldb.debugger.GetCommandInterpreter()
    interpreter.HandleCommand('x -s8 -fx -c' + args[1] + ' ' + args[0], result)

def restart(debugg, command, result, dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    print('rerunning \"' + command + '\"')
    interpreter.HandleCommand('kill', result)
    interpreter.HandleCommand('run ' + command, result)

def untilError(debugger, command, result, dict):
    interpreter = lldb.debugger.GetCommandInterpreter()
    interpreter.HandleCommand('breakpoint list', result)
    if re.search('name = \'exit\'', str(result)) is None:
        interpreter.HandleCommand('b exit', result)
    interpreter.HandleCommand('breakpoint list', result)
    breakpoints = re.findall("[0-9]+: name = \'.*\'", str(result))
    breakNum = None
    for b in breakpoints:
        if re.search("\'exit\'", b) is not None:
            breakNum = re.search("[0-9]+", b).group(0);
    if breakNum is None:
        print('Could not find exit breakpoint!')
        return

    print('breakpoint com add -o \"restart ' + command + '\" ' + breakNum)
    interpreter.HandleCommand('breakpoint com add -o \"restart ' + command + '\" ' + breakNum, result)

    interpreter.HandleCommand(command, result)

def toFile(debugger, command, result, dict):
  #Change the output file to a path/name of your choice
    f=open("/Users/ml9951/temp.txt","w")
    debugger.SetOutputFileHandle(f,True);
    try:
        debugger.HandleCommand(command)  
        print('Done with command')
    except:
        print("inside exception handler!")
        f.close()
        debugger.SetOutputFileHandle(sys.stdout, True)
    f.close()
    debugger.SetOutputFileHandle(sys.stdout, True)


#
# code that runs when this script is imported into LLDB
#
def __lldb_init_module (debugger, dict):
    # This initializer is being run from LLDB in the embedded command interpreter
    # Make the options so we can generate the help text for the new LLDB
    # command line command prior to registering it with LLDB below

    # Add any commands contained in this module to LLDB
    debugger.HandleCommand('command script add -f %s.bind bind' % __name__)
    debugger.HandleCommand('command script add -f %s.breakLab breakLab' % __name__)
    debugger.HandleCommand('command script add -f %s.mantWatch mantWatch' % __name__)
    debugger.HandleCommand('command script add -f %s.examine examine' % __name__)
    debugger.HandleCommand('command script add -f %s.restart restart' % __name__)
    debugger.HandleCommand('command script add -f %s.untilError untilError' %__name__)
    debugger.HandleCommand('command script add -f %s.toFile toFile' %__name__)






















