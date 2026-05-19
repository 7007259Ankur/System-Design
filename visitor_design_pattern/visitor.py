"""
Visitor Design Pattern - Advanced Implementation
Real-world scenario: Document AST with multiple export formats
The same document structure is traversed by different visitors —
HTML export, Markdown export, word count, SEO analysis —
without touching any element class.
"""

from __future__ import annotations
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Visitor Interface — one visit method per element type
# ---------------------------------------------------------------------------

class DocumentVisitor(ABC):
    @abstractmethod
    def visit_document(self, element: "Document") -> Any: ...

    @abstractmethod
    def visit_heading(self, element: "Heading") -> Any: ...

    @abstractmethod
    def visit_paragraph(self, element: "Paragraph") -> Any: ...

    @abstractmethod
    def visit_table(self, element: "Table") -> Any: ...

    @abstractmethod
    def visit_code_block(self, element: "CodeBlock") -> Any: ...

    @abstractmethod
    def visit_image(self, element: "Image") -> Any: ...


# ---------------------------------------------------------------------------
# Element Interface — every element must accept a visitor
# ---------------------------------------------------------------------------

class DocumentElement(ABC):
    @abstractmethod
    def accept(self, visitor: DocumentVisitor) -> Any:
        """Double dispatch: calls the right visitor method for this type."""
        ...


# ---------------------------------------------------------------------------
# Concrete Elements — the document AST nodes
# ---------------------------------------------------------------------------

@dataclass
class Heading(DocumentElement):
    text: str
    level: int = 1  # 1–6

    def accept(self, visitor: DocumentVisitor) -> Any:
        return visitor.visit_heading(self)


@dataclass
class Paragraph(DocumentElement):
    text: str
    bold_ranges: list[tuple[int, int]] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)  # (text, url)

    def accept(self, visitor: DocumentVisitor) -> Any:
        return visitor.visit_paragraph(self)


@dataclass
class Table(DocumentElement):
    headers: list[str]
    rows: list[list[str]]
    caption: str = ""

    def accept(self, visitor: DocumentVisitor) -> Any:
        return visitor.visit_table(self)


@dataclass
class CodeBlock(DocumentElement):
    code: str
    language: str = "python"
    filename: str = ""

    def accept(self, visitor: DocumentVisitor) -> Any:
        return visitor.visit_code_block(self)


@dataclass
class Image(DocumentElement):
    src: str
    alt: str
    caption: str = ""
    width: int = 0

    def accept(self, visitor: DocumentVisitor) -> Any:
        return visitor.visit_image(self)


@dataclass
class Document(DocumentElement):
    title: str
    children: list[DocumentElement] = field(default_factory=list)
    meta_description: str = ""
    author: str = ""

    def add(self, *elements: DocumentElement) -> "Document":
        self.children.extend(elements)
        return self

    def accept(self, visitor: DocumentVisitor) -> Any:
        return visitor.visit_document(self)


# ---------------------------------------------------------------------------
# Concrete Visitor 1 — HTML Export
# ---------------------------------------------------------------------------

class HTMLExportVisitor(DocumentVisitor):
    def __init__(self, include_meta: bool = True):
        self._include_meta = include_meta
        self._output: list[str] = []

    def visit_document(self, element: Document) -> str:
        lines = ["<!DOCTYPE html>", "<html>", "<head>"]
        lines.append(f"  <title>{element.title}</title>")
        if self._include_meta and element.meta_description:
            lines.append(f'  <meta name="description" content="{element.meta_description}">')
        if element.author:
            lines.append(f'  <meta name="author" content="{element.author}">')
        lines.append("</head>")
        lines.append("<body>")
        for child in element.children:
            lines.append(child.accept(self))
        lines.append("</body>")
        lines.append("</html>")
        return "\n".join(lines)

    def visit_heading(self, element: Heading) -> str:
        tag = f"h{element.level}"
        return f"<{tag}>{element.text}</{tag}>"

    def visit_paragraph(self, element: Paragraph) -> str:
        text = element.text
        for url_text, url in element.links:
            text = text.replace(url_text, f'<a href="{url}">{url_text}</a>')
        return f"<p>{text}</p>"

    def visit_table(self, element: Table) -> str:
        lines = ["<table>"]
        if element.caption:
            lines.append(f"  <caption>{element.caption}</caption>")
        lines.append("  <thead><tr>")
        for h in element.headers:
            lines.append(f"    <th>{h}</th>")
        lines.append("  </tr></thead>")
        lines.append("  <tbody>")
        for row in element.rows:
            lines.append("    <tr>")
            for cell in row:
                lines.append(f"      <td>{cell}</td>")
            lines.append("    </tr>")
        lines.append("  </tbody>")
        lines.append("</table>")
        return "\n".join(lines)

    def visit_code_block(self, element: CodeBlock) -> str:
        filename = f'<div class="filename">{element.filename}</div>' if element.filename else ""
        return f'{filename}<pre><code class="language-{element.language}">{element.code}</code></pre>'

    def visit_image(self, element: Image) -> str:
        width_attr = f' width="{element.width}"' if element.width else ""
        img = f'<img src="{element.src}" alt="{element.alt}"{width_attr}>'
        if element.caption:
            return f"<figure>{img}<figcaption>{element.caption}</figcaption></figure>"
        return img


