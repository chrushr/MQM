# MQM

OpenStreetMap (OSM) data quality is always a concern and frequently a barrier for use when compared to propriety data. Inspired by other OSM mapping projects, the Map Quality Measurement initiative intends to visualize map quality with a heat-map approach by summarizing map error indicators within relevant grids. We are not simply indicating areas that are missing map quality, we are providing insight for prioritization by overlapping social-economic metrics (e.g., population density, road density, etc.) to enable people-first decision-making when deciding where to work on improving map quality and function. The Map Quality Measure (MQM) is a heat-map style representation showing the map quality for a given geographic unit. To make MQM informative, the size and value of each unit used to summarize quality is sensitive to local context. Our project is developing an automated process to find the optimal heat-map grid size and update in response to an update trigger on demand.

# Usage
**Package Installation:** <br />
1. numpy
2. matplotlib
3. Python3
4. area (link: https://github.com/scisco/area)

**To run the program successifully, please follow steps:** <br />
1. create an arbitrary directory storing all sub-directories in the working directory, and put all input sub-directories into it. <br />

2. change a permission of the **test_script.sh** file by using command `chmod +x test_script.sh`. <br />

3. run the program through applying <br />

```
./test_script.sh [name of the arbitrary directory] [a level number]

For example:
./test_script.sh test_data 3
```

Note: <br />
Users can adjust the second and last parameter, and minimum value of the level number is 0. <br />
Value 0 represents that tree depth of a k-d tree is 1. <br />

**Output Format:** <br />
The output format of this program is also a geojson format that includes coordinates of all grids <br />
and the number of counts.

**Result:** <br />
The program yields two types of results: histograms and geojson files.
