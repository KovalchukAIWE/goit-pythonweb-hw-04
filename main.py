import asyncio
import argparse
import logging
import shutil
from pathlib import Path

async def copy_file(file_path: Path, dest_folder: Path):
    """
    Асинхронно копіює файл у цільову папку, створюючи підпапку за розширенням файлу.
    """
    try:
        # Визначаємо розширення файлу або присвоюємо 'no_extension', якщо його немає
        ext = file_path.suffix[1:] if file_path.suffix else "no_extension"
        target_folder = dest_folder / ext
        target_folder.mkdir(parents=True, exist_ok=True)
        target_file = target_folder / file_path.name

        # Асинхронне виконання синхронної операції копіювання у окремому потоці
        await asyncio.to_thread(shutil.copy2, file_path, target_file)
        logging.info(f"Скопійовано {file_path} до {target_file}")
    except Exception as e:
        logging.error(f"Помилка при копіюванні файлу {file_path}: {e}")

async def read_folder(source_folder: Path, dest_folder: Path):
    """
    Рекурсивно читає всі файли з вихідної папки та створює задачі для копіювання.
    """
    tasks = []
    # Проходимо по всіх файлах у папці та її підпапках
    for file_path in source_folder.glob('**/*'):
        if file_path.is_file():
            tasks.append(copy_file(file_path, dest_folder))
    if tasks:
        await asyncio.gather(*tasks)

def main():
    # Обробка аргументів командного рядка
    parser = argparse.ArgumentParser(description="Асинхронне сортування файлів за розширенням.")
    parser.add_argument("--source", required=True, help="Шлях до вихідної папки")
    parser.add_argument("--dest", required=True, help="Шлях до цільової папки")
    args = parser.parse_args()

    source_folder = Path(args.source)
    dest_folder = Path(args.dest)

    if not source_folder.exists():
        logging.error(f"Вихідна папка {source_folder} не існує.")
        return

    # Запуск асинхронного зчитування та копіювання файлів
    asyncio.run(read_folder(source_folder, dest_folder))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
