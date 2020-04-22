#!/usr/bin/env python3
""" 
Mission: Support C.R.U.D + S operations upon the EzLog.LOGFILE.
Project: Python 4000, Linux & DevOps (Udemy)
URL:     https://www.udemy.com/course/python-4000-gnu-devops
File:    ezlog.py
Version: 3.1 - Basic GUI invoked instead of help, as the new default.
"""

# Note: If you what to keep your log entries / messages in the same place,
# then change EzLog.LOGFILE to a hard-coded path + file location.

import os
import os.path
from datetime import datetime as zdatetime
from email import utils


from tkinter import *
class Prompter:
    def __init__(self):
        self._dict = None
        self._isOk = None
        self.last_row = None

    def _okay(self):
        self._isOk = True
        self.tk.quit()

    def _cancel(self):
        self._isOk = False
        self.tk.quit()

    @staticmethod
    def Begin(*fields, title="Input"):
        ''' Create the frame, add the title, as well as the input fields.'''
        from collections import OrderedDict
        self = Prompter()
        self.tk = Tk()

        self._dict = OrderedDict()

        if title:
            self.tk.title(title)

        self.last_row = 0
        # zFields (A Label, plus an Entry, in a grid layout)
        for ref in fields:
            obj = Label(master=self.tk, text=str(ref) + ": " )
            obj.grid(row=self.last_row, column=0)

            obj = Entry(master=self.tk, bd=5, width=72)
            obj.grid(row=self.last_row, sticky=W, column=1)

            if not self.last_row:
                obj.focus()

            self._dict[ref]=obj
            self.last_row += 1
        return self

    @staticmethod
    def End(prompter):
        ''' Add the closing buttons, center, and pack the Frame.'''
        if prompter.last_row is None:
            return False
        if isinstance(prompter, Prompter) is False:
            return False

        # zButtons (A Frame in the grid, plus the properly-centered pair of buttons)
        bottom = Frame(prompter.tk)
        bottom.grid(row=prompter.last_row, columnspan=2)
        btn = Button(bottom, text="Okay", command=prompter._okay)
        btn.pack(side=LEFT, pady=12)

        btn = Button(bottom, text="Cancel", command=prompter._cancel)
        btn.pack(side=RIGHT, padx=10)

        width = prompter.tk.winfo_screenwidth()
        height = prompter.tk.winfo_screenheight()
        x = int(width/2 - (prompter.tk.winfo_reqwidth()))
        y = int(height/2 - (prompter.tk.winfo_reqheight()))
        prompter.tk.geometry("+%d+%d" % (x, y))
        prompter.tk.geometry(f"+{x}+{y}")
        return True

    def show(self):
        from collections import OrderedDict
        self.tk.mainloop()
        try:
            results = OrderedDict()
            if self._isOk is not True:
                return results

            for ref in self._dict.keys():
                results[ref] = (self._dict[ref]).get()
            return results
        finally:
            try:
                self.tk.destroy()
            except:
                pass

    @staticmethod
    def Prompt(*fields, title="Input"):
        ''' Basic mission statement completed. '''
        self = Prompter.Begin(*fields, title=title)
        if Prompter.End(self) is False:
            raise Exception("AddButtons: Unexpected Error.")
        return self.show()


