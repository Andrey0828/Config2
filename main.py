import argparse
import sys
import os
import urllib.request
import json


def get_dependencies_from_registry(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())

            # Получаем последнюю версию пакета
            latest_version = data.get('dist-tags', {}).get('latest')
            if not latest_version:
                raise ValueError(f"Latest version not found for package {package_name}")
            # Извлекаем зависимости для последней версии
            versions = data.get('versions', {})
            dependencies = versions[latest_version].get('dependencies', {})
            return dependencies

    except Exception as e:
        raise RuntimeError(f"Failed to fetch data from registry: {e}")


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

        # Получение и вывод зависимостей
        dependencies = get_dependencies_from_registry(args.package)
        if dependencies:
            print("Direct dependencies:")
            for dep, version in dependencies.items():
                print(f"{dep}: {version}")
        else:
            print("No direct dependencies found")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
