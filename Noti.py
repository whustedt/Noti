import datetime, dialogs, notification, re, speech, time

task_types = {
    's' : ('schnell 🏃🏻‍♀️', 'Media/Sounds/arcade/Powerup_3'), 
    'n' : ('normal 🏃‍♀️', 'Media/Sounds/arcade/Powerup_1'),
    'l' : ('langsam 🚶🏻‍♀️', 'Media/Sounds/arcade/Powerup_2')
    }

programmes = {
    'Simple Test' : [
        ('s',0.1),
        ('n',0.5)
    ],
    '1h' : [
        ('n',12),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('s',3),
        ('l',1.5),
        ('n',12)
    ],
    'Tag 48 Lauftask' : [
        ('n',10),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('s',3), ('l',1),
        ('n',10)
    ],
    '62min' : [
        ('n',15),('s',4),('l',3),('s',4),('l',3),('s',4),('l',3),('s',4),('l',3),('s',4),('n',15)
    ],
    '182min' : [
        ('l',2.5),('n',64),
        ('l',1.5),('s',3),('l',1.5),
        ('s',6),('l',2),
        ('s',9),('l',4),
        ('s',6),('l',2),
        ('s',3),('l',1.5),
        ('s',3),('l',1.5),
        ('s',6),('l',2),('s',9),('l',4),
        ('s',6),('l',2),
        ('s',3),('l',1.5),('n',55),
        ('s',3),('l',1.5),
        ('s',6),('l',2),('s',9),('l',4),
        ('s',6),('l',2),('s',3),
        ('l',1.5),('n',45)
    ],
    '57 min' : [('l',10),('s',32),('l',15)]
    }

letztes_delay = 0

def stell_benachrichtigung_ein(typ, dauer, delay_in_minuten):
    global letztes_delay
    letztes_delay = letztes_delay + delay_in_minuten * 60
    nachricht = '{} ({} min)'.format(typ[0], dauer)
    notification.schedule(nachricht, delay=letztes_delay, sound_name=typ[1])
    
def get_benachrichtigungen_status():
    noti_status = ''
    for benachrichtigung in notification.get_scheduled():
        zeitpunkt = time.localtime(benachrichtigung['fire_date'])
        zeitpunkt_str = time.strftime("%H:%M:%S", zeitpunkt)
        noti_status += '\n{}: {}'.format(zeitpunkt_str, benachrichtigung['message'])
    return noti_status
        
def get_startchoice_text():
    status = get_benachrichtigungen_status().splitlines()
    if not status: # keine Notis terminiert
        return 'Was tun?'
    
    t = datetime.datetime.fromtimestamp(notification.get_scheduled()[0]['fire_date'])
    td = t - datetime.datetime.now()
    td_str = str(td).split('.')[0] # cut milliseconds
    text = 'Restdauer aktueller Task: {}'.format(td_str)
    
    for i in range(min(15, len(status))):
        text += '\n' + status[i]
    return text

def get_siri_status(quiet_if_not_active=False):
    ''' This is prepared for Siri Shortcuts which will be available with the next version of Pythonista'''
    notis = notification.get_scheduled()
    if not notis and quiet_if_not_active:
        return None
    elif not notis:
        return 'Kein Intervalltraining aktiv.'
    
    t = datetime.datetime.fromtimestamp(notis[0]['fire_date'])
    td = t - datetime.datetime.now()
    text = 'Noch {} Minuten. '.format(round(td.total_seconds() / 60))
    
    m = re.match(r"(\w+?) .+\((\d+) min\)", notis[0]['message'])
    if m:
        text += 'Dann {} für {} Minuten.'.format(m[1], m[2])
    return text

def main():
    siri_status = get_siri_status(quiet_if_not_active=True)
    if siri_status: speech.say(siri_status, 'de-DE')
    
    start_choice = dialogs.alert(title='Intervall-Benachrichtigungen', 
        message=get_startchoice_text(), 
        button1='Start/Restart', 
        button2='Benachrichtigungen entfernen',
        button3='Schließen',
        hide_cancel_button=True)
    
    if start_choice == 1: # Start/Restart
        notification.cancel_all() # Erstmal aufräumen
    
        delay = 0.1
        programm_id = dialogs.list_dialog(title='Programm?', items=list(programmes.keys()))
        print(programm_id)
        summe_der_einzelzeiten = round(sum(tupel[1] for tupel in programmes[programm_id]), 2)
        print('Dauer insg.: {} Minuten'.format(summe_der_einzelzeiten))
        for (typ, dauer) in programmes[programm_id]:
            stell_benachrichtigung_ein(typ=task_types[typ], dauer=dauer, delay_in_minuten=delay)
            delay = dauer
            
        # Schlussbenachrichtigung einstellen:
        global letztes_delay   
        letztes_delay = letztes_delay + delay * 60
        notification.schedule('Geschafft! 🥳', delay=letztes_delay, sound_name='Media/Sounds/arcade/Coin_3')
        
        print(get_benachrichtigungen_status())
    
    elif start_choice == 2: # Benachrichtigungen entfernen
        notification.cancel_all()
        dialogs.alert(title='Benachrichtigungen entfernt', button1='Okay', hide_cancel_button=True)
        
if __name__ == '__main__':
	main()
