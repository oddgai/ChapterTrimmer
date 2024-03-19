import flet as ft


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
            on_loaded=lambda e: print("Video loaded successfully!"),
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
