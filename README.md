# ChapterTrimmer

## Hot reload

```
rye run python src/app.py -d
```

## How to package by PyInstaller

```
pyinstaller src/app.py --onefile --specpath src/ --name "Chapter Trimmer" --icon assets/icon.ico
```
