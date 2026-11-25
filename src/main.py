import argparse
from pathlib import Path
from sorter import build_plan, execute_plan, write_report

def main():
    parser = argparse.ArgumentParser(description="Локальный сортировщик файлов по типам.")
    parser.add_argument("folder", help="Папка, файлы которой нужно отсортировать")
    parser.add_argument("--yes", action="store_true", help="Выполнить сортировку без дополнительного вопроса")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    try:
        plan = build_plan(folder)
    except ValueError as error:
        parser.error(str(error))

    print(f"Найдено файлов: {len(plan)}")
    for source, target in plan:
        print(f"{source.name} -> {target.parent.name}/{target.name}")
    write_report(folder, plan)

    if not args.yes:
        answer = input("Переместить файлы? [y/N]: ").strip().lower()
        if answer not in {"y", "yes", "д", "да"}:
            print("Сортировка отменена. Файлы не перемещались.")
            return

    results = execute_plan(plan, folder)
    write_report(folder, plan, results)
    print(f"Готово. Отчёт: {folder / 'report.md'}")
    print(f"Журнал: {folder / 'log.csv'}")

if __name__ == "__main__":
    main()
