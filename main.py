import argparse
import sys
import os


def main():
    parser = argparse.ArgumentParser()

    # Параметры
    parser.add_argument('--package', type=str, required=True)
    parser.add_argument('--source', type=str, required=True)
    parser.add_argument('--test-repo-mode', action='store_true')
    parser.add_argument('--max-depth', type=int, default=0)
    args = parser.parse_args()

    try:
        # Валидация параметров
        if not args.package or not args.package.strip():
            raise ValueError("Package name cannot be empty")

        if not args.source or not args.source.strip():
            raise ValueError("Source cannot be empty")

        if args.max_depth < 0:
            raise ValueError("Max depth cannot be negative")

        # Проверка существования файла для локального пути
        if args.test_repo_mode and not args.source.startswith(('http://', 'https://')):
            if not os.path.exists(args.source):
                raise FileNotFoundError(f"Source file not found: {args.source}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Вывод всех параметров в формате ключ-значение
    print("Configuration parameters:")
    print(f"package: {args.package}")
    print(f"source: {args.source}")
    print(f"test_repo_mode: {args.test_repo_mode}")
    print(f"max_depth: {args.max_depth}")


if __name__ == "__main__":
    main()
