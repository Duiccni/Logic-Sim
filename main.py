import pygame
import sys

pygame.init()
pygame.font.init()


class data:
    TILES = 30
    COL_A = 40
    ROW_A = 26
    WIDTH = COL_A * TILES
    HEIGHT = ROW_A * TILES
    H_WIDTH = WIDTH // 2
    H_HEIGHT = HEIGHT // 2


class colors:
    BG = 0x100808
    DARK = 0x2E2A2B
    LIGHT = 0x8A6D71
    WHITE = 0xDEC5C5
    GREEN = 0x33CF45
    BLUE = 0x29298F
    L_BLUE = 0x5656AA
    RED = 0x883C46
    RGB_WHIT = (0xC5, 0xC5, 0xC5)
    RGB_BLUE = (0x30, 0x30, 0xC5)
    RGB_RED = (0xC5, 0x30, 0x30)


class settings:
    TRIAL_LEN = 6
    QUALITY = 10
    CUS_QUALITY = 4
    ELEMENT_LEN = 5


class wire:
    def __init__(self, start, end, edgecon=[None, None], connects=[]):
        self.start = start
        self.end = end
        self.power = False
        self.edgecon = edgecon.copy()
        self.connects = connects.copy()

    def get_values(self, index):
        print(index, self.start, self.end, self.power, self.edgecon, self.connects)


class inputO:
    def __init__(self, pos):
        self.pos = pos
        self.power = False


class outputO:
    def __init__(self, pos):
        self.pos = pos
        self.power = False


class notO:
    def __init__(self, pos, end, rot, edgecon=[None, None]):
        self.pos = pos
        self.end = end
        self.rot = rot
        self.edgecon = edgecon.copy()
        self.selected = False


class andO:
    def __init__(self, pos, end, ipos, rot, edgecon=[None, None, None]):
        self.pos = pos
        self.end = end
        self.ipos = ipos
        self.rot = rot
        self.edgecon = edgecon.copy()
        self.selected = False


class custom_gateO:
    def __init__(self, wires=[], gates=[], inputs=[], outputs=[]):
        self.wires = [
            [False, list(filter(None, wo.edgecon)) + wo.connects] for wo in wires
        ]
        self.inputs = []
        for io in inputs:
            for wi in range(len(wires)):
                if wires[wi].start == io.pos or wires[wi].end == io.pos:
                    self.inputs.append(wi)
                    break
        self.outputs = []
        for oo in outputs:
            for wi in range(len(wires)):
                if wires[wi].start == oo.pos or wires[wi].end == oo.pos:
                    self.outputs.append(wi)
                    break
        self.gates = [
            (False if type(go) == notO else True, go.edgecon.copy()) for go in gates
        ]

    def wire_thread(self, already, power, index, time):
        for sub_wire in self.wires[index][1]:
            if sub_wire not in already:
                already.append(sub_wire)
                self.wires[sub_wire][0] = power
                if time < settings.QUALITY:
                    self.wire_thread(already, power, index, time + 1)

    def get_output(self, inputs=[]):
        if len(inputs) != len(self.inputs):
            return -1
        for ii in range(len(self.inputs)):
            self.wires[self.inputs[ii]][0] = inputs[ii]
            alreadyset = [self.inputs[ii]]
            self.wire_thread(alreadyset, inputs[ii], self.inputs[ii], 0)
        for i in range(settings.CUS_QUALITY):
            for gate in self.gates:
                if gate[0]:
                    power = self.wires[gate[1][0]][0] and self.wires[gate[1][2]][0]
                else:
                    power = self.wires[gate[1][0]][0] ^ True
                self.wires[gate[1][1]][0] = power
                alreadyset = [gate[1][1]]
                self.wire_thread(alreadyset, power, gate[1][1], 0)
        output = []
        for oo in self.outputs:
            output.append(self.wires[oo][0])
        return output

    def get_values(self):
        print(self.wires)
        print(self.inputs)
        print(self.outputs)
        print(self.gates)


custom_created_gates = []


class created_gate:
    def __init__(self, pos, type_index, edgei=[], edgeo=[]):
        self.pos = pos
        self.type_index = type_index
        self.edgei = edgei.copy()
        self.edgeo = edgeo.copy()


custom_gates = []

