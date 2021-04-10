# HotSpotMap: A python based temperature (thermal) map generation
# tool for HotSpot-6.0 (http://lava.cs.virginia.edu/HotSpot/)
# This tool uses python's turtle library
#
# Author: Gaurav Kothari (gkothar1@binghamton.edu) Copyright 2021
# 
#
# This tool generates:
# 1) Floor-plan image (using floor-plan file)
# 2) Thermal map (using floor-plan file and steady temperature file)
# 3) Fine grained thermal map (using floor-plan file and grid steady temperature file)
# 
# Output formats: '.eps' and '.pdf'
import os
import time
import subprocess
import tkinter
import turtle
import numpy as np
import matplotlib
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import argparse
from sys import argv

msg_prefix = "  HotSpotMap:"

# Colors used for temperature map
colors = [
    "#ff0000",
    "#ff3300",
    "#ff6600",
    "#ff9900",
    "#ffcc00",
    "#ffff00",
    "#ccff00",
    "#99ff00",
    "#66ff00",
    "#33ff00",
    "#00ff00",
    "#00ff33",
    "#00ff66",
    "#00ff99",
    "#00ffcc",
    "#00ffff",
    "#00ccff",
    "#0099ff",
    "#0066ff",
    "#0033ff",
    "#0000ff",
]

# Home co-ordinates for drawing the chip floor-plan
# Note: turtle's default home co-ordinates are (0,0)
# For drawing the floor-plan, we will start from (-w/2,-h/2), where
# w = width of the chip, h = height of the chip
chip_home_xpos = 0
chip_home_ypos = 0


class FlpUnit():
    def __init__(self, name, width, height, xpos, ypos, temp=0):
        self.name = name
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.temp = temp


def turtle_setup(config):
    # setup screen
    ts = turtle.Screen()
    cw = (config.chip_width * 1e-3 * config.zoom_by)
    ch = (config.chip_height * 1e-3 * config.zoom_by)
    ts.reset()
    ts.colormode(255)
    ts.tracer(0, 0)
    global chip_home_xpos
    chip_home_xpos = -(cw / 2)
    global chip_home_ypos
    chip_home_ypos = -(ch / 2)

    # create turtle cursor
    t = turtle.Turtle()
    t.pen(shown=False)
    t.width(1)
    t.hideturtle()
    t.penup()
    t.setpos(chip_home_xpos, chip_home_ypos)
    return t


def turtle_save_image(config):
    ts = turtle.getscreen()
    eps_file = os.path.join(
        config.output_dir, "{f}-{a}.eps".format(f=config.output_file,
                                                a=config.action))
    pdf_file = os.path.join(
        config.output_dir, "{f}-{a}.pdf".format(f=config.output_file,
                                                a=config.action))

    canvas = ts.getcanvas()
    canvas.config(width=config.chip_width * 1e-3 * config.zoom_by,
                  height=config.chip_height * 1e-3 * config.zoom_by)
    canvas.postscript(file=eps_file)
    print("{p} generated eps file: {f}".format(p=msg_prefix, f=eps_file))
    cmd = "ps2pdf {i} {o}".format(i=eps_file, o=pdf_file)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    print("{p} generated pdf file: {f}".format(p=msg_prefix, f=pdf_file))


def get_pos_from_chip_home(xpos, ypos):
    return (chip_home_xpos + xpos, chip_home_ypos + ypos)


