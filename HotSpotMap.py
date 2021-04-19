# HotSpotMap: A python based temperature (thermal) map generation
# tool for HotSpot-6.0 (http://lava.cs.virginia.edu/HotSpot/)
# This tool uses python's turtle library
#
# Author: Gaurav Kothari (gkothar1@binghamton.edu) Copyright 2021
#
# This tool generates:
# 1) Floor-plan image (using floor-plan file)
# 2) Thermal map (using floor-plan file and steady temperature file)
# 3) Fine grained thermal map (using floor-plan file and grid steady temperature file)
#
# Supports 2D and 3D stacked systems
# Supports output formats: '.eps' and '.pdf'
import os
import time
import subprocess
import tkinter
import turtle
import tempfile
import numpy as np
import matplotlib
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import argparse
from sys import argv


# To represent each floor-plan unit
class FloorplanUnit():
    def __init__(self, name, width, height, xpos, ypos, temp=0):
        self.name = name
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.temp = temp  # temperature


msg_prefix = "  HotSpotMap:"

# Home co-ordinates for drawing the chip floor-plan
# Note: turtle's default home co-ordinates are (0,0)
# For drawing the floor-plan, we will start from (-w/2,-h/2), where
# w = width of the chip, h = height of the chip
chip_home_xpos = 0
chip_home_ypos = 0


# Inspired from HotSpot 6.0
def get_chip_width(flp_units):
    min_x = flp_units[0].xpos
    max_x = flp_units[0].xpos + flp_units[0].width

    for i in range(1, len(flp_units)):
        if flp_units[i].xpos < min_x:
            min_x = flp_units[i].xpos
        if (flp_units[i].xpos + flp_units[i].width) > max_x:
            max_x = flp_units[i].xpos + flp_units[i].width

    return (max_x - min_x) * 1e3


# Inspired from HotSpot 6.0
def get_chip_height(flp_units):
    min_y = flp_units[0].ypos
    max_y = flp_units[0].ypos + flp_units[0].height

    for i in range(1, len(flp_units)):
        if flp_units[i].ypos < min_y:
            min_y = flp_units[i].ypos
        if (flp_units[i].ypos + flp_units[i].height) > max_y:
            max_y = flp_units[i].ypos + flp_units[i].height

    return (max_y - min_y) * 1e3


def get_pos_from_chip_home(xpos, ypos):
    return (chip_home_xpos + xpos, chip_home_ypos + ypos)


# Only for 3D systems, collect all the output files
# (for every layer) to combine them later as a single PDF
output_3d_files = []


#
# Functions related to Turtle
#
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
    t.pensize(0.5)
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
    print("{p} Generated eps file: {f}".format(p=msg_prefix, f=eps_file))
    cmd = "ps2pdf {i} {o}".format(i=eps_file, o=pdf_file)
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    print("{p} Generated pdf file: {f}".format(p=msg_prefix, f=pdf_file))

    if config.model_3d:
        output_3d_files.append(pdf_file)


