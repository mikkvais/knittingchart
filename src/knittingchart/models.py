from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChartSegment:
    name: str
    page_index: int
    first_row: int
    rows: list[list[int]]  # each row: 0=light, 1=dark; col 0 = stitch 1 (chart right)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def col_count(self) -> int:
        return len(self.rows[0]) if self.rows else 0

    @property
    def last_row(self) -> int:
        return self.first_row + self.row_count - 1


@dataclass
class MergedChart:
    title: str
    source_name: str
    chart_id: str
    cols: int
    segments: list[ChartSegment] = field(default_factory=list)
    rows: list[list[int]] = field(default_factory=list)
    row_numbers: list[int] = field(default_factory=list)

    @property
    def row_count(self) -> int:
        return len(self.rows)


@dataclass
class HtmlResult:
    html: str
    filename: str
    chart: MergedChart
    warnings: list[str] = field(default_factory=list)
