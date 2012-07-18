#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

def readSMSdb(dbfile):
    import sqlite3
    sms = []
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute('SELECT address, date, text, flags FROM message where flags in (2,3)')
    for sms_addr, sms_date, sms_body, sms_flag in c.fetchall():
        if sms_addr: sms_addr = sms_addr.encode('utf8')
        if sms_body:
            sms_body = sms_body.encode('utf8')
        else:
            sms_body = ""
        sms.append((sms_addr, sms_date, sms_body, sms_flag))
    return sms

def output2File(data, output_file):
    f = open(output_file,'w')
    f.write("""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <?xml-stylesheet type="text/xsl" href="sms.xsl"?>
    <smses count="%s">""" % len(data))
    for addr, date, body, flag in data:
        if flag == 3: flag = 1
        if flag not in (3,2): flag = 1
        f.write("""<sms protocol="0" address="%s" date="%d000" type="%s" subject="null" body="%s" toa="null" sc_toa="null" service_center="null" read="1" status="-1" locked="0" readable_date="" contact_name="(Unknown)" />\n""" % (addr, date,flag,body))
    f.write("</smses>\n")
    f.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert SMS from iPhone backup to Android SMS Backup")
    parser.add_argument('--smsdb',dest = "smsdb", help = "Path of SMS sqlite file.", required=True)
    parser.add_argument('--output',dest = "output", help = "filename of output", required=True)
    args =  parser.parse_args()
    d = readSMSdb(args.smsdb)
    output2File(d,args.output)

