import datetime, dialogs, json, notification, os, re, speech, time, ui

task_types = {
    's' : ('schnell 🏃🏻‍♀️', 'arcade:Powerup_3'), 
    'n' : ('normal 🏃‍♀️', 'arcade:Powerup_1'),
    'l' : ('langsam 🚶🏻‍♀️', 'arcade:Powerup_2'),
    'p' : ('pause 🧘🏻‍♀️', 'arcade:Coin_1')
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

filename_pause_data = "noti_paused_data.json"

class PlannedNoti(object):
    
    @classmethod
    def init_and_schedule(cls, message, delay=None, sound_name=None, action_url=None):
        notification.schedule(message=message, delay=delay, sound_name=sound_name, action_url=action_url)
        return cls(notification.get_scheduled()[-1])
    
    def __init__(self, data):
        self.data = data
        
    @property
    def message(self):
        return self.data['message']
    @property
    def fire_date(self): 
        return self.data['fire_date']
    @property
    def sound_name(self):
        return self.data['sound_name'].split('.')[0] # cut filename-suffix
    @property
    def action_url(self):
        return self.data['action_url']
    @property
    def fire_date_readable(self):
        fire_date_conv = time.localtime(self.fire_date)
        return time.strftime("%H:%M:%S", fire_date_conv)    
    @property
    def time_remaining(self):
        t = datetime.datetime.fromtimestamp(self.fire_date)
        return t - datetime.datetime.now()
        
    def __str__(self):
        return '{}, {}: {}'.format(self.fire_date_readable, self.time_remaining, self.data)
    
    __repr__ = __str__
    
    
    
    @staticmethod
    def get_scheduled():
        result = []
        for scheduled_notification in notification.get_scheduled():
            result.append(PlannedNoti(scheduled_notification))
        return result

    @staticmethod
    def get_benachrichtigungen_status():
        noti_status = ''
        for noti in PlannedNoti.get_scheduled():
            noti_status += '\n{}: {}'.format(noti.fire_date_readable, noti.message)
        return noti_status
        
    @staticmethod
    def pause():
        carbonized = []
        for noti in PlannedNoti.get_scheduled():
            delay_in_sec = round(noti.time_remaining.total_seconds())
            if delay_in_sec < 1: delay_in_sec = 1
            carbonized.append({'message':noti.message, 'delay':delay_in_sec, 'sound_name':noti.sound_name, 'action_url':noti.action_url})
        with open(filename_pause_data, "w") as write_file:
            write_file.write(json.dumps(carbonized, indent=4))
        notification.cancel_all()
            
    @staticmethod
    def load_paused_data():
        with open(filename_pause_data) as data_file:
            data = json.load(data_file)
        for carbonized_noti in data:
            PlannedNoti.init_and_schedule(message=carbonized_noti['message'], delay=carbonized_noti['delay'], sound_name=carbonized_noti['sound_name'], action_url=carbonized_noti['action_url'])
        os.remove(filename_pause_data)
        
    @staticmethod
    def check_if_pause_data_is_available():
        return os.path.exists(filename_pause_data)
        
    @staticmethod
    def remove_pause_data():
        if os.path.exists(filename_pause_data):
            os.remove(filename_pause_data)

letztes_delay = 0

def stell_benachrichtigung_ein(typ, dauer, delay_in_minuten):
    global letztes_delay
    letztes_delay = letztes_delay + delay_in_minuten * 60
    nachricht = '{} ({} min)'.format(typ[0], dauer)
    PlannedNoti.init_and_schedule(nachricht, delay=letztes_delay, sound_name=typ[1])
        
def get_startchoice_text():
    status = PlannedNoti.get_benachrichtigungen_status().splitlines()
    if not status: # keine Notis terminiert
        return 'Keine Session aktiv'
    
    td = PlannedNoti.get_scheduled()[0].time_remaining
    td_str = str(td).split('.')[0] # cut milliseconds
    text = 'Restdauer aktueller Task: {}'.format(td_str)
    
    for line in status:
        text += '\n' + line
    return text

def get_siri_status(quiet_if_not_active=False):
    ''' This is prepared for Siri Shortcuts which will be available with the next version of Pythonista'''
    notis = PlannedNoti.get_scheduled()
    if not notis and quiet_if_not_active:
        return None
    elif not notis:
        return 'Kein Intervalltraining aktiv.'
    
    text = 'Noch {} Minuten. '.format(round(notis[0].time_remaining.total_seconds() / 60))
    
    m = re.match(r"(\w+?) .+\((\d+) min\)", notis[0].message)
    if m:
        text += 'Dann {} für {} Minuten.'.format(m[1], m[2])
    return text

def close(sender):
    '''UI: Schließen'''
    sender.superview.close()

def cancel(sender):
    '''UI: Benachrichtigungen entfernen'''
    notification.cancel_all()
    dialogs.alert(title='Benachrichtigungen entfernt', button1='Okay', hide_cancel_button=True)
    sender.superview.close()
    
def start(sender):
    '''UI: Start/Restart'''
    notification.cancel_all() # Erstmal aufräumen
    PlannedNoti.remove_pause_data()
    
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
    PlannedNoti.init_and_schedule('Geschafft! 🥳', delay=letztes_delay, sound_name='arcade:Coin_3')
    
    print(PlannedNoti.get_benachrichtigungen_status())
    sender.superview.close()
    
def pause_or_continue(sender):
    '''UI: Pause/Weiter'''
    if PlannedNoti.check_if_pause_data_is_available():
       PlannedNoti.load_paused_data()
       dialogs.alert(title='Zwischenstand geladen\nWeiter gehts!', button1='Okay', hide_cancel_button=True)
       print(get_startchoice_text())
    else:
        PlannedNoti.pause()
        dialogs.alert(title='Zwischenstand gesichert', button1='Okay', hide_cancel_button=True)
    sender.superview.close()

def main():
    siri_status = get_siri_status(quiet_if_not_active=True)
    if siri_status: speech.say(siri_status, 'de-DE')
    
    active_session_available = len(PlannedNoti.get_scheduled())>0
    view = ui.load_view(pyui_path='Noti3.pyui')
    view['status'].text = get_startchoice_text()
    view['pauseButton'].enabled = PlannedNoti.check_if_pause_data_is_available() or active_session_available
    view['cancelButton'].enabled = active_session_available
    view.present(style='full_screen', title_bar_color='#af3a8a', title_color='#ffffff', orientations=['portrait'], hide_close_button=True)

def test():
    for i in range(1,3):
        PlannedNoti.init_and_schedule(message='Hello {}'.format(i), delay=i*60)
    noti = PlannedNoti.get_scheduled()[0]
    print(noti)
    notification.cancel_all()

if __name__ == '__main__':
    main()