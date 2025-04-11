## tilefetcher
Utilities to help with retrieving tiles

### Dependencies 
* [python 3](https://www.python.org/)
* [vt2geojson](https://github.com/mapbox/vt2geojson) npm install -g @mapbox/vt2geojson
* [geojson2ndjson](https://github.com/stevage/geojson2ndjson) npm install -g geojson2ndjson

### Examples
Fetch all vector tiles at zoom level 16 from (34859, 22736), (34860, 22737) and store them under the subdirectory `output`:
```
python tilefetcher.py -xs 34859 -xe 34860 -ys 22736 -ye 22737 -z 16 -f "vector.pbf" -t ${MAPBOX_ACCESS_TOKEN} -ep https://api.mapbox.com/v4/mapbox.mapbox-streets-v6 -o output/
```

Fetch all satellite tiles at zoom level 15 that overlap a geographic region defined by a 
bounding box with a north west corner at (48.14627, 11.5638) and a south east corner at
(48.13585, 11.58654) and store them under the subdirectory `output`:
```
python tilefetcher.py -xs 11.5638 -xe 11.58654 -ys 48.14627 -ye 48.13585 -z 15 -f "png32" -t ${MAPBOX_ACCESS_TOKEN} -ep https://api.mapbox.com/v4/mapbox.satellite/ -o output/ -ull -ts 256
```