class EzLog():

    RunDone = None
    Which   = None
    LOGFILE = "./logger.log"

    def __init__(self, message = ''):
        self.LFORMAT = '%Y/%m/%d: %H.%M.%S (LOCAL)'
        self.UFORMAT = '%Y/%m/%d: %H.%M.%S [%z]'
        self._hack(message)

    def _hack(self, message):
        znow = zdatetime.now()
        znow = utils.localtime(znow)
        self.local_date = znow.strftime(format=self.LFORMAT)
        self.message = str(message)

    def __str__(self):
        return self.local_date + "\t" + self.message + "\n"

    def hack(self, message):
        """ Update the time, as well as the message """
        self._hack(message)

    def is_null(self):
        return len(self.message) == 0

    @staticmethod
    def Create(message):
        EzLog.RunDone = None
        entry = EzLog(message)
        with open(EzLog.LOGFILE, "a") as fp:
            if entry.is_null():
                entry.message = "This is a test"
            fp.write(str(entry))
        EzLog.RunDone = "Create"

    @staticmethod
    def List(message):
        try:
            nelem = int(message)
            if nelem < 1:
                print(f"Ignoring {nelem}...")
                return
            with open(EzLog.LOGFILE) as fh:
                for which in range(nelem):
                    line = fh.readline()
                    if not line:
                        break
                    else:
                        print(f"{which+1}.) {line.strip()}")
        except Exception as ex:
            raise ex
        EzLog.RunDone = "List"

    @staticmethod
    def Update(message):
        if EzLog.Which == None:
            EzLog.Which = int(message)
            return
        if EzLog.Which < 1:
            print(f"Ignoring {EzLog.Which}...")
            return
        temp = EzLog.LOGFILE + "~"
        with open(temp, 'w') as fout:
            with open(EzLog.LOGFILE) as fin:
                goal = EzLog.Which - 1
                try:
                    for which in range(EzLog.Which):
                        line = fin.readline()
                        if not line:
                            break; # eof!
                        if which != goal:
                            fout.write(line)
                    if which != goal:
                        raise Exception() # trigger, only
                    fout.write(str(EzLog(message)))
                    try:
                        fout.writelines(fin.readlines())
                    except Exception as ex:
                        pass
                except Exception as ex:
                    fout.close()
                    os.unlink(temp)
                    print(f"Ignored: No line #{EzLog.Which} in {EzLog.LOGFILE}.")
                    return
        os.unlink(EzLog.LOGFILE)
        os.rename(temp, EzLog.LOGFILE)
        EzLog.RunDone = "Update"

    @staticmethod
    def Delete(message):
        temp = EzLog.LOGFILE + "~"
        try:
            nelem = int(message)
            if nelem < 1:
                print(f"Ignoring {nelem}...")
                return
            goal = nelem - 1
            with open(temp, 'w') as fout:
                with open(EzLog.LOGFILE) as fin:
                    try:
                        for which in range(nelem):
                            line = fin.readline()
                            if not line:
                                break; # eof!
                            if which == goal:
                                print("Removing:", line, end='') #stripless
                            else:
                                fout.write(line)
                        if which != goal:
                            raise Exception() # entry not found.
                        fout.writelines(fin.readlines())
                    except Exception as ex:
                        print(f"No log entry #{nelem}.")
                        fout.close()
                        os.unlink(temp)
        except Exception as ex:
            raise ex
        finally:
            if os.path.exists(temp):
                os.unlink(EzLog.LOGFILE)
                os.rename(temp, EzLog.LOGFILE)
        EzLog.RunDone = "Delete"

    @staticmethod
    def Search(message):
        if not message:
            return
        print(f'Searching for "{message}" in {EzLog.LOGFILE} ...')
        with open(EzLog.LOGFILE) as fh:
            for ss, line in enumerate(fh, 1):
                if line.find(message) != -1:
                    print(f"{ss}.) {line}", end='')
        EzLog.RunDone = "Search"

    @staticmethod
    def Show():
        entry = EzLog()
        results = Prompter.Prompt("Message", title=entry.local_date)
        if len(results) is 0:
            print("Canceled - Not logged.")
        else:
            entry.message = results["Message"]
            with open(EzLog.LOGFILE, "a") as fp:
                fp.write(str(entry))
            print(entry)
        EzLog.RunDone = "Show"

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--create",
                        nargs=argparse.REMAINDER,
                        type=EzLog.Create,
                        help='log quoted "message"')
    parser.add_argument("-u", "--update",
                        nargs=argparse.REMAINDER,
                        type=EzLog.Update,
                        help='set list (-l) # to quoted "message"')
    parser.add_argument("-l", "--list",
                        nargs=1,
                        type=EzLog.List,
                        help="list recent messages")
    parser.add_argument("-d", "--delete",
                        nargs=1,
                        type=EzLog.Delete,
                        help='delete list (-l) entry #')
    parser.add_argument("-s", "--search",
                        type=EzLog.Search,
                        help="search log entries")
    parser.parse_args()
    if not EzLog.RunDone:
        EzLog.Show()
    else:
        print(f"EzLog: {EzLog.RunDone} Completed.")