tsurface = pygame.Surface((data.WIDTH, data.HEIGHT), pygame.SRCALPHA, 32)
screen = pygame.display.set_mode((data.WIDTH, data.HEIGHT), pygame.NOFRAME, vsync=1)
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 28)
fontsmal = pygame.font.SysFont(None, 18)
elabels = [
    "Wire",
    "Input",
    "Output",
    "Not Gate",
    "And Gate",
    "Move",
    "Cus 1",
    "Cus 2",
    "Cus 3",
    "Cus 4",
]
cusest = [
    fontsmal.render("1", True, colors.RGB_RED),
    fontsmal.render("2", True, colors.RGB_RED),
    fontsmal.render("3", True, colors.RGB_RED),
    fontsmal.render("4", True, colors.RGB_RED),
]
stext = font.render(elabels[0], True, colors.RGB_WHIT)

pygame.mouse.set_visible(False)

lclickhold = False
rselection = False
changable = False

wires = []
mouse_trial = []
gates = []
inputs = []
outputs = []

swires = []
sgates = []
sinputs = []
soutputs = []


def clear_selecteds():
    swires.clear()
    sgates.clear()
    sinputs.clear()
    soutputs.clear()


slct_elem = 0
rotation = 0
copy_mode = False

temp = [None] * 2
temp2 = [None] * 2


def clear_temp(size=2):
    global temp
    temp = [None] * size


def clear_temp2(size=2):
    global temp2
    temp2 = [None] * size


def update_ltext():
    global stext
    stext = font.render(
        elabels[slct_elem],
        True,
        (colors.RGB_RED if copy_mode else colors.RGB_BLUE)
        if changable == 1
        else colors.RGB_WHIT,
    )


def axis_check(start, end):  # X axis = 1, Y = 0
    return abs(start[0] - end[0]) > abs(start[1] - end[1])


def check_touch(pos):
    for wi in range(len(wires)):
        axis = wires[wi].start[0] == wires[wi].end[0]
        maxpos = max(wires[wi].start[axis], wires[wi].end[axis])
        minpos = min(wires[wi].start[axis], wires[wi].end[axis])
        ax_ops = axis ^ True
        if (
            pos[ax_ops] == wires[wi].start[ax_ops]
            and pos[axis] <= maxpos
            and pos[axis] >= minpos
        ):
            return wi
    return None


def wire_thread(already, power, index, time):
    for sub_wire in wires[index].edgecon + wires[index].connects:
        if sub_wire != None and sub_wire not in already:
            already.append(sub_wire)
            wires[sub_wire].power = power
            if time < settings.QUALITY:
                wire_thread(already, power, sub_wire, time + 1)


def is_inrect(pos, minpos, maxpos):
    return (
        minpos[0] <= pos[0]
        and minpos[1] <= pos[1]
        and maxpos[0] >= pos[0]
        and maxpos[1] >= pos[1]
    )