# ---------------------------------------------------------------------------
# Concrete Visitor 2 — Markdown Export
# ---------------------------------------------------------------------------

class MarkdownExportVisitor(DocumentVisitor):
    def visit_document(self, element: Document) -> str:
        parts = [f"# {element.title}\n"]
        if element.meta_description:
            parts.append(f"_{element.meta_description}_\n")
        for child in element.children:
            parts.append(child.accept(self))
        return "\n".join(parts)

    def visit_heading(self, element: Heading) -> str:
        return f"{'#' * element.level} {element.text}"

    def visit_paragraph(self, element: Paragraph) -> str:
        text = element.text
        for url_text, url in element.links:
            text = text.replace(url_text, f"[{url_text}]({url})")
        return text

    def visit_table(self, element: Table) -> str:
        lines = []
        if element.caption:
            lines.append(f"*{element.caption}*")
        lines.append("| " + " | ".join(element.headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(element.headers)) + " |")
        for row in element.rows:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines)

    def visit_code_block(self, element: CodeBlock) -> str:
        header = f"```{element.language}"
        if element.filename:
            header += f" title=\"{element.filename}\""
        return f"{header}\n{element.code}\n```"

    def visit_image(self, element: Image) -> str:
        md = f"![{element.alt}]({element.src})"
        if element.caption:
            md += f"\n*{element.caption}*"
        return md


# ---------------------------------------------------------------------------
# Concrete Visitor 3 — Word Count Analyzer
# ---------------------------------------------------------------------------

@dataclass
class WordCountReport:
    total_words: int = 0
    heading_words: int = 0
    paragraph_words: int = 0
    code_lines: int = 0
    image_count: int = 0
    table_cells: int = 0

    def __str__(self) -> str:
        return (
            f"  Total words:      {self.total_words}\n"
            f"  Heading words:    {self.heading_words}\n"
            f"  Paragraph words:  {self.paragraph_words}\n"
            f"  Code lines:       {self.code_lines}\n"
            f"  Images:           {self.image_count}\n"
            f"  Table cells:      {self.table_cells}"
        )


class WordCountVisitor(DocumentVisitor):
    def __init__(self):
        self.report = WordCountReport()

    def _count(self, text: str) -> int:
        return len(re.findall(r"\w+", text))

    def visit_document(self, element: Document) -> WordCountReport:
        for child in element.children:
            child.accept(self)
        return self.report

    def visit_heading(self, element: Heading) -> None:
        n = self._count(element.text)
        self.report.heading_words += n
        self.report.total_words += n

    def visit_paragraph(self, element: Paragraph) -> None:
        n = self._count(element.text)
        self.report.paragraph_words += n
        self.report.total_words += n

    def visit_table(self, element: Table) -> None:
        for row in element.rows:
            for cell in row:
                self.report.total_words += self._count(cell)
                self.report.table_cells += 1

    def visit_code_block(self, element: CodeBlock) -> None:
        self.report.code_lines += element.code.count("\n") + 1

    def visit_image(self, element: Image) -> None:
        self.report.image_count += 1
        self.report.total_words += self._count(element.alt)


# ---------------------------------------------------------------------------
# Concrete Visitor 4 — SEO Analyzer
# ---------------------------------------------------------------------------

@dataclass
class SEOReport:
    score: int = 0
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    keyword_density: dict[str, int] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [f"  SEO Score: {self.score}/100"]
        if self.issues:
            lines.append("  Issues:")
            for i in self.issues:
                lines.append(f"    ✗ {i}")
        if self.suggestions:
            lines.append("  Suggestions:")
            for s in self.suggestions:
                lines.append(f"    → {s}")
        top_kw = sorted(self.keyword_density.items(), key=lambda x: -x[1])[:5]
        if top_kw:
            lines.append(f"  Top keywords: {', '.join(f'{k}({v})' for k, v in top_kw)}")
        return "\n".join(lines)


