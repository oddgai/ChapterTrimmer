import shutil
import subprocess
import tempfile
from pathlib import Path

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
from tqdm import tqdm


def detect_chapter(video_file_path: str) -> list[tuple[FrameTimecode, FrameTimecode]]:
    video = open_video(video_file_path)
    scene_manager = SceneManager()
    scene_manager.auto_downscale = True

    # detect White
    scene_manager.add_detector(ThresholdDetector(threshold=243, method=ThresholdDetector.Method.CEILING))

    # detect Black
    scene_manager.add_detector(ThresholdDetector(threshold=12, method=ThresholdDetector.Method.FLOOR))

    # TODO: なぜかエラーになるので直す
    # scene_manager.add_detector(AdaptiveDetector)

    scene_manager.detect_scenes(frame_source=video, show_progress=True)
    chapter_list = scene_manager.get_scene_list()
    return chapter_list


def save_selected_chapter(
    input_video_path: Path,
    chapter_list: list[tuple[FrameTimecode, FrameTimecode]],
    output_dir: Path,
    delete_dir: Path | None = None,
):
    for idx, chapter in tqdm(enumerate(chapter_list)):
        start_time = chapter[0].get_seconds()
        end_time = chapter[1].get_seconds()
        output_file_path = output_dir.joinpath(f"{input_video_path.stem}_{idx+1:03}{input_video_path.suffix}")
        cmd = f'ffmpeg -y -i "{str(input_video_path)}" -ss {start_time} -to {end_time} -c:v copy -c:a copy "{output_file_path}"'
        subprocess.run(cmd)

    if delete_dir:
        shutil.rmtree(delete_dir)
    print(f"saved in {str(output_dir)}")


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "ChapterTrimmer"
    page.spacing = 20
    page.padding = 20
    page.window_width = 800
    page.window_height = 1200
    page.scroll = ft.ScrollMode.ADAPTIVE

    def load_videos(e: ft.FilePickerResultEvent):
        uploaded_videos = [ft.VideoMedia(f.path) for f in e.files]

        original_video = ft.Video(
            aspect_ratio=16 / 9,
            autoplay=True,
            filter_quality=ft.FilterQuality.HIGH,
            playlist=uploaded_videos,
            playlist_mode=ft.PlaylistMode.LOOP,
        )

        current_status_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Detecting Chapters ...", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.ProgressBar(width=page.window_width, color="amber", bgcolor="#eeeeee"),
                ]
            )
        )

        page.add(ft.Text("Original Video", theme_style=ft.TextThemeStyle.TITLE_LARGE))
        page.add(original_video)
        page.add(current_status_content)
        page.update()

        input_video_path = Path(uploaded_videos[0].resource)
        chapter_list = detect_chapter(str(input_video_path))

        temp_dir = Path(tempfile.mkdtemp(prefix="chapter-trimmer-"))
        save_selected_chapter(input_video_path, chapter_list, output_dir=temp_dir)

        # chapterに分けた動画を読み込む
        splitted_video_list = []
        for splitted_file in temp_dir.glob(f"*{input_video_path.suffix}"):
            splitted_video_list.append(
                ft.Video(
                    aspect_ratio=16 / 9,
                    autoplay=False,
                    filter_quality=ft.FilterQuality.HIGH,
                    playlist=[ft.VideoMedia(str(splitted_file))],
                    playlist_mode=ft.PlaylistMode.SINGLE,
                )
            )

        # 表示する
        splitted_video_grid = ft.GridView(runs_count=2, spacing=40, run_spacing=20, child_aspect_ratio=16 / 10)
        current_status_content.content = ft.Column(
            [
                ft.Text(f"{len(splitted_video_list)} Chapters Detected!", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Text(
                    "Please select the chapters you want to save and press the button below.",
                    theme_style=ft.TextThemeStyle.BODY_LARGE,
                ),
            ]
        )
        page.add(splitted_video_grid)

        check_box_list = [ft.Checkbox(value=False) for _ in range(len(splitted_video_list))]
        for check_box, splitted_video in zip(check_box_list, splitted_video_list):
            splitted_video_grid.controls.append(ft.Column([check_box, splitted_video]))

        page.add(
            ft.Container(
                content=ft.ElevatedButton(
                    text="Save Selected Chapters",
                    on_click=lambda e: save_selected_chapter(
                        input_video_path,
                        [chapter for chapter, tf in zip(chapter_list, [c.value for c in check_box_list]) if tf],
                        output_dir=input_video_path.parent,
                        delete_dir=temp_dir,
                    ),
                ),
                margin=20,
                alignment=ft.alignment.center_right,
            ),
        )
        page.update()

    file_picker = ft.FilePicker(on_result=load_videos)
    page.overlay.append(file_picker)
    page.add(
        ft.ElevatedButton(
            "Pick Video file",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.VIDEO),
        ),
    )


ft.app(target=main)
