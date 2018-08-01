import os
import sys
import re
import urllib3
import smtplib as smtp
import datetime as date
import time

## haproxy stats
HAPROXY_STATS_URL = '/haproxy'
HAPROXY_PORT = 80
HAPROXY_IP = '192.168.1.1'
HAPROXY_AUTH = 'ON'
HAPROXY_USER = 'admin'
HAPROXY_PASS = 'password'

## Connect
MAIL_smtp = '172.21.34.80'
MAIL_port = 25

### Auth
MAIL_user = 'user'
Mail_pass = 'password'

### Send info
MAIL_from = 'haproxy@example.ro'
MAIL_to = 'status@example.ro'
MAIL_Subject = 'Servers Status'

## the Server group
SRV_group = 'WEB-Servers'


def timestamp():
    return date.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def SendMailSMTP(smtp_ip=None, port=25, user=None, password=None, mail_from=None, mail_to=None, mail_message=None, debug=0):
    if (smtp_ip is not None):
        ConnectSMTP = smtp.SMTP(smtp_ip, port)
        ConnectSMTP.set_debuglevel(debug)
        if (password is not None):
            ConnectSMTP.login(user, password)
        ConnectSMTP.sendmail(mail_from, mail_to, mail_message)
        ConnectSMTP.quit()

def CheckHaproxy(group_name):
    http = urllib3.PoolManager()
    headers = urllib3.util.make_headers(basic_auth='{0}:{1}'.format(HAPROXY_USER, HAPROXY_PASS))
    url = 'http://{0}:{1}{2};csv'.format(HAPROXY_IP,HAPROXY_PORT,HAPROXY_STATS_URL)

    if((HAPROXY_AUTH == 'on') or (HAPROXY_AUTH == 'ON')):
        r = http.request('GET', url, headers=headers)
    else:
        r = http.request('GET', url)

    if(r.status == 200):
        lines = re.split('\n+', r.data.decode('UTF-8'))
        head = re.split(',', lines[0])
        out = {}
        for i in range(1, (len(lines) - 1)):
            m = re.split(',',lines[i])
            if(m[0] == group_name):
                out[m[1]] = {}
                for x in range(2, (len(m) - 1)):
                    cont = m[x]
                    if(cont == ''):
                        cont = '0'
                    out[m[1]][head[x]] = cont
        return out
    else:
        return 'haproxy http error:{}'.format(r.status)

def SecToDaysTime(seconds):
    days = (seconds / (60 * 60 * 24))
    daysR = (seconds % (60 * 60 * 24))
    hours = (daysR / (60 * 60))
    HoursR = (daysR % (60 * 60))
    min = (HoursR / 60)
    return days, hours, min

def main( Server_Group, Subject ):
    mark = 0
    while(True):

        time.sleep(1)

        rez = CheckHaproxy(Server_Group)
        tableF = ''
        W = 'None'
        color = '#00FF00'
        status = 'OK'
        status_color = '#00FF00'

        for i in rez:
            if((i == 'BACKEND') and (rez[i]['status'] != 'UP')):
                W = 'CRITICAL !!!'
                status = 'CRITICAL !!!'
                color = '#f20d0d'
                status_color = '#f20d0d'
            elif((i != 'BACKEND') and (rez[i]['status'] != 'UP')):
                W = 'WARNING !!!'
                if(status != 'CRITICAL !!!'):
                    status = W
                    status_color = '#ffbf00'
                color = '#ffbf00'
            elif((rez[i]['status'] == 'UP')):
                W = 'OK'
                color = '#00FF00'

            days, hours, min = SecToDaysTime(int(rez[i]['downtime']))

            tableF += """<tr>
<th align="center" colspan="3"><b>{0}</b></th>
</tr>
<tr align="center">
<th><b>Status</b></th>
<th><b>DownTime</b></th>
<th><b>TimeStamp</b></th>
</tr>
<tr align="center">
<td bgcolor="{3}">{1}</td>
<td>{4}d{5}h{6}m</td>
<td>{2}</td>
</tr>
    
""".format(i, rez[i]['status'], timestamp(), color, int(days), int(hours), int(min))

        MAIL_message = """From: {0}
To: {1}
MIME-Version: 1.0
Content-type: text/html
Subject: {5} - {2}
<html>
<head>
</head>
<body>
<table border="1" align="center">
<tr>
<th align="center" colspan="3" bgcolor="{4}"><p><b>{2}</b></p></th>
</tr>
{3}
</table>
</body>
</html>
""".format(MAIL_from, MAIL_to, status, tableF, status_color, Subject)
        if(status == 'CRITICAL !!!') and (mark == 0):
            SendMailSMTP(smtp_ip=MAIL_smtp, port=MAIL_port, user=MAIL_user, password=Mail_pass, mail_from=MAIL_from,
                         mail_to=MAIL_to, mail_message=MAIL_message)
            mark = 1
        elif((status == 'WARNING !!!') and (mark == 0)):
            SendMailSMTP(smtp_ip=MAIL_smtp, port=MAIL_port, user=MAIL_user, password=Mail_pass, mail_from=MAIL_from,
                         mail_to=MAIL_to, mail_message=MAIL_message)
            mark = 2
        elif((status == 'OK') and (mark == 0)):
            SendMailSMTP(smtp_ip=MAIL_smtp, port=MAIL_port, user=MAIL_user, password=Mail_pass, mail_from=MAIL_from,
                         mail_to=MAIL_to, mail_message=MAIL_message)
            mark = 3
        elif(status == 'OK') and ((mark == 1) or (mark == 2)):
            mark = 0
        elif((status == 'WARNING !!!') and ((mark == 1) or (mark == 3))):
            mark = 0
        elif((status == 'CRITICAL !!!') and ((mark == 2) or (mark == 3))):
            mark = 0



try:
    main( SRV_group, MAIL_Subject )
except KeyboardInterrupt:
    print('stop')
    exit()