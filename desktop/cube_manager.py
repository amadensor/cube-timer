"""Cube manager"""
import PySimpleGUI as sg

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
    ]
]

count_up_col=[
    [sg.Text("countup"),sg.Input(key='countup',size=4)]
]

countdown_col=[
    [sg.Text("countdown")],
    [sg.Text("Start time"),sg.Input(key='countdown',size=4)]
]

clock_set=[
    sg.Text("year"),sg.Input(key='year',size=4),
    sg.Text("month"),sg.Input(key='month',size=4),
    sg.Text("day"),sg.Input(key='day',size=4),
    sg.Text("hour"),sg.Input(key='hour',size=4),
    sg.Text("minute"),sg.Input(key='minute',size=4),
    sg.Text("second"),sg.Input(key='second',size=4),
    sg.Button("set clock",key='clock')
]

actions=[
    sg.Button("Get scores",key='scores'),
    sg.Button("Read scores from SD", key='sd'),
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

def main():
    """main loop"""
    window=sg.Window("Cube Stuff",layout)
    while True:
        print("pre-read")
        event,values=window.read() #blocking call
        print("post-read")
        print(event,values)
        switch={
            'sd':read_sd,
            sg.WIN_CLOSED:None,
        }
        if event in (sg.WIN_CLOSED,'exit'):
            break
        if event:
            print(event,type(event))
            if switch.get(event):
                switch[event]()
            else:
                raise Exception("Undefined event")
        else:
            print("no event")
            break


    window.close()

def read_sd():
    """Read scores from SD card"""
    print("read sd")

main()