def draw_chip_dimensions(t, config):
    # draw height scale on left of the floor-plan
    arrow_height = 15
    xpos = -30
    ypos = 0
    t.penup()
    t.setpos(get_pos_from_chip_home(xpos, ypos))
    t.left(90)
    t.pendown()
    t.forward(config.chip_height * 1e-3 * config.zoom_by)
    temp = t.pos()
    t.left(135)
    t.forward(arrow_height)
    t.setpos(temp)
    t.right(270)
    t.forward(arrow_height)
    t.penup()
    t.setpos(get_pos_from_chip_home(xpos, ypos))
    t.pendown()
    t.left(90)
    t.forward(arrow_height)
    t.penup()
    t.setpos(get_pos_from_chip_home(xpos, ypos))
    t.right(270)
    t.pendown()
    t.forward(arrow_height)
    t.right(135)  # reset
    t.penup()

    canvas = turtle.getcanvas()
    xpos = -45
    ypos = (config.chip_height * 1e-3 * config.zoom_by) / 2
    pos = get_pos_from_chip_home(xpos, ypos)
    canvas.create_text(pos[0],
                       pos[1],
                       text="Height {h} mm".format(h=config.chip_height),
                       angle=90,
                       font=(config.font, config.font_size,
                             config.font_weight))

    # draw width scale on top of the floor-plan
    xpos = 0
    ypos = (config.chip_height * 1e-3 * config.zoom_by) + 30
    t.penup()
    t.setpos(get_pos_from_chip_home(xpos, ypos))
    t.pendown()
    t.forward(config.chip_width * 1e-3 * config.zoom_by)
    temp = t.pos()
    t.left(135)
    t.forward(arrow_height)
    t.setpos(temp)
    t.right(270)
    t.forward(arrow_height)
    t.penup()
    t.setpos(get_pos_from_chip_home(xpos, ypos))
    t.pendown()
    t.left(90)
    t.forward(arrow_height)
    t.penup()
    t.setpos(get_pos_from_chip_home(xpos, ypos))
    t.right(270)
    t.pendown()
    t.forward(arrow_height)
    t.penup()

    canvas = turtle.getcanvas()
    xpos = (config.chip_width * 1e-3 * config.zoom_by) / 2
    ypos = -45
    print((xpos, ypos))
    pos = get_pos_from_chip_home(xpos, ypos)
    print(pos)
    canvas.create_text(pos[0],
                       pos[1],
                       text="Width {w} mm".format(w=config.chip_width),
                       angle=0,
                       font=(config.font, config.font_size,
                             config.font_weight))


# Color map for temperatures
def get_chip_temp_cmap():
    global colors
    colors.reverse()
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "chipTemp", colors)
    return cmap


def draw_unit(t,
              xpos,
              ypos,
              width,
              height,
              config,
              name,
              border_color="",
              fill_color="",
              hide_names=True):
    xpos *= config.zoom_by
    ypos *= config.zoom_by
    pos = get_pos_from_chip_home(xpos, ypos)
    xpos = pos[0]
    ypos = pos[1]
    width *= config.zoom_by
    height *= config.zoom_by
    t.penup()
    t.setpos(xpos, ypos)
    t.color(border_color, fill_color)
    if fill_color:
        t.begin_fill()
    t.pendown()
    t.forward(width)
    t.left(90)
    t.forward(height)
    t.left(90)
    t.forward(width)
    t.left(90)
    t.forward(height)
    t.left(90)
    if fill_color:
        t.end_fill()
    t.penup()

    if name and (hide_names == False):
        t.setpos(xpos + (width / 2), ypos + (height / 2))
        t.pendown()
        t.color("black")
        print_name = name
        if config.print_area:
            area = (width / config.zoom_by) * (height /
                                               config.zoom_by) * 1e6  # mm2
            area = round(area, 3)
            print_name += " ({a})".format(a=area)
        t.write(print_name,
                align="center",
                font=(config.font, config.font_size, config.font_weight))
        t.penup()


def draw_color_bar(t, config, colors, temp_min, temp_max):
    xpos = ((config.chip_width + 0.05) * 1e-3)
    ypos = 0
    color_bar_max_height = config.chip_height * 1e-3
    color_cell_width = color_bar_max_height / len(colors)
    color_cell_height = color_cell_width

    temp_cell_width = color_cell_width * 3
    temp_cell_height = color_cell_height

    interval = len(colors)
    temp_values = np.linspace(temp_min,
                              temp_max,
                              num=int(interval),
                              endpoint=True)
    temp_values = [round(val, 2) for val in temp_values]

    i = 0
    for color in colors:
        # draw the temperature value
        draw_unit(t,
                  xpos,
                  ypos,
                  temp_cell_width,
                  temp_cell_height,
                  config,
                  name="{f}K".format(f=temp_values[i]),
                  border_color="",
                  fill_color="",
                  hide_names=False)
        # color cell
        draw_unit(t,
                  xpos + temp_cell_width,
                  ypos,
                  color_cell_width,
                  color_cell_height,
                  config,
                  name="",
                  border_color="black",
                  fill_color=color)
        ypos += color_cell_height
        i += 1


# This parses the given temperature file and extracts
# 1) number of rows and columns (for grid steady file)
# 2) min and max temperatures (for steady and grid steady file)
def get_temperature_file_config(temperature_file):
    file = open(temperature_file, "r")
    lines = file.readlines()
    num_rows = 0
    num_cols = 0
    total_cols = 0

    temperatures = []
    for line in lines:
        if line == "\n":
            total_cols = num_cols
            num_rows += 1
            num_cols = 0
            continue
        line = line.split("\t")
        temperatures.append(float(line[1]))
        num_cols += 1

    file.close()

    grid_steady_config = []
    grid_steady_config.append(str(num_rows))
    grid_steady_config.append(str(total_cols))
    grid_steady_config.append(str(min(temperatures)))
    grid_steady_config.append(str(max(temperatures)))
    return grid_steady_config


