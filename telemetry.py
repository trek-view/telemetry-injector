import os,re, sys, argparse
from pathlib import Path 

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)

from metadata.metadata import write_metadata

def main():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [options] [files]\n"
    )
    parser.add_argument(
        "-c",
        "--inject-camm-metadata",
        action="store_true",
        help=
        "injects camm metadata into the first file specified (.mp4 or "
        ".mov) and saves the result to the second file specified")
        
    parser.add_argument(
        "-g",
        "--inject-gpmd-metadata",
        action="store_true",
        help=
        "injects gopro metadata into the first file specified (.mp4 or "
        ".mov) and saves the result to the second file specified")

    parser.add_argument("-v", "--video", help="video file")

    parser.add_argument("-x", "--gpx", help="gpx file")

    parser.add_argument("-o", "--output", help="output file")

    args = parser.parse_args()

    if args.inject_camm_metadata or args.inject_gpmd_metadata:
        if args.video and args.gpx and args.output:
            video = Path(args.video)
            gpx = Path(args.gpx)
            output = Path(args.output)
            if (video.is_file() is not True):
                print('Please provide a valid mp4 file')
                exit()
            if (gpx.is_file() is not True):
                print('Please provide a valid gpx file')
                exit()
            """if (output.is_file() is True):
                print('Please provide a valid output mp4 file')
                exit()"""
            if (video.suffix.lower() != '.mp4'):
                print('Please provide a valid mp4 file')
                exit()
            if (gpx.suffix.lower() != '.gpx'):
                print('Please provide a valid gpx file')
                exit()
            if (output.suffix.lower() != '.mp4'):
                print('Please provide a valid mp4 file')
                exit()
            metadata = b''
            if args.inject_camm_metadata:
                metadata = b'camm'
            if args.inject_gpmd_metadata:
                metadata = b'gpmd'
            write_metadata(video, gpx, output, metadata)
        else:
            parser.print_help()
            exit()
    else:
        parser.print_help()
        exit()


if __name__ == "__main__":
    main()

