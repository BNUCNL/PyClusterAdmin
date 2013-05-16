# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

import os
import re
import paramiko

def ssh2mount(ip, username, passwd, src_path, targ_dir):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, passwd, timeout=5)
        print 'connect to the host ' + ip + '......'
        # if target directory does not exist...
        stdin, stdout, stderr = ssh.exec_command('test -e ' + \
                targ_dir + ' && echo "exist" || echo "not exist"')
        dir_status = stdout.readlines()
        dir_status = dir_status[0].strip()
        if dir_status == 'not exist':
            print targ_dir + ' does not exist, create it automatically.'
            cmd = ' '.join(['mkdir', targ_dir])
            stdin, stdout, stderr = ssh.exec_command(cmd)
            err_status, err = print_ssh_log(stdout, stderr)
            if err_status == 'error':
                ssh.close()
                return
        # mount filesystem
        cmd = ' '.join(['mount', src_path, targ_dir])
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err_status, err = print_ssh_log(stdout, stderr)
        if err_status == 'normal':
            print ip + ': mount filesystem ' + src_path + '... OK'
            ssh.close()
    except:
        raise
        ssh.close()

def ssh2umount(ip, username, passwd, targ_dir):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, passwd, timeout=5)
        print 'connect to the host ' + ip + '......'
        # if target directory does not exist...
        stdin, stdout, stderr = ssh.exec_command('test -e ' + \
                targ_dir + ' && echo "exist" || echo "not exist"')
        dir_status = stdout.readlines()
        dir_status = dir_status[0].strip()
        if dir_status == 'not exist':
            print targ_dir + ' does not exist.'
            ssh.close()
            return
        # umount filesystem
        cmd = ' '.join(['umount', targ_dir])
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err_status, err = print_ssh_log(stdout, stderr)
        if err_status == 'error':
            x = err[0].strip()
            if x == ' '.join(['umount:', targ_dir + ':', 'device is busy']):
                print 'Kill all process on device...'
                tmp_cmd = 'fuser -km ' + targ_dir
                stdin, stdout, stderr = ssh.exec_command(tmp_cmd)
                print_ssh_log(stdout, stderr)
                stdin, stdout, stderr = ssh.exec_command(cmd)
                err_status, err = print_ssh_log(stdout, stderr)
                if err_status == 'normal':
                    print ip + ': umount filesystem ' + targ_dir + '... OK'
        else:
            print ip + ': umount filesystem ' + targ_dir + '... OK'
        ssh.close()
    except:
        raise
        ssh.close()

def ssh2poweroff(ip, username, passwd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, passwd, timeout=5)
        print 'connect to the host ' + ip + '......'
        print 'send signal to shut down...'
        stdin, stdout, stderr = ssh.exec_command('poweroff')
        ssh.close()
    except:
        raise
        ssh.close()

def ssh2service(ip, username, passwd, service_name, service_status):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, passwd, timeout=5)
        print 'connect to the host ' + ip + '......'
        print service_status + ' service ' + service_name
        cmdstr = ' '.join(['service', service_name, service_status])
        stdin, stdout, stderr = ssh.exec_command(cmdstr)
        print_ssh_log(stdout, stderr)
        ssh.close()
    except:
        raise
        ssh.close()

def read_nfstab(nfstab_file):
    try:
        info = open(nfstab_file).readlines()
        info = [line.strip() for line in info]
        info = [line.split() for line in info 
                if not re.match(r'#', line) and line]
        tab = {}
        for item in info:
            tab[item[0]] = [item[1], item[2]]
        return tab
    except:
        print "Can not read file " + nfstab_file
        raise

def read_nfs_config(nfs_config_file):
    try:
        info = open(nfs_config_file).readlines()
        info = [line.strip() for line in info]
        info = [line.split(':') for line in info
                if not re.match(r'#', line) and line]
        info = dict(info)
        for host in info:
            temp = info[host].split(',')
            info[host] = [item.strip() for item in temp]
        return info
    except:
        print "Can not read file " + nfstab_file
        raise

def read_hoststab(hoststab_file):
    try:
        info = open(hoststab_file).readlines()
        info = [line.strip() for line in info]
        info = [line.split() for line in info
                if not re.match(r'#', line) and line]
        info = dict(info)
        return info
    except:
        print "Can not read file " + hoststab_file
        raise

def ssh2killall(ip, username, passwd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, 22, username, passwd, timeout=5)
        print 'connect to the host ' + ip + '......'
        stdin, stdout, stderr = ssh.exec_command('who')
        out = stdout.readlines()
        if len(out):
            out = [line.strip().split()[0] for line in out]
            user_list = []
            for usr in out:
                if not usr in user_list:
                    user_list.append(usr)
            for usr in user_list:
                print 'Kill all processes of user ' + usr
                stdin, stdout, stderr = ssh.exec_command('killall -u ' + usr)
                info = stdout.readlines()
                for item in info:
                    print item
        else:
            print 'No users on host ' + ip
        ssh.close()
    except:
        raise
    ssh.close()

def print_ssh_log(stdout, stderr):
    out = stdout.readlines()
    err = stderr.readlines()
    if len(out):
        print 'SSH_OUTPUT_STRING:'
        for item in out:
            print item
    if len(err):
        print 'SSH_ERROR_STRING:'
        for item in err:
            print item
        return 'error', err
    else:
        return 'normal', err

