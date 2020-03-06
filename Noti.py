import datetime, dialogs, notification, re, speech, time

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
    
letztes_delay = 0

def stell_benachrichtigung_ein(typ, dauer, delay_in_minuten):
    global letztes_delay
    letztes_delay = letztes_delay + delay_in_minuten * 60
    nachricht = '{} ({} min)'.format(typ[0], dauer)
    notification.schedule(nachricht, delay=letztes_delay, sound_name=typ[1])
    

def main():
    start_choice = dialogs.alert(title='Intervall-Benachrichtigungen', 
        message='Was tun?', 
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
        notification.schedule('Geschafft! 🥳', delay=letztes_delay, sound_name='arcade:Coin_3')
        
        print('Benachrichtigungen erstellt')
    
    elif start_choice == 2: # Benachrichtigungen entfernen
        notification.cancel_all()
        dialogs.alert(title='Benachrichtigungen entfernt', button1='Okay', hide_cancel_button=True)
        
if __name__ == '__main__':
	main()
