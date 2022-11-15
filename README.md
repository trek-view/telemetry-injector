# telemetry-injector

## Introduction

telemetry-injector takes a series of geotagged photos and creates a video with either CAMM or GPMD telemetry.

## How it works

We needed a way to upload to videos to the Google Street View API for our Trail Maker product.

Previously we uploaded videos alongside a gpx files as described in our blog; [Creating a Video File Ready to be Uploaded to the Google Street View API](https://www.trekview.org/blog/2022/create-google-street-view-video-publish-api/).

However, we wanted a way to inject telemetry into the video so that the video could be shared elsewhere, without the requirement to always share the GPX file alongside it.

Google Street View supports [CAMM](https://www.trekview.org/blog/2021/metadata-exif-xmp-360-video-files-camm-camera-motion-metadata-spec/) and [GPMD](https://www.trekview.org/blog/2020/metadata-exif-xmp-360-video-files-gopro-gpmd/) telemetry standards.

Therefore this script;

1. takes a series of geotagged images
2. parses out the telemetry into a gpx file
3. creates a camm / gpmd binary file from gpx
4. creates a video file from photos
5. injects the camm binary stream into the video

The specifics of how each step in this process works...

Karamvir TODO

## Installation

Download

```shell
git clone https://github.com/trek-view/telemetry-injector
cd telemetry-injector
```

Setup virtual environment

```shell
python3 -m venv telemetry-injector_venv
source c/bin/activate
```

Install required libraries

```shell
pip3 install -r requirements.txt
```

## Usage

```shell
python3 telemetry-injector.py -c -i INPUT_IMAGE_DIRECTORY/ -o OUTPUT_VIDEO_FILE.mp4
```

* `-g`: Flag to use gpmf metadata injection.
* `-c`: Flag to use camm metadata injection.
* `-i`: Input image directory.
* `-v`: Input mp4 files, should be mp4 video.
* `-x`: Input gpx files, should be mp4 video.
* `-o`: Output video file conataining metadata.

### Image Input

For `camm` images metadata injection
	
```shell
python3 telemetry-injector.py -c -i input_image_directory -o OUTPUT_VIDEO_FILE.mp4
```

For `gpmf` images metadata injection

```shell
python3 telemetry-injector.py -g -i input_image_directory -o OUTPUT_VIDEO_FILE.mp4
```


### Video Input

For `camm` video metadata injection
	
```shell
python3 telemetry-injector.py -c -v input_mp4_video_file -x input_gpx_file -o output_mp4_video_file
```

For `gpmf` video metadata injection

```shell
python telemetry-injector.py -g -v input_mp4_video_file -x input_gpx_file -o output_mp4_video_file
```