class SEOAnalyzerVisitor(DocumentVisitor):
    def __init__(self):
        self.report = SEOReport(score=100)
        self._h1_count = 0
        self._all_text: list[str] = []

    def _penalize(self, points: int, issue: str) -> None:
        self.report.score = max(0, self.report.score - points)
        self.report.issues.append(issue)

    def visit_document(self, element: Document) -> SEOReport:
        if not element.meta_description:
            self._penalize(15, "Missing meta description")
        elif len(element.meta_description) < 50:
            self._penalize(5, "Meta description too short (< 50 chars)")
        elif len(element.meta_description) > 160:
            self._penalize(5, "Meta description too long (> 160 chars)")

        for child in element.children:
            child.accept(self)

        if self._h1_count == 0:
            self._penalize(20, "No H1 heading found")
        elif self._h1_count > 1:
            self._penalize(10, f"Multiple H1 headings ({self._h1_count}) — use only one")

        # keyword density
        all_words = re.findall(r"\b\w{4,}\b", " ".join(self._all_text).lower())
        for word in all_words:
            self.report.keyword_density[word] = self.report.keyword_density.get(word, 0) + 1

        if len(all_words) < 300:
            self.report.suggestions.append("Add more content — aim for 300+ words")
        self.report.suggestions.append("Add internal links to improve crawlability")

        return self.report

    def visit_heading(self, element: Heading) -> None:
        if element.level == 1:
            self._h1_count += 1
        self._all_text.append(element.text)

    def visit_paragraph(self, element: Paragraph) -> None:
        self._all_text.append(element.text)
        if len(element.links) == 0 and len(element.text) > 200:
            self.report.suggestions.append("Long paragraph with no links — consider adding references")

    def visit_table(self, element: Table) -> None:
        if not element.caption:
            self.report.suggestions.append("Add captions to tables for better accessibility and SEO")

    def visit_code_block(self, element: CodeBlock) -> None:
        if not element.filename:
            self.report.suggestions.append("Add filenames to code blocks for better context")

    def visit_image(self, element: Image) -> None:
        if not element.alt:
            self._penalize(5, f"Image '{element.src}' missing alt text")
        self._all_text.append(element.alt)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Visitor Pattern — Document AST Export Demo")
    print("=" * 55)

    # Build the document structure once
    doc = Document(
        title="Python Design Patterns Guide",
        meta_description="A comprehensive guide to design patterns in Python with advanced runnable examples.",
        author="Dev Team",
    ).add(
        Heading("Introduction", level=1),
        Paragraph(
            "Design patterns are reusable solutions to common software problems. "
            "Learn more at the official Python docs.",
            links=[("official Python docs", "https://docs.python.org")]
        ),
        Heading("Creational Patterns", level=2),
        Paragraph("Creational patterns deal with object creation mechanisms."),
        Table(
            headers=["Pattern", "Category", "Complexity"],
            rows=[
                ["Factory Method", "Creational", "Medium"],
                ["Abstract Factory", "Creational", "High"],
                ["Builder", "Creational", "Medium"],
                ["Singleton", "Creational", "Low"],
            ],
            caption="Overview of Creational Patterns"
        ),
        Heading("Code Example", level=2),
        CodeBlock(
            code='class Singleton:\n    _instance = None\n\n    def __new__(cls):\n        if not cls._instance:\n            cls._instance = super().__new__(cls)\n        return cls._instance',
            language="python",
            filename="singleton.py"
        ),
        Image(
            src="/images/patterns-diagram.png",
            alt="UML diagram of design patterns",
            caption="Figure 1: Design Pattern relationships",
            width=800
        ),
    )

    # --- Visitor 1: HTML Export ---
    print("\n>>> HTML Export (first 300 chars)")
    html = doc.accept(HTMLExportVisitor())
    print(html[:300] + "...\n")

    # --- Visitor 2: Markdown Export ---
    print(">>> Markdown Export")
    md = doc.accept(MarkdownExportVisitor())
    print(md[:400] + "...\n")

    # --- Visitor 3: Word Count ---
    print(">>> Word Count Report")
    wc_report = doc.accept(WordCountVisitor())
    print(wc_report)

    # --- Visitor 4: SEO Analysis ---
    print("\n>>> SEO Analysis Report")
    seo_report = doc.accept(SEOAnalyzerVisitor())
    print(seo_report)

    # --- Add a new visitor without touching any element class ---
    print("\n>>> Plain Text Export (new visitor, zero element changes)")

    class PlainTextVisitor(DocumentVisitor):
        def visit_document(self, el: Document) -> str:
            parts = [el.title.upper(), "=" * len(el.title)]
            for child in el.children:
                parts.append(child.accept(self))
            return "\n".join(parts)

        def visit_heading(self, el: Heading) -> str:
            return f"\n{'  ' * (el.level - 1)}{el.text.upper()}"

        def visit_paragraph(self, el: Paragraph) -> str:
            return el.text

        def visit_table(self, el: Table) -> str:
            rows = [" | ".join(el.headers)]
            rows += [" | ".join(row) for row in el.rows]
            return "\n".join(rows)

        def visit_code_block(self, el: CodeBlock) -> str:
            return f"[Code: {el.language}]\n{el.code}"

        def visit_image(self, el: Image) -> str:
            return f"[Image: {el.alt}]"

    plain = doc.accept(PlainTextVisitor())
    print(plain[:400] + "...")


if __name__ == "__main__":
    main()
