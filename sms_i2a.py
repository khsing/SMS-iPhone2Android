#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

def checkVersion(c):
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [i[0] for i in tables.fetchall()]
    if 'chat_message_join' in tables:
        return 'ios6'
    else:
        return 'ios5'

def readSMSdb(dbfile):
    import sqlite3
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    ver = checkVersion(c)
    if ver == 'ios5':
        return readiOS5SMSdb(c)
    elif ver == 'ios6':
        return readiOS6SMSdb(c)

def readiOS6SMSdb(c):
    sms = []
    c.execute("select chat.chat_identifier, account_login, message.date, message.is_from_me, text from chat join chat_message_join as cm on cm.chat_id = chat.ROWID join message on cm.message_id = message.ROWID where chat.service_name ='SMS';")
    for ident, acct, sms_date, is_from_me, sms_body in c.fetchall():
        if ident: ident = ident.encode('utf8')
        if acct: acct = acct.encode('utf8').split(':')[1]
        if sms_body: 
            sms_body = sms_body.encode('utf8')
        else:
            sms_body = ""
        if is_from_me == 1:
            sms_addr = acct
            sms_flag = 2
        else:
            sms_addr = ident
            sms_flag = 1
        sms.append((sms_addr, sms_date, sms_body, sms_flag))
    return sms

def readiOS5SMSdb(c):
    sms = []
    c.execute('SELECT address, date, text, flags FROM message where flags in (2,3)')
    for sms_addr, sms_date, sms_body, sms_flag in c.fetchall():
        if sms_addr: sms_addr = sms_addr.encode('utf8')
        if sms_body:
            sms_body = sms_body.encode('utf8')
        else:
            sms_body = ""
        if sms_flag == 3:
            sms_flag = 2
        elif sms_flag == 2:
            sms_flag = 1
        else:
            sms_flag = 1
        sms.append((sms_addr, sms_date, sms_body, sms_flag))
    return sms

def output2File(data, output_file):
    f = open(output_file,'w')
    f.write("""<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <?xml-stylesheet type="text/xsl" href="sms.xsl"?>
    <smses count="%s">""" % len(data))
    for addr, date, body, flag in data:
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

