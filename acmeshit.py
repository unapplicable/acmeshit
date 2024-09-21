#!/usr/bin/env python3

import sys, os
import pwd, grp
from time import sleep
from dnslib import DNSLabel, QTYPE, RR, dns
from dnslib.server import DNSServer

VERBOSE=True

def records(name):
    try:
      ff = open(name)
    except IOError:
      sys.stderr.write("File {} not found\n".format(name))
      sys.exit(1)

    with ff as f:
        return sorted({line.strip() for line in f.readlines()})

class Resolver(object):
  def __init__(self, records_file):
      self._records_file = records_file

  def resolve(self, request, handler):
    sys.stderr.write(repr(request))
    reply = request.reply()
    zone = '\n'.join(
        '{} 1 TXT "{}"'.format(
            request.q.qname,
            txt.strip(),
        )
        for txt in records(self._records_file)
    )
    if VERBOSE:
        sys.stderr.write(repr(zone) + '\n')
    reply.add_answer(
        *RR.fromZone(
            zone
        )
    )
    return reply

def drop_privileges(user):
    runningUid = pwd.getpwnam(user).pw_uid
    runningGid = grp.getgrnam(user).gr_gid

    os.setgroups([])

    os.setgid(runningGid)
    os.setuid(runningUid)

if __name__ == '__main__':
  if len(sys.argv) != 4:
      sys.stderr.write("Usage: {} <user> <address <file_with_txt_records>\n".format(sys.argv[0]))
      sys.exit(1)

  user = sys.argv[1]
  records_file = os.path.abspath(sys.argv[3])
  os.chdir('/')
  records(records_file)
  resolver = Resolver(records_file)
  server = DNSServer(resolver, address=sys.argv[2], port=53)

drop_privileges(user)
records(records_file)
server.start_thread()

while True:
  sleep(1000)
