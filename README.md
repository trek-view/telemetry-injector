# 0. Introduction

Camera metadata tool provides the ability to add metadata to a mp4 file.

# 1. Usage

For `camm` video metadata injection
	
```
	$ python telemetry.py -c -v input_mp4_video_file -x input_gpx_file -o output_mp4_video_file
```

For `gpmf` video metadata injection

```
	$ python telemetry.py -g -v input_mp4_video_file -x input_gpx_file -o output_mp4_video_file
```

For `camm` images metadata injection
	
```
	$ python telemetry.py -c -i input_image_directory -o output_mp4_video_file
```

For `gpmf` images metadata injection

```
	$ python telemetry.py -g -i input_image_directory -o output_mp4_video_file
```

# 1.1 Input Parameters

`-g`: Flag to use gpmf metadata injection.

`-c`: Flag to use camm metadata injection.

`-i`: Input image directory.

`-v`: Input mp4 files, should be mp4 video.

`-x`: Input gpx files, should be mp4 video.

`-o`: Output video file conataining metadata.