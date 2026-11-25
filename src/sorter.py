from pathlib import Path
from datetime import datetime
import csv
import shutil

CATEGORIES = {
    "docs": {".doc", ".docx", ".pdf", ".txt", ".rtf", ".md"},
    "images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"},
    "tables": {".csv", ".xls", ".xlsx", ".ods"},
    "archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "code": {".py", ".js", ".html", ".css", ".java", ".cpp", ".sql"},
}

def classify_file(path: Path) -> str:
    """Возвращает категорию файла по его расширению."""
    suffix = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "other"

def build_plan(folder: Path) -> list[tuple[Path, Path]]:
    """Создаёт план перемещения, не меняя файлы на диске."""
    folder = Path(folder).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise ValueError("Указанная папка не существует или это не папка.")

    plan = []
    for item in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        if item.is_file() and item.name not in {"report.md", "log.csv"}:
            target_dir = folder / classify_file(item)
            target = target_dir / item.name
            counter = 1
            while target.exists() or any(existing_target == target for _, existing_target in plan):
                target = target_dir / f"{item.stem}_{counter}{item.suffix}"
                counter += 1
            plan.append((item, target))
    return plan

def execute_plan(plan: list[tuple[Path, Path]], folder: Path) -> list[tuple[str, str]]:
    """Перемещает файлы и записывает журнал выполненных действий."""
    results = []
    log_path = Path(folder) / "log.csv"
    with log_path.open("w", newline="", encoding="utf-8") as log_file:
        writer = csv.writer(log_file)
        writer.writerow(["время", "исходный файл", "новый путь", "статус"])
        for source, target in plan:
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target))
                status = "перемещён"
            except OSError as error:
                status = f"ошибка: {error}"
            writer.writerow([datetime.now().isoformat(timespec="seconds"), source.name, str(target), status])
            results.append((source.name, status))
    return results

def write_report(folder: Path, plan: list[tuple[Path, Path]], results=None) -> Path:
    folder = Path(folder)
    lines = [
        "# Отчёт о сортировке файлов",
        "",
        f"Папка: `{folder}`",
        f"Файлов в плане: {len(plan)}",
        "",
        "## План перемещения",
        "",
    ]
    if not plan:
        lines.append("Подходящих файлов для сортировки нет.")
    for source, target in plan:
        lines.append(f"- `{source.name}` → `{target.parent.name}/{target.name}`")
    if results is not None:
        lines.extend(["", "## Результат", ""])
        for name, status in results:
            lines.append(f"- `{name}`: {status}")
    report = folder / "report.md"
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report