while True:
    mdown = False
    for e in pygame.event.get():
        match e.type:
            case pygame.QUIT:
                pygame.quit()
                sys.exit()
            case pygame.MOUSEBUTTONDOWN:
                mdown = True
            case pygame.KEYDOWN:
                match e.key:
                    case pygame.K_m:
                        custom_created_gates.append(
                            custom_gateO(wires, gates, inputs, outputs)
                        )
                        settings.ELEMENT_LEN += 1
                        slct_elem = settings.ELEMENT_LEN
                        if changable == 1:
                            changable = 2
                        update_ltext()
                    case pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    case pygame.K_SPACE:
                        for ii in range(len(inputs)):
                            for wi in range(len(wires)):
                                if (
                                    wires[wi].start == inputs[ii].pos
                                    or wires[wi].end == inputs[ii].pos
                                ):
                                    alreadyset = [wi]
                                    wires[wi].power = inputs[ii].power
                                    wire_thread(alreadyset, inputs[ii].power, wi, 0)
                                    break
                        for gi in range(len(gates)):
                            if None not in gates[gi].edgecon:
                                tpower = False
                                if type(gates[gi]) == notO:
                                    tpower = wires[gates[gi].edgecon[0]].power ^ True
                                elif type(gates[gi]) == andO:
                                    tpower = (
                                        wires[gates[gi].edgecon[0]].power
                                        and wires[gates[gi].edgecon[2]].power
                                    )
                                alreadyset = [gates[gi].edgecon[1]]
                                wires[gates[gi].edgecon[1]].power = tpower
                                wire_thread(alreadyset, tpower, gates[gi].edgecon[1], 0)
                        for cg in custom_gates:
                            output = custom_created_gates[cg.type_index].get_output(
                                [
                                    (False if wi == None else wires[wi].power)
                                    for wi in cg.edgei
                                ]
                            )
                            for i in range(len(cg.edgeo)):
                                if cg.edgeo[i] != None:
                                    wires[cg.edgeo[i]].power = output[i]
                        for oi in range(len(outputs)):
                            for wi in range(len(wires)):
                                if (
                                    wires[wi].start == outputs[oi].pos
                                    or wires[wi].end == outputs[oi].pos
                                ):
                                    outputs[oi].power = wires[wi].power
                                    break
                    case pygame.K_z:
                        pass  # Undo
                    case pygame.K_x:
                        pass  # Redo
                    case pygame.K_c:
                        wires.clear()
                        gates.clear()
                        inputs.clear()
                        outputs.clear()
                        custom_gates.clear()
                    case pygame.K_v:
                        print()
                        for wi in range(len(wires)):
                            wires[wi].get_values(wi)
                        for elm in inputs + outputs:
                            print(type(elm), elm.pos)
                        for gate in gates:
                            print(type(gate), gate.pos, gate.edgecon)
                        for cus in custom_created_gates:
                            cus.get_values()
                        for cg in custom_gates:
                            print(cg.edgei, cg.edgeo)
                    case pygame.K_UP:
                        if slct_elem < settings.ELEMENT_LEN:
                            if changable == 1:
                                changable = 2
                            slct_elem += 1
                        update_ltext()
                    case pygame.K_DOWN:
                        if slct_elem > 0:
                            if changable == 1:
                                changable = 2
                            slct_elem -= 1
                        update_ltext()
                    case pygame.K_RIGHT:
                        if rotation < 3:
                            rotation += 1
                        else:
                            rotation = 0
                    case pygame.K_LEFT:
                        if rotation > 0:
                            rotation -= 1
                        else:
                            rotation = 3
                    case pygame.K_TAB:
                        copy_mode ^= True
                        update_ltext()
    screen.fill(colors.BG)
    mpos = pygame.mouse.get_pos()
    mpre = pygame.mouse.get_pressed()

    relmpos = (
        round(mpos[0] / data.TILES) * data.TILES,
        round(mpos[1] / data.TILES) * data.TILES,
    )

    for x in range(data.TILES, data.WIDTH, data.TILES):
        pygame.draw.line(screen, colors.DARK, (x, 0), (x, data.HEIGHT))
    for x in range(data.TILES, data.HEIGHT, data.TILES):
        pygame.draw.line(screen, colors.DARK, (0, x), (data.WIDTH, x))

    for wo in wires:
        pygame.draw.line(
            screen,
            colors.GREEN
            if wo.power == 1
            else (colors.L_BLUE if wo.power == 2 else colors.LIGHT),
            wo.start,
            wo.end,
            2,
        )
        for i in range(2):
            if wo.edgecon[i] != None:
                pygame.draw.circle(screen, colors.LIGHT, wo.end if i else wo.start, 3)

    screen.blit(stext, (10, 10))

    for elm in inputs:
        pygame.draw.rect(
            screen,
            colors.GREEN
            if elm.power == 1
            else (colors.L_BLUE if elm.power == 2 else colors.LIGHT),
            (elm.pos[0] - 5, elm.pos[1] - 5, 10, 10),
            2,
        )

    for elm in outputs:
        pygame.draw.circle(
            screen,
            colors.GREEN
            if elm.power == 1
            else (colors.L_BLUE if elm.power == 2 else colors.LIGHT),
            elm.pos,
            5,
            2,
        )

    for cg in custom_gates:
        leni = len(custom_created_gates[cg.type_index].inputs)
        leno = len(custom_created_gates[cg.type_index].outputs)
        screen.blit(cusest[cg.type_index], (cg.pos[0] + 3, cg.pos[1] + 3))
        pygame.draw.rect(
            screen,
            colors.RED,
            (cg.pos[0], cg.pos[1], data.TILES, (max(leni, leno) - 1) * data.TILES),
            2,
        )
        for i in range(leni):
            if cg.edgei[i] != None:
                pygame.draw.circle(
                    screen, colors.RED, (cg.pos[0], cg.pos[1] + data.TILES * i), 4, 2
                )
        for i in range(leno):
            if cg.edgeo[i] != None:
                pygame.draw.circle(
                    screen,
                    colors.RED,
                    (cg.pos[0] + data.TILES, cg.pos[1] + data.TILES * i),
                    4,
                    2,
                )

    for gate in gates:
        if gate.edgecon[0] != None:
            pygame.draw.circle(screen, colors.RED, gate.pos, 4, 2)
        if gate.edgecon[1] != None:
            pygame.draw.circle(screen, colors.RED, gate.end, 4, 2)
        if type(gate) == notO:
            tmpd = ((gate.rot % 2) * 10, (1 - gate.rot % 2) * 10)
            pygame.draw.polygon(
                screen,
                colors.L_BLUE if gate.selected else colors.RED,
                (
                    (gate.pos[0] + tmpd[0], gate.pos[1] + tmpd[1]),
                    (gate.pos[0] - tmpd[0], gate.pos[1] - tmpd[1]),
                    gate.end,
                ),
                2,
            )
        elif type(gate) == andO:
            if gate.edgecon[2] != None:
                pygame.draw.circle(screen, colors.RED, gate.ipos, 4, 2)
            pygame.draw.lines(
                screen,
                colors.L_BLUE if gate.selected else colors.RED,
                False,
                (gate.ipos, gate.pos, gate.end),
                2,
            )
            pygame.draw.circle(
                screen,
                colors.L_BLUE if gate.selected else colors.RED,
                gate.pos,
                data.TILES,
                2,
                gate.rot == 0,
                gate.rot == 3,
                gate.rot == 2,
                gate.rot == 1,
            )

    mouse_trial.append(mpos)
    if len(mouse_trial) > settings.TRIAL_LEN:
        mouse_trial.pop(0)
    for i in range(len(mouse_trial) - 2):
        pygame.draw.line(screen, colors.DARK, mouse_trial[i], mouse_trial[i + 1], 2)

    if changable == 2:
        changable = False
        if lclickhold == True and (difpos[0] != 0 or difpos[1] != 0):
            if copy_mode:
                indexstart = len(wires)
                swires.sort()
                for wi in swires:
                    #wires.append(wire((wires[wi].start[0] + difpos[0],wires[wi].start[1] + difpos[1],),(wires[wi].end[0] + difpos[0],wires[wi].end[1] + difpos[1],),[((indexstart + swires.index(wires[wi].edgecon[i])) if wires[wi].edgecon[i] in swireselse None)for i in range(2)],list(filter(None,[((indexstart + swires.index(i))if i in swireselse None)for i in wires[wi].connects],)),))
                    wires[wi].power = 0
                for ii in sinputs:
                    inputs.append(
                        inputO(
                            (
                                inputs[ii].pos[0] + difpos[0],
                                inputs[ii].pos[1] + difpos[1],
                            )
                        )
                    )
                    inputs[ii].power = 0
                for oi in soutputs:
                    outputs.append(
                        outputO(
                            (
                                outputs[oi].pos[0] + difpos[0],
                                outputs[oi].pos[1] + difpos[1],
                            )
                        )
                    )
                    outputs[oi].power = 0
                for gi in sgates:
                    if type(gates[gi]) == notO:
                        gates.append(
                            notO(
                                (
                                    gates[gi].pos[0] + difpos[0],
                                    gates[gi].pos[1] + difpos[1],
                                ),
                                (
                                    gates[gi].end[0] + difpos[0],
                                    gates[gi].end[1] + difpos[1],
                                ),
                                gates[gi].rot,
                                [
                                    (
                                        (
                                            indexstart
                                            + swires.index(gates[gi].edgecon[i])
                                        )
                                        if gates[gi].edgecon[i] in swires
                                        else None
                                    )
                                    for i in range(2)
                                ],
                            )
                        )
                    elif type(gates[gi]) == andO:
                        gates.append(
                            andO(
                                (
                                    gates[gi].pos[0] + difpos[0],
                                    gates[gi].pos[1] + difpos[1],
                                ),
                                (
                                    gates[gi].end[0] + difpos[0],
                                    gates[gi].end[1] + difpos[1],
                                ),
                                (
                                    gates[gi].ipos[0] + difpos[0],
                                    gates[gi].ipos[1] + difpos[1],
                                ),
                                gates[gi].rot,
                                [
                                    (
                                        (
                                            indexstart
                                            + swires.index(gates[gi].edgecon[i])
                                        )
                                        if gates[gi].edgecon[i] in swires
                                        else None
                                    )
                                    for i in range(3)
                                ],
                            )
                        )
                    gates[gi].selected = False
            else:
                for wi in swires:
                    for i in range(2):
                        if (
                            wires[wi].edgecon[i] != None
                            and wires[wi].edgecon[i] not in swires
                        ):
                            wires[wires[wi].edgecon[i]].connects.remove(wi)
                            wires[wi].edgecon[i] = None
                    for ci in range(len(wires[wi].connects)):
                        if wires[wi].connects[ci] not in swires:
                            wires[wires[wi].connects[ci]].edgecon[
                                wires[wires[wi].connects[ci]].edgecon.index(wi)
                            ] = None
                            wires[wi].connects.pop(ci)
                    wires[wi].start = (
                        wires[wi].start[0] + difpos[0],
                        wires[wi].start[1] + difpos[1],
                    )
                    wires[wi].end = (
                        wires[wi].end[0] + difpos[0],
                        wires[wi].end[1] + difpos[1],
                    )
                    wires[wi].power = 0
                for ii in sinputs:
                    inputs[ii].pos = (
                        inputs[ii].pos[0] + difpos[0],
                        inputs[ii].pos[1] + difpos[1],
                    )
                    inputs[ii].power = 0
                for oi in soutputs:
                    outputs[oi].pos = (
                        outputs[oi].pos[0] + difpos[0],
                        outputs[oi].pos[1] + difpos[1],
                    )
                    outputs[oi].power = 0
                for gi in sgates:
                    for i in range(2 + (type(gates[gi]) == andO)):
                        if gates[gi].edgecon[i] not in swires:
                            gates[gi].edgecon[i] = None
                    gates[gi].pos = (
                        gates[gi].pos[0] + difpos[0],
                        gates[gi].pos[1] + difpos[1],
                    )
                    gates[gi].end = (
                        gates[gi].end[0] + difpos[0],
                        gates[gi].end[1] + difpos[1],
                    )
                    if type(gates[gi]) == andO:
                        gates[gi].ipos = (
                            gates[gi].ipos[0] + difpos[0],
                            gates[gi].ipos[1] + difpos[1],
                        )
                    gates[gi].selected = False
        lclickhold = False
        copy_mode = False
        clear_selecteds()
    elif changable == 1:
        if mpre[0]:
            if lclickhold == False:
                lclickhold = True
                spos = relmpos
                epos = relmpos
                difpos = (0, 0)
            if epos != relmpos:
                epos = relmpos
                difpos = (epos[0] - spos[0], epos[1] - spos[1])
                tsurface.fill(0)
                if difpos[0] != 0 or difpos[1] != 0:
                    pygame.draw.rect(
                        tsurface,
                        (0x30, 0x30, 0x50, 0x50),
                        (
                            minpos[0] + difpos[0],
                            minpos[1] + difpos[1],
                            maxpos[0] - minpos[0],
                            maxpos[1] - minpos[1],
                        ),
                    )
            if difpos[0] != 0 or difpos[1] != 0:
                screen.blit(tsurface, (0, 0))
                pygame.draw.rect(
                    screen,
                    colors.BLUE,
                    (
                        minpos[0] + difpos[0],
                        minpos[1] + difpos[1],
                        maxpos[0] - minpos[0],
                        maxpos[1] - minpos[1],
                    ),
                    3,
                )
                pygame.draw.line(screen, colors.RED, spos, epos)
                pygame.draw.circle(screen, colors.RED, spos, 6, 3)
                pygame.draw.circle(screen, colors.RED, epos, 6, 3)
        elif lclickhold == True:
            difpos = (epos[0] - spos[0], epos[1] - spos[1])
            slct_elem = settings.ELEMENT_LEN - 1
            changable = 2
            update_ltext()
    elif mpre[2] and slct_elem == 5:  # Zelect
        if rselection == False:
            rselection = True
            spos = relmpos
            epos = relmpos
            maxpos = relmpos
            minpos = relmpos
            difbool = False
            tsurface.fill(0)
        if epos != relmpos:
            epos = relmpos
            maxpos = (max(spos[0], epos[0]), max(spos[1], epos[1]))
            minpos = (min(spos[0], epos[0]), min(spos[1], epos[1]))
            difbool = (epos[0] - spos[0]) != 0 and (epos[1] - spos[1]) != 0
            tsurface.fill(0)
            if difbool:
                pygame.draw.rect(
                    tsurface,
                    (0x30, 0x30, 0x50, 0x50),
                    (
                        minpos[0],
                        minpos[1],
                        maxpos[0] - minpos[0],
                        maxpos[1] - minpos[1],
                    ),
                )
        if difbool:
            screen.blit(tsurface, (0, 0))
            pygame.draw.rect(
                screen,
                colors.BLUE,
                (minpos[0], minpos[1], maxpos[0] - minpos[0], maxpos[1] - minpos[1]),
                3,
            )
    elif rselection == True:
        rselection = False
        if difbool:
            clear_selecteds()
            for wi in range(len(wires)):
                if is_inrect(wires[wi].start, minpos, maxpos) and is_inrect(
                    wires[wi].end, minpos, maxpos
                ):
                    swires.append(wi)
                    wires[wi].power = 2
            for ii in range(len(inputs)):
                if is_inrect(inputs[ii].pos, minpos, maxpos):
                    sinputs.append(ii)
                    inputs[ii].power = 2
            for oi in range(len(outputs)):
                if is_inrect(outputs[oi].pos, minpos, maxpos):
                    soutputs.append(oi)
                    outputs[oi].power = 2
            for gi in range(len(gates)):
                if is_inrect(gates[gi].pos, minpos, maxpos):
                    sgates.append(gi)
                    gates[gi].selected = True
            changable = True
            update_ltext()
    elif mdown:
        if mpre[1]:  # Power
            for io in inputs:
                if io.pos == relmpos:
                    io.power ^= True
                    break
        elif mpre[2]:
            if slct_elem == 0:  # Delete
                index = check_touch(relmpos)
                if index != None:
                    for i in range(2):
                        if wires[index].edgecon[i] != None:
                            wires[wires[index].edgecon[i]].connects.remove(index)
                    for gi in range(len(gates)):
                        for i in range(2 + (type(gates[gi]) == andO)):
                            if gates[gi].edgecon[i] == index:
                                gates[gi].edgecon[i] = None
                            elif (
                                gates[gi].edgecon[i] != None
                                and gates[gi].edgecon[i] > index
                            ):
                                gates[gi].edgecon[i] -= 1
                    for cgi in range(len(custom_gates)):
                        for ii in range(len(custom_gates[cgi].edgei)):
                            if custom_gates[cgi].edgei[ii] == index:
                                custom_gates[cgi].edgei[ii] = None
                            elif (
                                custom_gates[cgi].edgei[ii] != None
                                and custom_gates[cgi].edgei[ii] > index
                            ):
                                custom_gates[cgi].edgei[ii] -= 1
                        for oi in range(len(custom_gates[cgi].edgeo)):
                            if custom_gates[cgi].edgeo[oi] == index:
                                custom_gates[cgi].edgeo[oi] = None
                            elif (
                                custom_gates[cgi].edgeo[oi] != None
                                and custom_gates[cgi].edgeo[oi] > index
                            ):
                                custom_gates[cgi].edgeo[oi] -= 1
                    for wi in range(len(wires)):
                        for i in range(2):
                            if wires[wi].edgecon[i] == index:
                                wires[wi].edgecon[i] = None
                            elif (
                                wires[wi].edgecon[i] != None
                                and wires[wi].edgecon[i] > index
                            ):
                                wires[wi].edgecon[i] -= 1
                        for k in range(len(wires[wi].connects)):
                            if wires[wi].connects[k] > index:
                                wires[wi].connects[k] -= 1
                    wires.pop(index)
            else:
                bstop = False
                for elml in [inputs, outputs, gates, custom_gates]:
                    if bstop:
                        break
                    for iE in range(len(elml)):
                        if elml[iE].pos == relmpos:
                            elml.pop(iE)
                            bstop = True
                            break
        elif mpre[0] and slct_elem != 0:  # Place
            gon_append = True
            for elm in inputs + outputs + gates + custom_gates:
                if elm.pos == relmpos:
                    gon_append = False
                    break
            if gon_append:
                match slct_elem:
                    case 1:
                        inputs.append(inputO(relmpos))
                    case 2:
                        outputs.append(outputO(relmpos))
                    case 3:
                        tmpd = (data.TILES * (1 - rotation // 2 * 2), rotation % 2)
                        tend = (
                            relmpos[0] + (tmpd[1] ^ True) * tmpd[0],
                            relmpos[1] + tmpd[1] * tmpd[0],
                        )
                        clear_temp()
                        for wi in range(len(wires)):
                            if temp[0] == None and (
                                wires[wi].start == relmpos or wires[wi].end == relmpos
                            ):
                                temp[0] = wi
                            elif temp[1] == None and (
                                wires[wi].start == tend or wires[wi].end == tend
                            ):
                                temp[1] = wi
                            elif None not in temp:
                                break
                        gates.append(notO(relmpos, tend, rotation, temp))
                    case 4:
                        match rotation:
                            case 0:
                                tend = (relmpos[0] + data.TILES, relmpos[1])
                                tinp = (relmpos[0], relmpos[1] - data.TILES)
                            case 1:
                                tend = (relmpos[0], relmpos[1] + data.TILES)
                                tinp = (relmpos[0] + data.TILES, relmpos[1])
                            case 2:
                                tend = (relmpos[0] - data.TILES, relmpos[1])
                                tinp = (relmpos[0], relmpos[1] + data.TILES)
                            case 3:
                                tend = (relmpos[0], relmpos[1] - data.TILES)
                                tinp = (relmpos[0] - data.TILES, relmpos[1])
                        clear_temp(3)
                        for wi in range(len(wires)):
                            if temp[0] == None and (
                                wires[wi].start == relmpos or wires[wi].end == relmpos
                            ):
                                temp[0] = wi
                            elif temp[1] == None and (
                                wires[wi].start == tend or wires[wi].end == tend
                            ):
                                temp[1] = wi
                            elif temp[2] == None and (
                                wires[wi].start == tinp or wires[wi].end == tinp
                            ):
                                temp[2] = wi
                            elif None not in temp:
                                break
                        gates.append(andO(relmpos, tend, tinp, rotation, temp))
                    case _:
                        leni = len(custom_created_gates[slct_elem - 6].inputs)
                        leno = len(custom_created_gates[slct_elem - 6].outputs)
                        clear_temp(leni)
                        clear_temp2(leno)
                        for i in range(leni):
                            npos = (relmpos[0], relmpos[1] + i * data.TILES)
                            for wi in range(len(wires)):
                                if temp[i] == None and (
                                    wires[wi].start == npos or wires[wi].end == npos
                                ):
                                    temp[i] = wi
                                elif None not in temp:
                                    break
                        for i in range(leno):
                            npos = (
                                relmpos[0] + data.TILES,
                                relmpos[1] + i * data.TILES,
                            )
                            for wi in range(len(wires)):
                                if temp2[i] == None and (
                                    wires[wi].start == npos or wires[wi].end == npos
                                ):
                                    temp2[i] = wi
                                elif None not in temp2:
                                    break
                        custom_gates.append(
                            created_gate(relmpos, slct_elem - 6, temp, temp2)
                        )
    if mpre[0] and slct_elem == 0:
        if lclickhold == False:
            lclickhold = True
            spos = relmpos
            epos = relmpos
            clear_temp()
            temp[0] = check_touch(spos)
        if epos != relmpos:
            epos = relmpos
            temp[1] = check_touch(relmpos)
            isteep = axis_check(spos, epos)
        if spos != relmpos:
            pygame.draw.line(
                screen,
                colors.BLUE,
                spos,
                (epos[0] if isteep else spos[0], spos[1] if isteep else epos[1]),
                3,
            )
            if temp[0] != None:
                pygame.draw.circle(screen, colors.BLUE, spos, 4)
            if temp[1] != None:
                pygame.draw.circle(screen, colors.BLUE, epos, 4)
    elif lclickhold == True and changable == 0:
        lclickhold = False
        epos = relmpos
        if spos != relmpos:
            isteep = axis_check(spos, epos)
            tpos = (epos[0] if isteep else spos[0], spos[1] if isteep else epos[1])
            temp[1] = check_touch(tpos)
            gon_append = True
            isteep ^= True
            for i in range(2):
                if (
                    temp[i] != None
                    and isteep != axis_check(wires[temp[i]].start, wires[temp[i]].end)
                    and (
                        wires[temp[i]].start[isteep] != spos[isteep]
                        and wires[temp[i]].start[isteep] != tpos[isteep]
                        and wires[temp[i]].end[isteep] != spos[isteep]
                        and wires[temp[i]].end[isteep] != tpos[isteep]
                    )
                ):
                    gon_append = False
                    break
            if gon_append and temp[0] != None and temp[0] == temp[1]:
                gon_append = False
            if gon_append:
                for i in range(2):
                    if temp[i] != None:
                        wires[temp[i]].connects.append(len(wires))
                for gi in range(len(gates)):
                    if gates[gi].edgecon[0] == None and (
                        gates[gi].pos == spos or gates[gi].pos == tpos
                    ):
                        gates[gi].edgecon[0] = len(wires)
                    elif gates[gi].edgecon[1] == None and (
                        gates[gi].end == spos or gates[gi].end == tpos
                    ):
                        gates[gi].edgecon[1] = len(wires)
                    elif (
                        type(gates[gi]) == andO
                        and gates[gi].edgecon[2] == None
                        and (gates[gi].ipos == spos or gates[gi].ipos == tpos)
                    ):
                        gates[gi].edgecon[2] = len(wires)
                for cgi in range(len(custom_gates)):
                    bstop = False
                    for i in range(len(custom_gates[cgi].edgei)):
                        npos = (
                            custom_gates[cgi].pos[0],
                            custom_gates[cgi].pos[1] + i * data.TILES,
                        )
                        if custom_gates[cgi].edgei[i] == None and (
                            npos == spos or npos == tpos
                        ):
                            custom_gates[cgi].edgei[i] = len(wires)
                            bstop = True
                            break
                    if bstop == True:
                        continue
                    for i in range(len(custom_gates[cgi].edgeo)):
                        npos = (
                            custom_gates[cgi].pos[0] + data.TILES,
                            custom_gates[cgi].pos[1] + i * data.TILES,
                        )
                        if custom_gates[cgi].edgeo[i] == None and (
                            npos == spos or npos == tpos
                        ):
                            custom_gates[cgi].edgeo[i] = len(wires)
                            break
                wires.append(wire(spos, tpos, temp))
        clear_temp()

    if slct_elem > 5:
        pygame.draw.rect(
            screen,
            colors.RED,
            (
                relmpos[0],
                relmpos[1],
                data.TILES / 2,
                (
                    max(
                        len(custom_created_gates[slct_elem - 6].inputs),
                        len(custom_created_gates[slct_elem - 6].outputs),
                    )
                    - 1
                )
                * data.TILES,
            ),
            2,
        )
    else:
        match slct_elem:
            case 0:
                pygame.draw.circle(screen, colors.WHITE, relmpos, 3)
            case 1:
                pygame.draw.rect(
                    screen,
                    colors.WHITE,
                    (relmpos[0] - 5, relmpos[1] - 5, 10, 10),
                    2,
                )
            case 2:
                pygame.draw.circle(screen, colors.WHITE, relmpos, 5, 2)
            case 5:
                pygame.draw.circle(screen, colors.BLUE, relmpos, 3)
            case _:
                match rotation:
                    case 0:
                        tend = (relmpos[0] + 10, relmpos[1])
                    case 1:
                        tend = (relmpos[0], relmpos[1] + 10)
                    case 2:
                        tend = (relmpos[0] - 10, relmpos[1])
                    case 3:
                        tend = (relmpos[0], relmpos[1] - 10)
                pygame.draw.line(screen, colors.RED, relmpos, tend, 3)

    pygame.display.update()
    clock.tick(60)
