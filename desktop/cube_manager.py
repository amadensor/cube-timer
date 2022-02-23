"""Cube manager"""
import PySimpleGUI as sg
import serial
import serial.tools.list_ports
#port_list=[]
ser=serial.Serial()

def get_ports():
    """Get the list of serial ports, include a blank if none"""
    print('get ports')
    port_ret=[]
    ports=serial.tools.list_ports.comports()
    for port in ports:
        port_ret.append(port.device)
    if len(port_ret)==0:
        port_ret.append("")
    return port_ret

normal_titles=[
    [sg.Text("normal")],
    [sg.Text("inspection time")],
    [sg.Text("alert 1")],
    [sg.Text("alert 2")],
    [sg.Text("alert 3 (DNF)")],
]
normal_inputs=[
    [sg.Text()],
    [sg.Input(key='normal_inspect',size=4)],
    [sg.Input(key='normal_1',size=4)],
    [sg.Input(key='normal_2',size=4)],
    [sg.Input(key='normal_dnf',size=4)]
]
normal_col=[
    [
        sg.Column(normal_titles),
        sg.Column(normal_inputs)
    ],
    [
        sg.Button("Setup Normal",key="norm_button")
    ]

]

blindfolded_titles=[
    [sg.Text("Blind")],
    [sg.Text("inspection time - 0")],
    [sg.Text("alert 1")],
    [sg.Text("alert 2")],
    [sg.Text("alert 3 (DNF)")]
]
blindfold_inputs=[
    [sg.Text()],
    [sg.Input(key='blind_inspect',size=4)],
    [sg.Input(key='blind_1',size=4)],
    [sg.Input(key='blind_2',size=4)],
    [sg.Input(key='blind_dnf',size=4)]
]
blindfolded_col=[
    [
        sg.Column(blindfolded_titles),
        sg.Column(blindfold_inputs)
    ],
    [
        sg.Button("Setup Blindfolded",key="bf_button")
    ]
]

count_up_col=[
    [sg.Text("countup"),sg.Input(key='countup',size=4)],
    [
        sg.Button("Setup Count Up",key="cu_button")
    ]
]

countdown_col=[
    [sg.Text("countdown")],
    [sg.Text("Start time"),sg.Input(key='countdown',size=4)],
    [sg.Button("Setup Countdown",key="cd_button")]
]

clock_set=[
    sg.Text("year"),sg.Input(key='year',size=4),
    sg.Text("month"),sg.Input(key='month',size=4),
    sg.Text("day"),sg.Input(key='day',size=4),
    sg.Text("hour"),sg.Input(key='hour',size=4),
    sg.Text("minute"),sg.Input(key='minute',size=4),
    sg.Text("second"),sg.Input(key='second',size=4),
    sg.Button("Set Clock",key='clock_button')
]

actions=[
    sg.Button("Get scores",key='scores'),
    sg.Button("Read scores from SD", key='sd_button'),
    sg.Button("Port", key='refresh_port'),
    sg.Combo([],key="port_select",enable_events=True,s=16),
    sg.Button("Exit",key='exit')
]

layout=[
    [sg.Column(normal_col,background_color="blue"),
    sg.Column(blindfolded_col,background_color="red"),
    sg.Column(count_up_col,background_color="green"),
    sg.Column(countdown_col,background_color="white")],
    clock_set,
    actions
]
window=sg.Window("Cube Stuff",layout)

def main():
    """main loop"""
    window.finalize()
    refresh_port('x')
    while True:
        print("pre-read")
        event,values=window.read() #blocking call
        print("post-read")
        print(event,values)
        switch={
            'norm_button':setup_normal,
            "bf_button":set_blind,
            "cu_button":set_countup,
            "cd_button":set_countdown,
            'clock_button':set_clock,
            'scores':read_scores,
            'sd_button':read_sd,
            'port_select':set_port,
            'refresh_port':refresh_port,
            sg.WIN_CLOSED:None,
        }
        if event in (sg.WIN_CLOSED,'exit'):
            break
        if event:
            print(event,type(event))
            if switch.get(event):
                switch[event](values)
            else:
                raise Exception("Undefined event")
        else:
            print("no event")
            break


    window.close()

def read_sd(values):
    """Read scores from SD card"""
    print("read sd")
    del values
def setup_normal(values):
    """Set up normal timer"""
    print("Normal")
    cmd={}
    cmd['mode']='normal'
    cmd['inspct']=values['normal_inspect']
    cmd['alert1']=values['normal_1']
    cmd['alert2']=values['normal_2']
    cmd['dnf']=values['normal_dnf']
    send_command(values['port_select'],cmd)

def set_blind(values):
    """Setup Blind"""
    cmd={}
    cmd['mode']='blind'
    cmd['inspect']=values['blind_inspect']
    cmd['alert1']=values['blind_1']
    cmd['alert2']=values['blind_2']
    cmd['dnf']=values['blind_dnf']
    send_command(values['port_select'],cmd)

def set_countup(values):
    """Setup count up timer"""
    del values
    cmd={'mode':'cu'}
    send_command(values['port_select'],cmd)

def set_countdown(values):
    """Setup countdown"""
    cmd={}
    cmd['mode']='cd'
    cmd['cd']=values['countdown']
    send_command(values['port_select'],cmd)


def set_clock(values):
    """"Set real time clock"""
    cmd={}
    cmd['year']=values['year']
    cmd['month']=values['month']
    cmd['day']=values['day']
    cmd['hour']=values['hour']
    cmd['minute']=values['minute']
    cmd['second']=values['second']
    send_command(values['port_select'],cmd)

def read_scores(values):
    """"Read scores via serial"""
    del values
    cmd={'mode':'rs'}
    send_command(values['port_select'],cmd)

def send_command(port,cmds):
    """Send command across serial"""
    ser.port=port
    ser.timeout=1
    ser.open()
    #ser=serial.Serial(,timeout=1)

    for cmd in cmds:
        print("#",cmd)
        serline=str(cmd+":"+cmds[cmd])
        ser.write(serline.encode('UTF-8'))
    print(ser.readlines())
    ser.close()

def refresh_port(values):
    """Refresh port selector"""
    del values
    port_list=get_ports()
    window['port_select'].update(values=port_list,value=port_list[0])


def set_port(values):
    """Set the port when it is changed in the selector"""
    ser.port=values['port_select']
main()
