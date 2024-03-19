import os
import subprocess
import tempfile

import flet as ft
from scenedetect import (
    AdaptiveDetector,
    ContentDetector,
    SceneManager,
    ThresholdDetector,
    open_video,
    split_video_ffmpeg,
)
from scenedetect.frame_timecode import FrameTimecode


def detect_chapter(video_file_path: str) -> list[tuple[FrameTimecode, FrameTimecode]]:
    """動画内の真っ黒/真っ白シーンを区切りとしてチャプターを検出する"""
    print(video_file_path)
    video = open_video(video_file_path)
    scene_manager = SceneManager()
    scene_manager.auto_downscale = True

    scene_manager.add_detector(
        ThresholdDetector(threshold=243, method=ThresholdDetector.Method.CEILING)
    )  # detect White
    scene_manager.add_detector(ThresholdDetector(threshold=12, method=ThresholdDetector.Method.FLOOR))  # detect Black

    # TODO: なぜかエラーになるので直す
    # scene_manager.add_detector(AdaptiveDetector)

    scene_manager.detect_scenes(frame_source=video)
    chapter_list = scene_manager.get_scene_list()
    for chapter in chapter_list:
        print(chapter)
    return chapter_list


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "ChapterTrimmer"
    page.spacing = 20
    page.padding = 50

    def load_videos(e: ft.FilePickerResultEvent):
        uploaded_videos = [ft.VideoMedia(f.path) for f in e.files]

        video = ft.Video(
            aspect_ratio=16 / 9,
            autoplay=True,
            filter_quality=ft.FilterQuality.HIGH,
            playlist=uploaded_videos,
            playlist_mode=ft.PlaylistMode.LOOP,
        )

        page.add(
            ft.Stack(
                [
                    video,
                    ft.Container(
                        content=ft.Text(),
                        on_click=lambda _: video.play_or_pause(),
                        border_radius=0,
                        ink=True,
                        left=0,
                        right=0,
                        top=0,
                        bottom=70,
                    ),
                ]
            ),
        )
        page.update()

        input_video_path = uploaded_videos[0].resource
        chapter_list = detect_chapter(input_video_path)
        split_video_ffmpeg(input_video_path, chapter_list, output_dir="C://Users/kouki/Downloads", show_progress=True)
        print("saved")

    file_picker = ft.FilePicker(on_result=load_videos)
    page.overlay.append(file_picker)
    page.add(
        ft.Row(
            [
                ft.ElevatedButton(
                    "Pick files",
                    icon=ft.icons.UPLOAD_FILE,
                    on_click=lambda _: file_picker.pick_files(
                        allow_multiple=True, file_type=ft.FilePickerFileType.VIDEO
                    ),
                ),
            ]
        ),
    )


ft.app(target=main)