def draw_grid_steady_thermal_map(config, turtle):
    start = time.time()

    # find min and max temperatures reported in grid steady file
    grid_steady_config = get_temperature_file_config(config.temperature_file)

    rows = int(grid_steady_config[0])
    cols = int(grid_steady_config[1])
    temp_min = float(grid_steady_config[2])
    temp_max = float(grid_steady_config[3])
    print(
        "{p} reading grid steady file {f}, found {r} rows, {c} cols, {min} min-temp, {max} max-temp"
        .format(p=msg_prefix,
                f=config.temperature_file,
                r=rows,
                c=cols,
                min=temp_min,
                max=temp_max))

    # normalize temperature range between 0 and 1, which will be used to fetch color from color map
    norm_temp_range = matplotlib.colors.Normalize(vmin=temp_min, vmax=temp_max)

    # generate color map
    cmap = get_chip_temp_cmap()

    global colors
    draw_color_bar(turtle, config, colors, temp_min, temp_max)

    grid_cell_width = (config.chip_width * 1e-3) / cols
    grid_cell_height = (config.chip_height * 1e-3) / rows

    file = open(config.temperature_file, "r")
    lines = file.readlines()

    xpos = 0
    ypos = (config.chip_height * 1e-3) - grid_cell_height
    print("{p} drawing temperature grid".format(p=msg_prefix))

    for line in lines:
        if line == "\n":
            xpos = 0
            ypos -= grid_cell_height
            # parsed one complete row
        else:
            line = line.split("\t")
            col = line[0]  # column number
            temp = float(
                line[1])  # temperature of the cell at current row and column

            color = matplotlib.colors.rgb2hex(cmap(norm_temp_range(temp)))
            draw_unit(turtle,
                      xpos,
                      ypos,
                      grid_cell_width,
                      grid_cell_height,
                      config,
                      name="",
                      border_color=color,
                      fill_color=color)
            xpos += grid_cell_width

    file.close()
    end = time.time()
    print("{p} finished drawing temperature grid in {t} seconds".format(
        p=msg_prefix, t=round((end - start), 2)))


def draw_steady_thermal_map(config, turtle):
    start = time.time()
    # find min and max temperatures reported in steady file
    steady_config = get_temperature_file_config(config.temperature_file)

    temp_min = float(steady_config[2])
    temp_max = float(steady_config[3])
    print("{p} reading steady file {f}, found {min} min-temp, {max} max-temp".
          format(p=msg_prefix,
                 f=config.temperature_file,
                 min=temp_min,
                 max=temp_max))

    # normalize temperature range between 0 and 1, which will be used to fetch color from color map
    norm_temp_range = matplotlib.colors.Normalize(vmin=temp_min, vmax=temp_max)

    # generate color map
    cmap = get_chip_temp_cmap()

    draw_color_bar(turtle, config, colors, temp_min, temp_max)

    # read all the floor-plan units
    file = open(config.floor_plan, "r")
    flp = file.readlines()
    flpUnits = []

    for line in flp:
        if "#" in line or line == "\n":
            continue
        line = line.split("\t")
        flpUnits.append(
            FlpUnit(line[0], float(line[1]), float(line[2]), float(line[3]),
                    float(line[4])))

    file.close()

    file = open(config.temperature_file, "r")
    lines = file.readlines()

    for line in lines:
        line = line.split("\t")
        name = line[0]
        temp = float(line[1])

        for unit in flpUnits:
            if unit.name == name:
                color = matplotlib.colors.rgb2hex(cmap(norm_temp_range(temp)))
                draw_unit(turtle,
                          unit.xpos,
                          unit.ypos,
                          unit.width,
                          unit.height,
                          config,
                          name=unit.name,
                          border_color="black",
                          fill_color=color,
                          hide_names=config.hide_names)

    file.close()
    end = time.time()
    print("{p} finished steady temperature map in {t} seconds".format(
        p=msg_prefix, t=round((end - start), 2)))


