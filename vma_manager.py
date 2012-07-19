#!/usr/bin/python
#-*- coding: utf-8 -*-
import json
import os
import subprocess

import urllib2
import sys

global config
config={}

START = 'start'
STOP = 'stop'

def print_header():
    print config['COLUMN_FORMAT'].format('host', 'port', 'java version', 'OS', 'selenium version')


def get_status(hosts):
    """
        try to make http request to selenium server
    """
    print_header()

    def get_url(host, port):
        return "http://{0}{1}:{2}/wd/hub/status".format(host, config['DOMAIN'], port)

    for host in hosts:
        response = None
        port = config['NODE_PORT']
        url1 = get_url(host, port)
        try:
            response = urllib2.urlopen(urllib2.Request(url1))
        except urllib2.URLError as e:
            pass
        if response is None:
            port = config['ALONE_PORT']
            url2 = get_url(host, port)
            try:
                response = urllib2.urlopen(urllib2.Request(url2))
            except urllib2.URLError as e:
                print "{0} {1}".format(host, e.reason)
        if response is None:
            continue
        response_json = json.loads(response.read().split('\x00')[0])

        print config['COLUMN_FORMAT'].format(host, port, response_json['value']['java']['version'],
                                             response_json['value']['os']['name'],
                                             response_json['value']['build']['version'])


def stopstart_service(host, action):
    """
       start or stop selenium service via ssh
       avalaible actions 'stop' 'start'
       """
    fnull = open(os.devnull, 'w')
    p = subprocess.Popen(["ssh", "{0}@{1}{2}".format(config['LOGIN'], host, config['DOMAIN']), "net {0} selenium".format(action)], stderr=fnull)
    p.communicate()
    if p.returncode == 0:
        print "success {0} {1}".format(action, host)
    else:
        print "fail {0} {1}".format(action, host)
    fnull.close()

def restart_service(hosts):
    for host in hosts:
        stopstart_service(host,STOP)
        stopstart_service(host,START)


def start_service(hosts):
    for host in hosts:
        stopstart_service(host, START)

def stop_service(hosts):
    for host in hosts:
        stopstart_service(host, STOP)


def deploy_new_version(hosts):
    for host in hosts:
        stopstart_service(host,STOP)
        p = subprocess.Popen(["scp", config['LOCAL_ARTIFACT'], "{0}@{1}{2}:{3}".format(config['LOGIN'], host, config['DOMAIN'], config['REMOTE_PATH'])])
        p.communicate()
        stopstart_service(host,START)


def download_new_version(version):
    """
    version is list not string
    """
    wget = subprocess.Popen(["wget", config['SELENIUM_URL'].format(version[0]), "-O", config['LOCAL_ARTIFACT']])
    wget.communicate()
    if wget.returncode != 0:
        print "Could not fetch new version {0}. wget return code {1}".format(version, wget.returncode)
    else:
        get_local_version()


def change_selenium_role(hosts, regkey):
    """
        change selenium server role by using windows regestry keys in bat files
        exec through ssh regkey_alone.bat or regkey_node.bat
       """
    for host in hosts:
        print host
        stopstart_service(host, STOP)
        fnull = open(os.devnull, 'w')
        p = subprocess.Popen(["ssh", "{0}@{1}{2}".format(config['LOGIN'], host, config['DOMAIN']), regkey], stderr=fnull)
        p.communicate()
        if p.returncode == 0:
            print "success change {0} role".format(host)
        else:
            print "fail change {0} role".format(host)
        fnull.close()
        stopstart_service(host, START)

def make_alone(host):
    change_selenium_role(host,config['REGKEY_ALONE'])

def make_grid_node(host):
    change_selenium_role(host,config['REGKEY_NODE'])

def get_local_version():
    """
    fetch version from selenium jar in LOCAL_ARTIFACT directory
    """
    unzip = subprocess.Popen(["unzip", "-c", config['LOCAL_ARTIFACT'], "*MANIFEST.MF"], stdout=subprocess.PIPE)
    grep = subprocess.Popen(["grep", "Selenium-Version"], stdin=unzip.stdout, stdout=subprocess.PIPE)
    unzip.stdout.close()
    output = grep.communicate()[0]
    print output

def print_help():
    print "Usage: vma_manager.py command [arg]"
    print "Available commands:"
    print "list <all|host1 host2 ...> show status of all hosts in pool or of specified hosts"
    print "stop, start, restart  <all|host>"
    print "download <version> download selenium jar archive to local directory"
    print "deploy <all|host1 host2 ...> deploy new selenium version from local directory to all host or specified hosts"
    print "alone <all|host1 host2 ...> run selenium on host as standalone server on port 4444"
    print "node <all|host1 host2 ...> run selenium on host as grid node on port 5555"
    print "getv show version of saved selenium jar archive"
    print "help show this message end exit"

handlers = {
    "list": get_status,
    "stop": stop_service,
    "start": start_service,
    "restart":restart_service,
    "download":download_new_version,
    "deploy":deploy_new_version,
    "alone":make_alone,
    "node":make_grid_node,
    "getv":get_local_version,
    "help":print_help
}

def main(configfile='config.cfg'):
    if os.path.exists(configfile):
        execfile(configfile, config)
    else:
        execfile('config.cfg.ex',config)
    if len(sys.argv) > 1:
        action = sys.argv[1]
        try:
            if sys.argv[2:] == []:
                handlers[action]()
            elif sys.argv[2] == 'all':
                handlers[action](config['HOSTS'])
            else:
                handlers[action](sys.argv[2:])
        except Exception as e:
            print "ERROR", e
            print "Try exec with help option"
            exit()
    else:
        print_help()
        exit()

if __name__ == "__main__":
    main()