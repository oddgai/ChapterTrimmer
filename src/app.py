import subprocess
import tempfile
from pathlib import Path

import flet as ft
from scenedetect import SceneManager, ThresholdDetector, open_video
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


def main(page: ft.Page):
    page.title = "Chapter Trimmer"
    page.padding = 40
    page.window_width = 1200
    page.window_height = 900
    page.scroll = ft.ScrollMode.AUTO

    def init_page(initial_container: ft.Container):
        page.clean()
        page.add(initial_container)

    def save_splitted_chapter(
        input_video_path: Path,
        chapter_list: list[tuple[FrameTimecode, FrameTimecode]],
        output_dir: Path,
    ) -> list[Path]:
        splitted_file_path_list = []
        for idx, chapter in tqdm(enumerate(chapter_list)):
            start_time = chapter[0].get_seconds()
            end_time = chapter[1].get_seconds()
            output_file_path = output_dir.joinpath(
                f"{input_video_path.stem}_chapter_{idx+1:0{len(str(len(chapter_list)))}}{input_video_path.suffix}"
            )
            cmd = f'ffmpeg -y -i "{str(input_video_path)}" -ss {start_time} -to {end_time} -c:v copy -c:a copy "{output_file_path}"'
            subprocess.run(cmd)
            splitted_file_path_list.append(output_file_path)
        return splitted_file_path_list

    def merge_selected_chapter(
        splitted_file_path_list: list[Path],
        selected_chapter_list: list[int],
        original_video_file_path: Path,
        delete_dir: Path,
    ):
        output_file_path = original_video_file_path.parent.joinpath(
            f"{original_video_file_path.stem}_edit{original_video_file_path.suffix}"
        )
        selected_chapter_file_path_list = [splitted_file_path_list[idx] for idx in selected_chapter_list]
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            print(tf.name)
            with open(tf.name, "w") as f:
                for file_path in selected_chapter_file_path_list:
                    f.write(f"file {file_path.as_posix()}\n")

            cmd = f'ffmpeg -y -f concat -safe 0 -i "{tf.name}" -c copy "{output_file_path}"'
            print(cmd)
            subprocess.run(cmd)

        # 完了したらダイアログを表示
        complete_dialog = ft.AlertDialog(
            title=ft.Text(f"Trimmed video saved here; {str(output_file_path)}"),
            content=ft.Text("Load other video if necessary."),
            on_dismiss=init_page(file_pick_button),
        )
        page.dialog = complete_dialog
        complete_dialog.open = True
        page.update()

    def load_videos(e: ft.FilePickerResultEvent):
        init_page(file_pick_button)

        uploaded_video = [ft.VideoMedia(f.path) for f in e.files]
        current_status_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Detecting Chapters ...", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                    ft.Text("Progress is displayed in the console.", theme_style=ft.TextThemeStyle.BODY_LARGE),
                    ft.ProgressBar(width=page.window_width, color="amber", bgcolor="#eeeeee"),
                ]
            )
        )
        page.add(current_status_content)
        page.update()

        input_video_path = Path(uploaded_video[0].resource)
        chapter_list = detect_chapter(str(input_video_path))

        temp_dir = Path(tempfile.mkdtemp(prefix="chapter-trimmer-"))
        splitted_file_path_list = save_splitted_chapter(
            input_video_path=input_video_path, chapter_list=chapter_list, output_dir=temp_dir
        )

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
        splitted_video_grid = ft.GridView(
            runs_count=3, spacing=20, run_spacing=20, child_aspect_ratio=16 / 12, padding=ft.padding.only(right=20)
        )
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
            splitted_video_grid.controls.append(
                ft.Container(
                    ft.Column([check_box, splitted_video]),
                    bgcolor=ft.colors.GREY_200,
                    border_radius=10,
                    padding=10,
                ),
            )

        # submitボタンクリックで選択したチャプターの動画を保存する
        page.add(
            ft.Container(
                content=ft.ElevatedButton(
                    text="Merge Selected Chapters",
                    on_click=lambda e: merge_selected_chapter(
                        splitted_file_path_list=splitted_file_path_list,
                        selected_chapter_list=[i for i, c in enumerate(check_box_list) if c.value],
                        original_video_file_path=input_video_path,
                        delete_dir=temp_dir,
                    ),
                ),
                margin=ft.margin.symmetric(vertical=10),
                alignment=ft.alignment.center_right,
            ),
        )
        page.update()

    file_picker = ft.FilePicker(on_result=load_videos)
    page.overlay.append(file_picker)
    file_pick_button = ft.Container(
        ft.ElevatedButton(
            "Pick Video File",
            icon=ft.icons.UPLOAD_FILE,
            on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.VIDEO),
        ),
        padding=ft.padding.only(bottom=20),
    )
    page.add(file_pick_button)
    page.update()


ft.app(target=main)
