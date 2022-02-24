"""Cube manager"""
import time
import json
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
    [sg.Text("inspection time")],
    [sg.Text("alert 1")],
    [sg.Text("alert 2")],
]
normal_inputs=[
    [sg.Input(key='normal_inspect',size=4,default_text="15")],
    [sg.Input(key='normal_1',size=4,default_text="8")],
    [sg.Input(key='normal_2',size=4,default_text="12")],
]
normal_col=[
    [
        sg.Column(normal_titles),
        sg.Column(normal_inputs)
    ],
    [
        sg.Button("Apply",key="norm_button")
    ]

]

blindfolded_titles=[
    [sg.Text("inspection time - 0")],
    [sg.Text("alert 1")],
    [sg.Text("alert 2")]
]
blindfold_inputs=[
    [sg.Input(key='blind_inspect',size=4,default_text="0")],
    [sg.Input(key='blind_1',size=4,default_text="0")],
    [sg.Input(key='blind_2',size=4,default_text="0")],
]
blindfolded_col=[
    [
        sg.Column(blindfolded_titles),
        sg.Column(blindfold_inputs)
    ],
    [
        sg.Button("Apply",key="bf_button")
    ]
]

count_up_col=[
    [sg.Text("Start From"),sg.Input(key='countup',size=4)],
    [
        sg.Button("Apply",key="cu_button")
    ]
]

countdown_col=[
    [sg.Text("Start time"),sg.Input(key='countdown',size=4)],
    [sg.Button("Apply",key="cd_button")]
]

clock_set=[[
    sg.Text("year"),sg.Input(key='year',size=4),
    sg.Text("month"),sg.Input(key='month',size=4),
    sg.Text("day"),sg.Input(key='day',size=4),
    sg.Text("hour"),sg.Input(key='hour',size=4),
    sg.Text("minute"),sg.Input(key='minute',size=4),
    sg.Text("second"),sg.Input(key='second',size=4),
    sg.Button("Set",key='clock_button')]
]

actions=[
    sg.Button("Get scores",key='scores'),
    sg.Button("Read scores from SD", key='sd_button'),
    sg.Button("Port", key='refresh_port'),
    sg.Combo([],key="port_select",enable_events=True,s=16),
    sg.Button("Exit",key='exit')
]

layout=[
    [sg.Frame("Setup Normal",normal_col),
    sg.Frame("Setup Blindfolded",blindfolded_col),
    sg.Frame("Setup Count Up",count_up_col),
    sg.Frame("Setup Countdown",countdown_col)],
    [sg.Frame("Clock",clock_set)],
    actions
]
window=sg.Window("Cube Stuff",layout)

def main():
    """main loop"""
    window.finalize()
    port=refresh_port({'x':'x'})
    set_port({'port_select':port})
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
    ser.close()


def read_sd(values):
    """Read scores from SD card"""
    print("read sd")
    del values
def setup_normal(values):
    """Set up normal timer"""
    print("Normal")
    cmd={}
    cmd['mode']='normal'
    cmd['inspect']=values['normal_inspect']
    cmd['alert1']=values['normal_1']
    cmd['alert2']=values['normal_2']
    send_command(cmd)

def set_blind(values):
    """Setup Blind"""
    cmd={}
    cmd['mode']='blind'
    cmd['inspect']=values['blind_inspect']
    cmd['alert1']=values['blind_1']
    cmd['alert2']=values['blind_2']
    send_command(cmd)

def set_countup(values):
    """Setup count up timer"""
    del values
    cmd={'mode':'cu'}
    send_command(cmd)

def set_countdown(values):
    """Setup countdown"""
    cmd={}
    cmd['mode']='cd'
    cmd['cd']=values['countdown']
    send_command(cmd)


def set_clock(values):
    """"Set real time clock"""
    cmd={}
    cmd['clock']=(
        "C"+
        values['year']+
        values['month']+
        values['day']+
        values['hour']+
        values['minute']+
        values['second']
    )
    send_command(cmd)

def read_scores(values):
    """"Read scores via serial"""
    del values
    cmd={'rs':''}
    score_bytes=send_command(cmd)
    score_str=score_bytes[0].decode()
    score_dict=json.loads(score_str)
    print(json.dumps(score_dict,indent=4))
    return score_dict

def send_command(cmds):
    """Send command across serial"""
    for cmd in cmds:
        print("#",cmd)
        serline=str(cmd+":"+cmds[cmd])
        ser.write(serline.encode('UTF-8'))
        time.sleep(1)
    ret_data=ser.readlines()
    print(ret_data)
    return ret_data

def refresh_port(values):
    """Refresh port selector"""
    port_list=get_ports()
    window['port_select'].update(values=port_list,value=port_list[0])
    if not values.get('port_select'):
        set_port({"port_select":port_list[0]})
    return port_list[0]


def set_port(values):
    """Set the port when it is changed in the selector"""
    if values['port_select']:
        ser.close()
        ser.port=values['port_select']
        ser.timeout=1
        ser.open()

main()
