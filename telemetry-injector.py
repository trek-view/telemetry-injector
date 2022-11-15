import os,re, sys, argparse
from pathlib import Path 

path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)

from metadata.metadata import write_metadata, create_video_from_images

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

    parser.add_argument("-i", "--images-directory", help="image directory to make video file from.")

    parser.add_argument("-x", "--gpx", help="gpx file")

    parser.add_argument("-o", "--output", help="output file")

    args = parser.parse_args()

    framerate = 5

    if args.inject_camm_metadata or args.inject_gpmd_metadata:
        metadata = b''
        if args.inject_camm_metadata:
            metadata = b'camm'
        if args.inject_gpmd_metadata:
            metadata = b'gpmd'
        if args.images_directory and args.output:
            images_directory = Path(args.images_directory)
            output_vid = Path(args.output).absolute()
            output_dir = output_vid.parent
            if (images_directory.is_dir() is not True):
                print('Please provide a valid images directory')
                exit()
            if (output_dir.is_dir()  is not True):
                print('Please provide a valid output directory')
                exit()
            if output_vid.is_file() or output_vid.is_dir():
                print('Output file already exists.')
                exit()
            if (output_vid.suffix.lower() != '.mp4'):
                print('Output file should be a mp4.')
                exit()
            print('Creating video in {} directory'.format(output_dir))
            o_vid = str(output_vid.name)
            create_video_from_images(images_directory, output_dir, output_vid, o_vid, framerate, metadata)
        elif args.video and args.gpx and args.output:
            video = Path(args.video)
            gpx = Path(args.gpx)
            output = Path(args.output)
            if (video.is_file() is not True):
                print('Please provide a valid input mp4 file')
                exit()
            if (gpx.is_file() is not True):
                print('Please provide a valid gpx file')
                exit()
            if (video.suffix.lower() != '.mp4'):
                print('Please provide a valid input mp4 file')
                exit()
            if (gpx.suffix.lower() != '.gpx'):
                print('Please provide a valid gpx file')
                exit()
            if (output.suffix.lower() != '.mp4'):
                print('Output file should be a mp4 file')
                exit()
            write_metadata(video, gpx, output, framerate, metadata)
        else:
            parser.print_help()
            exit()
    else:
        parser.print_help()
        exit()


if __name__ == "__main__":
    main()

