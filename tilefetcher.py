import math
import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-xs", "--x_start", help="Starting X coordinate of the tile or longitude"
                                             "of the bounding box if -ull option is used.", type=float, default=0)
parser.add_argument("-xe", "--x_end", help="Ending X coordinate of the tile or longitude"
                                           "of the bounding box if -ull option is used.", type=float, default=0)
parser.add_argument("-ys", "--y_start", help="Starting Y coordinate of the tile or latitude"
                                             "of the bounding box if the -ull option is used", type=float, default=0)
parser.add_argument("-ye", "--y_end", help="Ending Y coordinate of the tile or latitude"
                                           "of the bounding box if the -ull option is used", type=float, default=0)
parser.add_argument("-z", "--zoom", help="Z coordinate of the tile", type=int, default=1)
parser.add_argument("-ts", "--tile_size", help="Size of the tile in pixels", type=int, default=512)
parser.add_argument("-ull", "--use_lat_lon", help="Use a lat/lon pair describing a bounding box to calculate"
                                                  "the overlapping tiles.", action=argparse.BooleanOptionalAction)
parser.add_argument("-o", "--output", help="Output director", type=str, default="./")
parser.add_argument("-ep", "--end_point", help="URL for the tile set", type=str, required=1)
parser.add_argument("-f", "--format",
                    help="Format of the tile set, e.g vector.pbf for vector tiles or png32 satellite tiles", type=str,
                    required=1)
parser.add_argument("-t", "--token", help="Mapbox access token", type=str, required=1)
parser.add_argument("-ag", "--as_geojson", help="Output as geojson files. Only for vector tiles",
                    action=argparse.BooleanOptionalAction)
parser.add_argument("-ld", "--line_delimited", help="Output as line delimited. Effective when --as_geojson is set.",
                    action=argparse.BooleanOptionalAction)
parser.add_argument("-v", "--verbose", help="Verbose logging", action=argparse.BooleanOptionalAction)
parser.set_defaults(feature=True)
args = parser.parse_args()


def get_tile(x, y, z):
    print(f"Fetching tile {z}/{x}/{y}")

    url = os.path.join(args.end_point, f"{z}/{x}/{y}." + args.format + "?access_token=" + args.token)
    output_name = os.path.join(args.output, f"{z}-{x}-{y}." + args.format)

    try:
        # Fetch the tiles
        if args.as_geojson and args.format == "vector.pbf":
            geojson_output = os.path.join(args.output, f"{z}-{x}-{y}.geojson")
            vt2geojson_command = f"vt2geojson -z {z} -x {x} -y {y} {url} > {geojson_output}"
            subprocess.run(vt2geojson_command, shell=True, check=True)
            if args.line_delimited:
                delimited_geojson_output = os.path.join(args.output, f"{z}-{x}-{y}.txt")
                geojson2ndjson_and_rm_command = f"geojson2ndjson {geojson_output} > {delimited_geojson_output} && rm {geojson_output}"
                subprocess.run(geojson2ndjson_and_rm_command, shell=True, check=True)
        else:
            output_tar = os.path.join(args.output, f"{z}-{x}-{y}.tar.gz" if args.format == "vector.pbf" else f"{z}-{x}-{y}." + args.format)
            curl_command = f"curl \"{url}\" -o {output_tar}" + (" -v" if args.verbose else "")
            subprocess.run(curl_command, shell=True, check=True)
            if args.format == "vector.pbf":
                if os.path.exists(output_tar):
                    gunzip_and_rm_command = f"gunzip -c {output_tar} > {output_name} && rm {output_tar}"
                    subprocess.run(gunzip_and_rm_command, shell=True, check=True)
                else:
                    print(f"Failed to download tile {output_name}.")
    except subprocess.CalledProcessError:
        print(f"Errors occurred during download or processing of tile {z}-{x}-{y}.")


def get_tile_id(lat, lon, zoom):
    lat = min(max(lat, -85.051128779806604), 85.051128779806604)
    world_size = args.tile_size * math.pow(2, zoom)
    mercator_x = (lon + 180.0) / 360.0
    mercator_y = (180.0 - (180.0 / math.pi * math.log(math.tan(math.pi / 4.0 + lat * math.pi / 360.0)))) / 360.0
    x = math.floor(math.floor(mercator_x * world_size) / args.tile_size)
    y = math.floor(math.floor(mercator_y * world_size) / args.tile_size)
    return int(x), int(y)


def get_tile_ids():
    x_start, y_start = get_tile_id(args.y_start, args.x_start, args.zoom)
    x_end, y_end = get_tile_id(args.y_end, args.x_end, args.zoom)
    if x_end < x_start or y_end < y_start:
        print(f"Incorrect lat/lon provided for the bounding region, only the tile containing"
              f"the first lat/lon {y_start, x_start} will be fetched.")
        return range(x_start, x_start + 1), range(y_start, y_start + 1)
    return range(x_start, x_end), range(y_start, y_end)


if __name__ == "__main__":
    x_range = range(int(args.x_start), int(args.x_end) + 1)
    y_range = range(int(args.y_start), int(args.y_end) + 1)

    if args.use_lat_lon:
        ranges = get_tile_ids()
        x_range = ranges[0]
        y_range = ranges[1]

    for a in x_range:
        for b in y_range:
            get_tile(a, b, args.zoom)
