# Copyright 2019 David Zellhoefer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys


# add fields of interest to the following list, only this field will be extracted

# general overview of Pica + fields (in German) is available under https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/inhalt.shtml

# 028A  1. Verfasser (siehe https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/3000.pdf)
# 028B  2. Verfasser und weitere (siehe https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/3000.pdf)
# 021A  Hauptsachtitel (siehe https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/4000.pdf)
# 021B  Hauptsachtitel bei j-Sätzen (siehe https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/4004.pdf)
# 033A  Ort und Verlag (siehe https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/4030.pdf)
# 010@  Sprache (siehe https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/1500.pdf)
# 019@  Erscheinungsland (siehe https://www.gbv.de/bibliotheken/verbundbibliotheken/02Verbund/01Erschliessung/02Richtlinien/01KatRicht/1700.pdf)
fieldsOfInterest=['028A','028B','021A','021B','033A','010@','019@']

# choose you file to be processed here
with open("./analysis/test_large.pp", "rb") as f:
    byte = f.read(1)
    i = 0
    unicodeHot = False
    lastUnicodeMarker = None
    last = None
    fieldSeparator = False

    currentLine = ""
    # encoding is indicated in 001U as "0utf8"

    while byte != b"":
        # Do stuff with byte.

        byte = f.read(1)
        # debug (print all seen bytes)
        # print(str(byte)+"\t"+str(int.from_bytes(byte,sys.byteorder)))
        i += 1

        # if in unicode processing mode, compose 2 byte unicode character
        if unicodeHot:
            bytestream = last + lastUnicodeMarker + byte
            currentLine = currentLine[:-1] + bytestream.decode('utf-8', "replace")

        # if we find a \r\n, we have a new line
        if byte == b'\n' and last == b'\r':
            #print(currentLine)
            # split must be based on b'\x1f'
            currentLine = currentLine.replace("\x1e", "")
            #tokens = currentLine.replace('\x1f', "\t").split("\t")
            tokens = currentLine.split("\t")
            # remove whitespaces etc.
            tokens=list(map(str.strip, tokens))
            #TODO remove @ in certain sub-fields because it is used as a sorting indicator in PICA+
            #['028A', 'dPaul\x1faCelan\x1f9131811533\x1fdPaul\x1faCelan\x1fE1920\x1fF1970\x1f0gnd/118519859']

            if tokens[0] in fieldsOfInterest:
                subtokens=tokens[1].split('\x1f')
                print(tokens[0]+":\t"+str(subtokens))
            currentLine = ""

        # if we find a space followed by \xlf, we have found a field separator
        if byte == b'\x1f' and last == b' ':
            # currentLine = currentLine +"\t"
            byte = b'\t'

        # if we find a \n followed by \x1d, we have found a record separator
        if byte == b'\x1d' and last == b'\n':
            print("*NEW_RECORD*")

        # take care of 2 byte unicode characters, toggle unicode processing mode, see above
        if byte == b'\xcc':
            unicodeHot = True
            lastUnicodeMarker = byte
        else:
            if byte:
                last = byte
            else:
                last = b' '
            # ignore output for \r
            if not byte == b'\r':
                if not byte == b'\n':
                    if byte:
                        if not unicodeHot:
                            currentLine = currentLine + byte.decode('utf-8',
                                                                    "replace")  # see https://docs.python.org/3/howto/unicode.html#the-unicode-type
                        else:
                            unicodeHot = False
