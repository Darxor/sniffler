from functools import partial

from tqdm import tqdm

from sniffler.core.collector import Collector
from sniffler.researchers import (
    AudioResearcher,
    BasicResearcher,
    ImageResearcher,
    LegacyOfficeResearcher,
    ModernOfficeResearcher,
    PdfResearcher,
)


def run_scan(path):
    researchers = [
        BasicResearcher(),
        ImageResearcher(),
        AudioResearcher(),
        PdfResearcher(),
        ModernOfficeResearcher(),
        LegacyOfficeResearcher(),
    ]
    collector = Collector(
        path,
        researchers,
        progress_bar=partial(tqdm, desc="Collecting", unit=" files"),
    )
    collector.collect(show_progress=False)
    return collector.collection
