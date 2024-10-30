import customtkinter as ctk
from tqdm import tqdm

from .utils import inherit_signature_from


class AutoHidingScrollableFrame(ctk.CTkScrollableFrame):
    """
    Scrollable frame that hides the scrollbar when children element do not exceed the frame.
    """

    @inherit_signature_from(ctk.CTkScrollableFrame.__init__)
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event=None):
        self._parent_canvas.configure(scrollregion=self._parent_canvas.bbox("all"))
        if self._needs_scrollbar():
            self._scrollbar.grid()
        else:
            self._scrollbar.grid_remove()

    def _needs_scrollbar(self):
        if self._orientation == "vertical":
            return self._parent_frame.winfo_height() < self.winfo_reqheight()
        else:
            return self._parent_frame.winfo_width() < self.winfo_reqwidth()


class CTkTqdm(tqdm):
    def __init__(self, *args, progressbar: ctk.CTkProgressBar | None = None, **kwargs):
        self.progressbar = progressbar
        if self.progressbar is not None:
            self.progressbar.set(0)
        super().__init__(*args, **kwargs)

    def display(self, *args, **kwargs):
        pass  # Prevent console output

    def refresh(self, *args, **kwargs):
        pass  # Prevent console output

    def update(self, n=1) -> None:
        super().update(n)
        if self.progressbar and self.total:
            self.progressbar.set(self.n / self.total)
