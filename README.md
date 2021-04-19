# HotSpotMap
A Python-based temperature (thermal) maps generation tool for HotSpot-6.0 (http://lava.cs.virginia.edu/HotSpot/)

This tool uses Python's Turtle library to generate publication-quality floor-plan images and thermal maps for 2D and 3D systems.

It can generate:
1) Floor-plan images (using floor-plan files)
2) Thermal maps (using floor-plan file and steady temperature file)
3) Fine-grained thermal maps (using floor-plan file and grid steady temperature file)

Generated images are in `.eps` and `.pdf` format.

If you are using this tool, please cite our GitHub link: https://github.com/bucaps/HotSpotMap

Please submit a pull request for any enhancements or contributions.

## Requirements
1) Python version `3.5`
2) Tkinter version `8.6`
3) `pdfjam`

## Setup
Clone the tool using:
```
git clone https://github.com/bucaps/HotSpotMap.git
```

## Examples
- `example-2d` folder in this repository contains a sample floor-plan (`ev6.flp`), steady temperature file (`gcc.steady`), and grid steady temperature file (`gcc.grid.steady`). 
- `example-3d` folder in this repository contains a example 3D system and the associated `lcf` (layer configuration file), floor-plan files and temperature files.

These files are also included in the `HotSpot-6.0` distribution at: https://github.com/uvahotspot/hotspot

## Usage: 2D systems

### To generate floor-plan image:

```
# This will generate ev6-flp.eps and ev6-flp.pdf in the example-2d directory
python3.5 HotSpotMap.py -a flp -f example-2d/ev6.flp -o ev6 -z 30000 -fts 7 -d example-2d -pcd
```

- `-a` : action {`flp` or `steady` or `grid-steady`}
- `-f` : path to the floor-plan file
- `-o` : prefix for output file
- `-z` : zoom level 
- `-fts` : font size
- `-d` : output directory
- `-pcd` : print chip's width and height

### To generate a thermal map using a steady temperature file:

```
# This will generate ev6-steady.eps and ev6-steady.pdf in the example-2d directory
python3.5 HotSpotMap.py -a steady -f example-2d/ev6.flp -t example-2d/gcc.steady -o ev6 -z 30000 -fts 7 -d example-2d
```

- `-t` : path to steady temperature file

### To generate a fine-grained thermal map using grid steady temperature file:

```
# This will generate ev6-grid-steady.eps and ev6-grid-steady.pdf in the example-2d directory
python3.5 HotSpotMap.py -a grid-steady -f example-2d/ev6.flp -t example-2d/gcc.grid.steady -r 64 -c 64 -o ev6 -z 30000 -fts 7 -d example-2d
```

- `-t` : path to grid steady temperature file

## Usage: 3D systems

### To generate floor-plan image:

```
# This will generate .eps and .pdf file for each layer in specified in the lcf, and combine them into a single pdf file `ev6-3D-concat.pdf`
python3.5 HotSpotMap.py -a flp -3D -f example-3d/ev6_3D.lcf -o ev6_3D -z 30000 -fts 7 -d example-3d -pcd -concat
```

- `-3D` : enable 3D system
- `-f` : path to the `lcf` file (layer configuration file)
- `-concat`: combines the floor-plans of all the layers into a single single pdf 

Using `-concat` will combine images of layers from `lcf` which have power dissipation.

### To generate a thermal map using a steady temperature file:

```
# This will generate ev6-steady.eps and ev6-steady.pdf in the example-2d directory
python3.5 HotSpotMap.py -a steady -3D -f example-3d/ev6_3D.lcf -t example-3d/ev6_3D.steady -o ev6_3D -z 30000 -fts 7 -d example-3d -pcd -concat
```

- `-t` : path to steady temperature file

### To generate a fine-grained thermal map using grid steady temperature file:

```
# This will generate ev6-grid-steady.eps and ev6-grid-steady.pdf in the example-2d directory
python3.5 HotSpotMap.py -a grid-steady -3D -f example-3d/ev6_3D.lcf -t example-3d/ev6_3D.grid.steady -r 64 -c 64 -o ev6_3D -z 30000 -fts 7 -d example-3d -pcd -concat
```
- `-t` : path to grid steady temperature file

#### Format of grid steady file for 3D systems
Grid temperatures of each layer should be followed by the layer number as shown below:

```
layer_0
0 341.14
1 341.18
2 341.24
3 341.32
...
...
```

This can be achieved by simplifying modifying `dump_top_layer_temp_grid()` function in `temperature_grid.c` file in `HotSpot 6.0` to print out grid temperatures for 
all the layers as follows:

```c
  int l;
  for(l=0;  l < model->n_layers; l++){
     fprintf(fp, "layer_%d\n", l);
     for(i=0; i < model->rows; i++){
         for(j=0; j < model->cols; j++){
             fprintf(fp, "%d\t%.2f\n", i*model->cols+j,
                     model->last_steady->cuboid[l][i][j]);
         }
         fprintf(fp, "\n");
     }
     fprintf(fp, "\n");
  }
```

### Important Note
- You can try out various levels of zoom `-z` and font-size `-fts` until you find a combination that suits your chip floor plan.
- For generating thermal maps using grid steady temperature file, you need to specify rows (`-r`) and columns (`-c`) used in the HotSpot's grid model.

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
  -3D, --model-3D       To indicate a 3D system
  -f FLOOR_PLAN, --flp FLOOR_PLAN
                        Floor-plan file
  -t TEMPERATURE_FILE, --temperature TEMPERATURE_FILE
                        Steady temperature file or Grid steady temperature
                        file based on action
  -r GRID_ROWS, --row GRID_ROWS
                        Number of rows in grid-steady model
  -c GRID_COLS, --col GRID_COLS
                        Number of columns in grid-steady model
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
                        Draw chip' width and height scale
  -concat, --concat-3D  Combines the images generated for all layer into a
                        single PDF
  -pa, --print-area     Print unit's area (mm2) alongside its name, rounded to
                        three decimal places
```

### License
This project is licensed under MIT License -  refer to the [LICENSE.md](LICENSE.md) file for details.

### Author
- Gaurav Kothari
- Email: gkothar1@binghamton.edu