def draw_floorplan(config, t):
    start = time.time()
    file = open(config.floor_plan, "r")
    flp = file.readlines()
    flpUnits = []

    for line in flp:
        if "#" in line or line == "\n":
            continue
        line = line.split("\t")
        flpUnits.append(
            FlpUnit(line[0], float(line[1]), float(line[2]), float(line[3]),
                    float(line[4])))

    file.close()
    print("{p} drawing floor-plan".format(p=msg_prefix))
    print(
        "{p} reading floor-plan file {f}: found {u} units, {w}mm chip-width, {h}mm chip-height"
        .format(f=config.floor_plan,
                p=msg_prefix,
                u=len(flpUnits),
                w=config.chip_width,
                h=config.chip_height))

    for unit in flpUnits:
        draw_unit(turtle,
                  unit.xpos,
                  unit.ypos,
                  unit.width,
                  unit.height,
                  config,
                  name=unit.name,
                  border_color="black",
                  fill_color="",
                  hide_names=config.hide_names)

    end = time.time()
    print("{p} finished drawing floor-plan in {t} seconds".format(
        p=msg_prefix, t=round((end - start), 2)))


def parse_command_line():
    description = "A python based temperature (thermal) map generation tool for HotSpot-6.0 (http://lava.cs.virginia.edu/HotSpot/), Author: Gaurav Kothari (gkothar1@binghamton.edu)"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-a",
                        "--action",
                        action="store",
                        dest="action",
                        required=True,
                        choices=["flp", "steady", "grid-steady"],
                        help="Action type")
    parser.add_argument("-f",
                        "--flp",
                        action="store",
                        dest="floor_plan",
                        required=True,
                        help="Floor-plan file")
    parser.add_argument(
        "-t",
        "--temperature",
        action="store",
        dest="temperature_file",
        required=("steady" in argv) or ("grid-steady" in argv),
        help=
        "Steady temperature file or Grid steady temperature file based on action"
    )
    parser.add_argument("-cw",
                        "--chip-width",
                        action="store",
                        type=float,
                        dest="chip_width",
                        required=True,
                        help="Width of the chip (mm)")
    parser.add_argument("-ch",
                        "--chip-height",
                        action="store",
                        type=float,
                        dest="chip_height",
                        required=True,
                        help="Height of the chip (mm)")
    parser.add_argument("-ft",
                        "--font",
                        action="store",
                        dest="font",
                        required=False,
                        default="Ubuntu",
                        help="Font family")
    parser.add_argument("-fts",
                        "--font-size",
                        action="store",
                        dest="font_size",
                        required=False,
                        default=9,
                        type=int,
                        help="Font size")
    parser.add_argument("-ftw",
                        "--font-weight",
                        action="store",
                        dest="font_weight",
                        required=False,
                        default="normal",
                        help="Font weight")
    parser.add_argument("-o",
                        "--output-file",
                        action="store",
                        dest="output_file",
                        required=True,
                        help="Output file name prefix")
    parser.add_argument("-d",
                        "--output-directory",
                        action="store",
                        dest="output_dir",
                        required=False,
                        default=os.getcwd(),
                        help="Output directory")
    parser.add_argument("-hn",
                        "--hide-names",
                        action="store_true",
                        dest="hide_names",
                        required=False,
                        default=False,
                        help="Hide names on floor-plan")
    parser.add_argument("-z",
                        "--zoom-by",
                        action="store",
                        dest="zoom_by",
                        type=int,
                        required=False,
                        default=75000,
                        help="Zoom factor")
    parser.add_argument("-pcd",
                        "--print-chip-dim",
                        action="store_true",
                        dest="print_chip_dim",
                        required=False,
                        default=False,
                        help="Draw chip width and height scale")
    parser.add_argument(
        "-pa",
        "--print-area",
        action="store_true",
        dest="print_area",
        required=False,
        default=False,
        help=
        "Print unit's area (mm2) alongside its name, rounded to three decimal places"
    )
    args = parser.parse_args()
    print("{p} {d}".format(p=msg_prefix, d=description))
    return args


def main():
    config = parse_command_line()

    turtle = turtle_setup(config)
    if config.action == "flp":
        draw_floorplan(config, turtle)
    else:
        if config.action == "grid-steady":
            draw_grid_steady_thermal_map(config, turtle)
            # This will superimpose floor-plan onto temperature grid
            draw_floorplan(config, turtle)
        else:
            draw_steady_thermal_map(config, turtle)

    if config.print_chip_dim:
        draw_chip_dimensions(turtle, config)
    turtle_save_image(config)


if __name__ == "__main__":
    main()
