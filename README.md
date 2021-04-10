# HotSpotMap
A Python-based temperature (thermal) maps generation tool for HotSpot-6.0 (http://lava.cs.virginia.edu/HotSpot/)

This tool uses Python's Turtle library to generate publication-quality:
1) Floor-plan images (using floor-plan files)
2) Thermal maps (using floor-plan file and steady temperature file)
3) Fine-grained thermal maps (using floor-plan file and grid steady temperature file)

Generated images are in `.eps` and `.pdf` format.

If you are using this tool, please cite our GitHub link: https://github.com/bucaps/HotSpotMap

Please submit a pull request for any enhancements or contributions.

## Requirements
1) Python version `3.5`
2) Tkinter version `8.6`

## Setup
Clone the tool using:
```
git clone https://github.com/bucaps/HotSpotMap.git
```

## Usage
`example-2d` folder in this repository contains a sample floor-plan (`ev6.flp`), steady temperature file (`gcc.steady`), and grid steady temperature file (`gcc.grid.steady`). These files are also included in the `HotSpot-6.0` distribution at: https://github.com/uvahotspot/hotspot

### To generate floor-plan image:

```
# This will generate ev6-flp.eps and ev6-flp.pdf in the example-2d directory
python3.5 HotSpotMap.py -a flp -f example-2d/ev6.flp -cw 16 -ch 16 -o ev6 -z 30000 -fts 7 -d example-2d -pcd
```

- `-a` : action {`flp` or `steady` or `grid-steady`}
- `-cw`: width of chip in `mm`
- `-ch`: height of chip in `mm`
- `-o` : prefix for output file
- `-z` : zoom level 
- `-fts` : font size
- `-d` : output directory
- `-pcd` : print chip's width and height

### To generate a thermal map using a steady temperature file:

```
# This will generate ev6-steady.eps and ev6-steady.pdf in the example-2d directory
python3.5 HotSpotMap.py -a steady -f example-2d/ev6.flp -t example-2d/gcc.steady -cw 16 -ch 16 -o ev6 -z 30000 -fts 7 -d example-2d
```

- `-t` : path to steady temperature file

### To generate a fine-grained thermal map using grid steady temperature file:

```
# This will generate ev6-grid-steady.eps and ev6-grid-steady.pdf in the example-2d directory
python3.5 HotSpotMap.py -a grid-steady -f example-2d/ev6.flp -t example-2d/gcc.grid.steady -cw 16 -ch 16 -o ev6 -z 30000 -fts 7 -d example-2d
```

- `-t` : path to grid steady temperature file

### Important Note
You can try out various levels of zoom `-z` and font-size `-fts` until you find a combination that suits your chip floor plan.

### Full list of options
To get a complete list of available options, type:
```
python3.5 HotSpotMap.py -h
```

Currently, supported options are:
```
  -h, --help            show this help message and exit
  -a {flp,steady,grid-steady}, --action {flp,steady,grid-steady}
                        Action type
  -f FLOOR_PLAN, --flp FLOOR_PLAN
                        Floor-plan file
  -t TEMPERATURE_FILE, --temperature TEMPERATURE_FILE
                        Steady temperature file or Grid steady temperature
                        file based on action
  -cw CHIP_WIDTH, --chip-width CHIP_WIDTH
                        Width of the chip (mm)
  -ch CHIP_HEIGHT, --chip-height CHIP_HEIGHT
                        Height of the chip (mm)
  -ft FONT, --font FONT
                        Font family
  -fts FONT_SIZE, --font-size FONT_SIZE
                        Font size
  -ftw FONT_WEIGHT, --font-weight FONT_WEIGHT
                        Font weight
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output file name prefix
  -d OUTPUT_DIR, --output-directory OUTPUT_DIR
                        Output directory
  -hn, --hide-names     Hide names on floor-plan
  -z ZOOM_BY, --zoom-by ZOOM_BY
                        Zoom factor
  -pcd, --print-chip-dim
                        Draw chip width and height scale
  -pa, --print-area     Print unit's area alongside its name

```

### License
This project is licensed under MIT License -  refer to the [LICENSE.md](LICENSE.md) file for details.

### Author
Gaurav Kothari
Email: gkothar1@binghamton.edu
