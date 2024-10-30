import logging
import sys
import threading
from collections.abc import Callable
from functools import partial
from pathlib import Path
from tkinter import PhotoImage

import customtkinter as ctk

from .collector import Collector
from .csv_writer import write_csv
from .gui_components import AutoHidingScrollableFrame, CTkTqdm
from .researchers import (
    AudioResearcher,
    BasicResearcher,
    ImageResearcher,
    LegacyOfficeResearcher,
    ModernOfficeResearcher,
    PdfResearcher,
    Researcher,
)

ICON_PATH = Path(__file__).parent / "assets" / "sniffler.png"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class ChoosePath(ctk.CTkFrame):
    def __init__(self, master, path: Path, title: str = "Choose Path", button_text: str = "Browse") -> None:
        super().__init__(master)
        self.path = path
        self.title_text = title

        self.title_label = ctk.CTkLabel(self, text=self.title_text, font=ctk.CTkFont(size=14, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(10, 0), sticky="w")

        self.scroll_frame = AutoHidingScrollableFrame(self, height=23, orientation="horizontal")
        self.scroll_frame.grid(row=1, column=0, padx=(20, 10), pady=(5, 20), sticky="ew")

        self.label = ctk.CTkLabel(self.scroll_frame, text=str(self.path.resolve()), height=9)
        self.label.grid(row=0, column=0, sticky="nw")

        self.browse_button = ctk.CTkButton(self, text=button_text, command=self.browse_callback)
        self.browse_button.grid(row=1, column=2, padx=(0, 20), pady=(5, 20), sticky="nsew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def browse_callback(self) -> None:
        path = ctk.filedialog.askdirectory(initialdir=self.path.resolve())
        if path:
            self.path = Path(path)
            self.label.configure(text=str(self.path.resolve()))


class AppController:
    def __init__(
        self,
        researchers: list[Callable[..., Researcher]],
        source: ChoosePath,
        target: ChoosePath,
        progress_bar: ctk.CTkProgressBar,
        status_label: ctk.CTkLabel,
        start_button: ctk.CTkButton,
    ):
        logger.info("Initializing controller...")
        self.researchers = researchers
        self.source = source
        self.target = target
        self.progress_bar = progress_bar
        self.status_label = status_label
        self.start_button = start_button

    def start_collection(self) -> None:
        logger.info("Starting collection...")
        self.start_button.configure(state="disabled")
        self.status_label.configure(text="Sniffling...")
        researchers = [researcher() for researcher in self.researchers]
        pbar = partial(CTkTqdm, progressbar=self.progress_bar)

        def task():
            collector = None
            try:
                collector = Collector(self.source.path, researchers, progress_bar=pbar)
                collector.collect(show_progress=True)
            except Exception as e:
                logger.exception(e)
                self.status_label.configure(text="An error occurred, please check the logs.")

            if collector and collector.collection:
                self.progress_bar.set(1)
                logger.info("Collection finished.")
                write_csv(
                    self.target.path.joinpath("out.csv"), collector.collection.keys, collector.collection, delimiter=";"
                )
                logger.info("CSV saved.")
                self.start_button.configure(state="normal")
                self.status_label.configure(text="Sniffling complete, output saved to 'out.csv' in the target directory.")

        threading.Thread(target=task).start()


class AppUI(ctk.CTk):
    def __init__(
        self, researchers: list[Callable[..., Researcher]], title: str = "Sniffler", dims: tuple[int, int] = (700, 500)
    ) -> None:
        logger.info("Initializing UI...")
        super().__init__()
        self.title(title)
        self.geometry(f"{dims[0]}x{dims[1]}")
        self.iconphoto(True, PhotoImage(file=ICON_PATH))
        self.grid_columnconfigure((0, 1), weight=1)

        # Initialize UI components
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, columnspan=2, pady=(10, 20), padx=20, sticky="nsew")
        self.tabs.add("Collect")
        self.tabs.add("Stats")
        self.tabs.add("About")

        # Collect tab layout
        collect_tab = self.tabs.tab("Collect")
        collect_tab.grid_columnconfigure((0, 1), weight=1)

        # Path selection components
        self.source = ChoosePath(collect_tab, Path("."), title="Choose a directory to sniff", button_text="Browse")
        self.source.grid(row=0, column=0, columnspan=2, pady=(20, 0), padx=20, sticky="ew")

        self.target = ChoosePath(collect_tab, Path("."), title="Choose output directory", button_text="Browse")
        self.target.grid(row=2, column=0, columnspan=2, pady=(0, 20), padx=20, sticky="ew")

        # Start button
        self.start_button = ctk.CTkButton(collect_tab, text="Start", height=40)
        self.start_button.grid(row=3, column=0, columnspan=2, pady=(0, 20), padx=20, sticky="ew")

        # Progress bar and status label
        self.progress_bar = ctk.CTkProgressBar(collect_tab)
        self.progress_bar.grid(row=4, column=0, columnspan=2, pady=(0, 0), padx=20, sticky="ew")
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(collect_tab, text="Ready for sniffling", font=ctk.CTkFont(size=10))
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(0, 10))

        # Stats tab layout
        stats_tab = self.tabs.tab("Stats")
        stats_tab.grid_columnconfigure(0, weight=1)
        stats_tab.grid_rowconfigure(0, weight=1)

        # About tab layout
        about_tab = self.tabs.tab("About")
        about_tab.grid_columnconfigure(0, weight=1)
        about_tab.grid_rowconfigure(0, weight=1)

        about_text = (
            "Sniffler is a tool to collect information about files in a directory.\n"
            "It is built using Python and Tkinter.\n\n"
            "Developed by: Alexander Sevostianov\n"
            "GitHub: https://github.com/Darxor/"
        )
        about_label = ctk.CTkLabel(about_tab, text=about_text, font=ctk.CTkFont(size=12))
        about_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Controller setup
        self.controller = AppController(
            researchers, self.source, self.target, self.progress_bar, self.status_label, self.start_button
        )
        self.start_button.configure(command=self.controller.start_collection)

        self.focus_force()


def main() -> None:
    researchers = [
        BasicResearcher,
        ImageResearcher,
        AudioResearcher,
        PdfResearcher,
        ModernOfficeResearcher,
        LegacyOfficeResearcher,
    ]

    app = AppUI(researchers)
    app.mainloop()


if __name__ == "__main__":
    main()
