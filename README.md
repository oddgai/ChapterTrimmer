# ChapterTrimmer

## requirements

- ffmpeg

## Hot reload

```
rye run python src/app.py -d
```

## How to package by PyInstaller

```
pyinstaller src/app.py --onefile --specpath src/ --name ChapterTrimmer --icon assets/icon.ico
```
