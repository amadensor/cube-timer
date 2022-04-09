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
    [sg.Text("Cutoff")],
    [sg.Text("Inspection Time")],
    [sg.Text("Inspection Limit")],
    [sg.Text("Alert 1")],
    [sg.Text("Alert 2")],
]
normal_inputs=[
    [sg.Input(key='normal_cutoff',size=4,default_text="600")],
    [sg.Input(key='normal_inspect',size=4,default_text="15")],
    [sg.Input(key='normal_limit',size=4,default_text="17")],
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
    [sg.Text("Cutoff")],
    [sg.Text("Inspection Time - 0")],
    [sg.Text("Inspection Timit - 0")],
    [sg.Text("Alert 1")],
    [sg.Text("Alert 2")]
]
blindfold_inputs=[
    [sg.Input(key='blind_cutoff',size=4,default_text="0")],
    [sg.Input(key='blind_inspect',size=4,default_text="0")],
    [sg.Input(key='blind_limit',size=4,default_text="0")],
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
    sg.Button("Set Clock",key='clock_button')]
]

actions=[
    sg.Button("Reset scores",key='scores'),
    sg.Button("Reboot timer",key='reboot'),
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
            'scores':reset_scores,
            'reboot':reboot_timer,
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
    del values
    file_picker=[
        [sg.Text("Pick Target File"),sg.Input(),sg.FileSaveAs(key="-FILE-")],
        [sg.Button("Process")]
        ]
    file_win=sg.Window('File Browse',file_picker)
    file_event,file_values=file_win.read()
    print(file_event)
    print(file_values)
    write_file=file_values[0]
    file_win.close()
    print(write_file)
    cmd={'sd':''}
    score_bytes=send_command(cmd)
    score_list=[]
    for score_byte in score_bytes:
        score_str=score_byte.decode()
        #score_dict=json.loads(score_str)
        #score_list.append(score_dict.decode())
        score_list.append(score_str)
    print(json.dumps(score_list,indent=4))
    save_file=open(write_file,"w")
    for line in score_list[2:]:
        save_file.write(line)
    save_file.close()
    return score_list

def setup_normal(values):
    """Set up normal timer"""
    print("Normal")
    cmd={}
    cmd['mode']='normal'
    cmd['cutoff']=values['normal_cutoff']
    cmd['inspect']=values['normal_inspect']
    cmd['fail']=values['normal_limit']
    cmd['alert1']=values['normal_1']
    cmd['alert2']=values['normal_2']
    send_command(cmd)

def set_blind(values):
    """Setup Blind"""
    cmd={}
    cmd['mode']='blind'
    cmd['cutoff']=values['blind_cutoff']
    cmd['inspect']=values['blind_inspect']
    cmd['fail']=values['blind_limit']
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
    del values
    l_time=time.localtime()
    cmd={}
    cmd['clock']=(
        "C"+
        str(l_time.tm_year)+
        ("00"+str(l_time.tm_mon))[-2:]+
        ("00"+str(l_time.tm_mday))[-2:]+
        ("00"+str(l_time.tm_hour))[-2:]+
        ("00"+str(l_time.tm_min))[-2:]+
        ("00"+str(l_time.tm_sec))[-2:]
    )
    print(cmd)
    send_command(cmd)

def reset_scores(values):
    """"Read scores via serial"""
    del values
    cmd={'rs':''}
    score_bytes=send_command(cmd)
    score_str=score_bytes[0].decode()
    print(score_str)
    return score_str

def reboot_timer(cmds):
    """Send command across serial"""
    serline=chr(3)+chr(3)+chr(3)+"machine.reset()"+chr(11)+chr(13)
    ser.write(serline.encode('UTF-8'))
    time.sleep(1)


def send_command(cmds):
    """Send command across serial"""
    for cmd in cmds:
        print("#",cmd)
        serline=str(cmd+":"+cmds[cmd]+"\n")
        ser.write(serline.encode('UTF-8'))
        time.sleep(1)
    try:
        ret_data=ser.readlines()
        print(ret_data)
    except:
        ret_data=["Nothing".encode("UTF-8")]
    return ret_data

def refresh_port(values):
    """Refresh port selector"""
    port_list=get_ports()
    window['port_select'].update(values=port_list,value=port_list[0])
    #if not values.get('port_select'):
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
