# ChapterTrimmer

The app automatically detect chapters from consecutive black/white frames in a video and save only the selected chapters.

## Demo

Below `sample.mp4` file is composed of 5 videos connected by black/white frames.
ChapterTrimmer detect 5 chapters from this video and save only the chapters you need!

![demo](https://github.com/oddgai/ChapterTrimmer/assets/45445604/508e0a0c-eb95-4a15-9464-c5f04617d4cc)

## Download

https://github.com/oddgai/ChapterTrimmer/releases

## How to use

0. Preparation: Install [ffmpeg](https://ffmpeg.org/) before launching this app
1. Launch the application
    - At the same time, a console will be launched that displays the progress of chapter detection
2. Select your video
3. Please wait for chapter detection
4. Select the chapters you want to keep in the video and press the Merge button!
    - If the original file is `/hoge/sample.mp4`, it will be saved as `/hoge/sample_edit.mp4`


## For Developers

### Setup

Install [Rye](https://rye-up.com/) and run first sync

```
$ rye sync
```

### Hot reload

```
$ rye run python src/app.py -d
```

### How to package by PyInstaller

```
$ pyinstaller src/app.py --onefile --specpath src/ --name ChapterTrimmer --icon assets/icon.ico
```