def turtle_draw_unit(t,
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


def draw_chip_dimensions(t, config):
    # draw height scale on left of the floor-plan
    arrow_height = 15
    xpos = -30
    ypos = 0
    t.penup()
    t.color("black")
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
    pos = get_pos_from_chip_home(xpos, ypos)
    canvas.create_text(pos[0],
                       pos[1],
                       text="Width {w} mm".format(w=config.chip_width),
                       angle=0,
                       font=(config.font, config.font_size,
                             config.font_weight))


#
# Function related to temperature color bar
#

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


# Color map for temperatures
def get_chip_temp_cmap():
    global colors
    colors.reverse()
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "chipTemp", colors)
    return cmap


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
        turtle_draw_unit(t,
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
        turtle_draw_unit(t,
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


#
# Functions related to drawing chip floor-plan
#


# Checks if floor-plan has duplicated units
def check_duplicated_flp_units(flp_units_names):
    flp_units_namesSet = set(flp_units_names)

    if len(flp_units_namesSet) != len(flp_units_names):
        print("{p} warning! duplicated floor-plan units detected".format(
            p=msg_prefix))


def draw_floorplan(config, t):
    start = time.time()
    file = open(config.floor_plan, "r")
    flp = file.readlines()
    flp_units = []
    flp_units_names = []

    for line in flp:
        if "#" in line or line == "\n" or not line:
            continue
        line = line.split("\t")
        flp_units_names.append(line[0])
        flp_units.append(
            FloorplanUnit(line[0], float(line[1]), float(line[2]),
                          float(line[3]), float(line[4])))

    check_duplicated_flp_units(flp_units_names)

    print("{p} Drawing floor-plan".format(p=msg_prefix))
    print(
        "{p} Reading floor-plan file {f}: found {u} units, {w} mm chip-width, {h} mm chip-height"
        .format(f=config.floor_plan,
                p=msg_prefix,
                u=len(flp_units),
                w=config.chip_width,
                h=config.chip_height))

    file.close()

    for unit in flp_units:
        turtle_draw_unit(turtle,
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
    print("{p} Finished drawing floor-plan in {t} seconds".format(
        p=msg_prefix, t=round((end - start), 2)))


#
# Functions related to draw the temperature maps
#


# This parses the given temperature file and extracts
# min and max temperatures (for steady and grid steady file)
def get_temperature_file_config(temperature_file, grid_steady_file_3d=""):
    file = open(temperature_file, "r")
    lines = file.readlines()

    temperatures = []
    for line in lines:
        if line == "\n" or not line:
            continue
        line = line.split("\t")
        if len(line) == 1:
            continue  # for 3D grid steady file, skip layer header
        temperatures.append(float(line[1]))

    file.close()

    grid_steady_config = []
    grid_steady_config.append(str(min(temperatures)))
    grid_steady_config.append(str(max(temperatures)))
    return grid_steady_config


def draw_grid_steady_thermal_map(config, turtle, grid_steady_file_3d=""):
    start = time.time()

    temperature_limit_file = config.temperature_file

    if config.model_3d:
        # for 3D systems, use the original grid-steady file containing
        # the temperature data for all the layers to extract min and max
        # temperatures, because all the layers must use the same color range
        temperature_limit_file = grid_steady_file_3d

    # find min and max temperatures reported in grid steady file
    grid_steady_config = get_temperature_file_config(temperature_limit_file)

    rows = config.grid_rows
    cols = config.grid_cols
    temp_min = float(grid_steady_config[0])
    temp_max = float(grid_steady_config[1])
    print(
        "{p} Reading grid steady file {f}, with {r} rows, {c} cols, {min} min-temp, {max} max-temp"
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
    print("{p} Drawing temperature grid".format(p=msg_prefix))

    next_col = 0
    for line in lines:
        if line == "\n" or not line:
            continue
        else:
            line = line.split("\t")
            col = line[0]  # column number
            temp = float(
                line[1])  # temperature of the cell at current row and column

            color = matplotlib.colors.rgb2hex(cmap(norm_temp_range(temp)))
            turtle_draw_unit(turtle,
                             xpos,
                             ypos,
                             grid_cell_width,
                             grid_cell_height,
                             config,
                             name="",
                             border_color=color,
                             fill_color=color)
            xpos += grid_cell_width
            next_col += 1

            if next_col == config.grid_cols:
                # one complete row is finished
                xpos = 0
                next_col = 0
                ypos -= grid_cell_height

    file.close()
    end = time.time()
    print("{p} Finished drawing temperature grid in {t} seconds".format(
        p=msg_prefix, t=round((end - start), 2)))


def draw_steady_thermal_map(config, turtle):
    start = time.time()
    # find min and max temperatures reported in steady file
    steady_config = get_temperature_file_config(config.temperature_file)

    temp_min = float(steady_config[0])
    temp_max = float(steady_config[1])
    print("{p} Reading steady file {f}, found {min} min-temp, {max} max-temp".
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
    flp_units = []

    for line in flp:
        if "#" in line or line == "\n":
            continue
        line = line.split("\t")
        flp_units.append(
            FloorplanUnit(line[0], float(line[1]), float(line[2]),
                          float(line[3]), float(line[4])))

    file.close()

    file = open(config.temperature_file, "r")
    lines = file.readlines()

    for line in lines:
        line = line.split("\t")
        name = line[0]
        temp = float(line[1])

        # for 3D steady temperature file, each unit is appended with prefix layer_<layer>_
        # we need to remove that prefix
        if config.model_3d and "layer_" in name:
            name = name[name.find("_") + 1:]
            name = name[name.find("_") + 1:]

        for unit in flp_units:
            if unit.name == name:
                color = matplotlib.colors.rgb2hex(cmap(norm_temp_range(temp)))
                turtle_draw_unit(turtle,
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
    print("{p} Finished steady temperature map in {t} seconds".format(
        p=msg_prefix, t=round((end - start), 2)))


#
# Function related to parse file for 3D system (such as LCF and grid-steady file)
#


# Parse HotSpot's layer configuration file (lcf) for 3D systems
# For 3D systems, config.floor_plan is the lCF
def read_lcf(config):
    file = open(config.floor_plan, "r")
    lines = file.readlines()

    config_lines = [
    ]  # To store lcf after removing all the comments and blank lines

    for line in lines:
        if "#" in line or not line or line == "\n":
            continue
        config_lines.append(line)

    file.close()

    layer_num_pos = 0  # pos of layer number for the corresponding layer
    has_power_pos = 2  # pos of power dissipation flag  for the corresponding layer
    floor_plan_file_pos = 6  # pos of floor plan file for the corresponding layer

    current_line = 0
    current_layer = []

    lcf_home_dir = os.path.dirname(config.floor_plan)
    lcf_breakdown_list = []

    while current_line < len(config_lines):
        if current_line and ((current_line % 7) == 0):
            temp = []
            temp.append(current_layer[layer_num_pos].rstrip())
            temp.append(current_layer[has_power_pos].rstrip())
            temp.append(
                os.path.join(lcf_home_dir,
                             current_layer[floor_plan_file_pos].rstrip()))
            lcf_breakdown_list.append(temp)
            current_layer.clear()

        current_layer.append(config_lines[current_line])
        current_line += 1

    print("{p} Finished reading lcf file: {f}, found {flp} floor-plan files".
          format(p=msg_prefix,
                 f=config.floor_plan,
                 flp=len(lcf_breakdown_list)))

    return lcf_breakdown_list


def extract_grid_temperatures_for_layer(config, temperature_file, layer):
    file = open(temperature_file, "r")
    lines = file.readlines()
    file.close()

    # remove all the empty lines
    cleaned_lines = []
    for line in lines:
        if line == "\n" or not line:
            continue
        cleaned_lines.append(line)

    line_num = 0
    look_for_layer = "layer_{l}".format(l=layer)

    while cleaned_lines[line_num].rstrip() != look_for_layer:
        line_num += 1

    print(
        "{p} Grid temperature data for layer {l} starts at line {n} in file: {f}"
        .format(p=msg_prefix, l=layer, n=line_num, f=temperature_file))

    # grid temperatures for current layer start at line_num
    line_num += 1  # skip the header line for this layer
    file = open("temp.grid.steady", "w")

    # we will read grid_rows x grid_cols line from this line onwards
    lines_read = line_num
    lines_to_read = line_num + (config.grid_rows * config.grid_cols)

    while lines_read < lines_to_read:
        current_line = cleaned_lines[lines_read]
        file.write("{l}\n".format(l=current_line.rstrip()))
        lines_read += 1

    file.close()


# For 2D systems
def main_2d(config):
    turtle = turtle_setup(config)
    if config.action == "flp":
        draw_floorplan(config, turtle)
    else:
        if config.action == "grid-steady":
            draw_grid_steady_thermal_map(config, turtle)
            draw_floorplan(
                config, turtle
            )  # This will superimpose floor-plan onto temperature grid
        else:
            draw_steady_thermal_map(config, turtle)

    if config.print_chip_dim:
        draw_chip_dimensions(turtle, config)
    turtle_save_image(config)


# For 3D stacked systems
def main_3d(config):
    lcf_breakdown_list = read_lcf(config)

    output_file_bkp = config.output_file
    temperature_file_bkp = config.temperature_file

    for lcf_layer in lcf_breakdown_list:
        layer = int(lcf_layer[0])  # layer number

        # override the config parameters
        config.floor_plan = lcf_layer[2]
        config.output_file = output_file_bkp
        config.output_file += "-layer-{l}".format(l=layer)

        turtle = turtle_setup(config)

        print("{s} Processing layer {l} with floor-plan: {f}".format(
            s=msg_prefix, l=layer, f=config.floor_plan))

        if config.action == "flp":
            draw_floorplan(config, turtle)
        else:
            if config.action == "grid-steady":
                extract_grid_temperatures_for_layer(config,
                                                    temperature_file_bkp,
                                                    layer)

                # this file has extracted grid temperatures for current layer
                config.temperature_file = "temp.grid.steady"
                draw_grid_steady_thermal_map(config, turtle,
                                             temperature_file_bkp)
                draw_floorplan(
                    config, turtle
                )  # this will superimpose floor-plan onto temperature grid
                os.remove("temp.grid.steady")
            else:
                draw_steady_thermal_map(config, turtle)

        if config.print_chip_dim:
            draw_chip_dimensions(turtle, config)


        turtle_save_image(config)

        print("")

    if config.concat:
        # this code block combines all the files
        # generated for each layer into a single PDF
        output_file_list_str = ""

        for file in output_3d_files:
            output_file_list_str += "{f} ".format(f=file)

        final_concat_output = os.path.join(
            config.output_dir, "{p}-{a}-concat.pdf".format(p=output_file_bkp,a=config.action))

        pdfjam = "pdfjam --nup {n}x1 --landscape {files} -o {output}".format(
            n=len(output_3d_files),
            files=output_file_list_str,
            output=final_concat_output)

        print("{p} Executing {c}".format(p=msg_prefix, c=pdfjam))
        process = subprocess.Popen(pdfjam, shell=True)
        process.wait()
        stdout, stderr = process.communicate()

        if stdout:
            print(stdout)

        if stderr:
            print(stderr)


def setup_chip_dimensions(config):
    floor_plan_file = config.floor_plan

    if config.model_3d:
        lcf_breakdown_list = read_lcf(config)
        # index 0 in lcf_breakdown_list is the 1st layer in 3D system
        # index 2 in 1st layer is the floor-plan file for that layer
        # for stacked 3D system, all layers must have equal dimensions, so pick any 1 layer
        floor_plan_file = lcf_breakdown_list[0][2]

    file = open(floor_plan_file, "r")
    flp = file.readlines()
    flp_units = []
    file.close()

    for line in flp:
        if "#" in line or line == "\n" or not line:
            continue
        line = line.split("\t")
        flp_units.append(
            FloorplanUnit(line[0], float(line[1]), float(line[2]),
                          float(line[3]), float(line[4])))

    config.chip_height = round(get_chip_height(flp_units), 5)
    config.chip_width = round(get_chip_width(flp_units), 5)

    print("{p} Calculated chip's width as {w} mm and chip's height as {h} mm".
          format(p=msg_prefix, w=config.chip_width, h=config.chip_height))


def parse_command_line():
    version = 2.0
    description = "A python based temperature (thermal) map generation tool for HotSpot-6.0 (http://lava.cs.virginia.edu/HotSpot/), Author: Gaurav Kothari (gkothar1@binghamton.edu) v{v}".format(
        v=version)
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-a",
                        "--action",
                        action="store",
                        dest="action",
                        required=True,
                        choices=["flp", "steady", "grid-steady"],
                        help="Action type")
    parser.add_argument("-3D",
                        "--model-3D",
                        action="store_true",
                        dest="model_3d",
                        required=False,
                        default=False,
                        help="To indicate a 3D system")
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
    parser.add_argument("-r",
                        "--row",
                        action="store",
                        dest="grid_rows",
                        type=int,
                        required=("grid-steady" in argv),
                        help="Number of rows in grid-steady model")
    parser.add_argument("-c",
                        "--col",
                        action="store",
                        dest="grid_cols",
                        type=int,
                        required=("grid-steady" in argv),
                        help="Number of columns in grid-steady model")
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
                        help="Draw chip' width and height scale")
    parser.add_argument("-concat",
                        "--concat-3D",
                        action="store_true",
                        dest="concat",
                        required=False,
                        default=False,
                        help="Combines the images generated for all layer into a single PDF")
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
    print("")
    return args


def main():
    config = parse_command_line()

    # before we start drawing images, first quickly read floor-plan file
    # and calculate the chip's width and height
    setup_chip_dimensions(config)

    if config.model_3d:
        main_3d(config)
    else:
        main_2d(config)


if __name__ == "__main__":
    main()
