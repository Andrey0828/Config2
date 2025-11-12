import argparse
import sys
import os
import urllib.request
import json
from collections import deque


def get_dependencies_from_registry(package_name, registry_url):
    url = f"{registry_url.rstrip('/')}/{package_name}"
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
            return list(dependencies.keys())

    except Exception as e:
        raise RuntimeError(f"Failed to fetch data from registry: {e}")


def load_test_graph(file_path):
    with open(file_path) as f:
        return json.load(f)


def build_dependency_graph(start_package, source_type, source, max_depth):
    graph = {}
    visited = set()
    queue = deque([(start_package, 0)])

    while queue:
        current_package, depth = queue.popleft()
        # Пропускаем уже посещенные пакеты для обработки циклических зависимостей
        if current_package in visited:
            continue

        visited.add(current_package)
        if current_package not in graph:
            graph[current_package] = []

        # Проверяем ограничение по глубине
        if depth >= max_depth:
            continue

        # Получаем зависимости в зависимости от типа источника
        if source_type == "file":
            dependencies = source.get(current_package, [])
        else:
            try:
                dependencies = get_dependencies_from_registry(current_package, source)
            except Exception as e:
                print(f"Error: {e}")
                dependencies = []

        # Добавляем зависимости в граф и очередь для дальнейшего обхода
        for dep in dependencies:
            graph[current_package].append(dep)
            if dep not in visited:
                queue.append((dep, depth + 1))

    return graph


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

        if args.test_repo_mode:
            if not os.path.exists(args.source):
                raise FileNotFoundError(f"Source file not found: {args.source}")
            graph_source = load_test_graph(args.source)
            source_type = "file"
        else:
            if args.source.startswith(('http://', 'https://')):
                graph_source = args.source
                source_type = "registry"
            elif os.path.exists(args.source):
                graph_source = load_test_graph(args.source)
                source_type = "file"
            else:
                graph_source = args.source
                source_type = "registry"

        dependency_graph = build_dependency_graph(args.package, source_type,graph_source,  args.max_depth)

        for package, dependencies in dependency_graph.items():
            if dependencies:
                print(f"{package} -> {', '.join(dependencies)}")
            else:
                print(f"{package} -> No dependencies")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()