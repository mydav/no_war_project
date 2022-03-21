from typing import List
from modules.text_functions import to_hash
from modules.print_functions import show_list


def get_urls_to_external_pages_from_parsed(
    parsed, d_to="temp/external_pages/test"
):
    urls = []

    blocks_with_snipets = [
        parsed.snipets,
        parsed.also_ask,
    ]
    for block in blocks_with_snipets:
        for snipet in block:
            url = snipet.url
            urls.append(url)

    if parsed.answer:
        urls.append(parsed.answer.url)

    return get_download_task_from_urls(urls, d_to=d_to)


def get_download_task_from_urls(urls: List, d_to="temp/external_pages/test"):
    tasks = []
    for url in urls:
        h = to_hash(url)
        f_to = f"{d_to}/{h}.html"
        _ = {
            "url": url,
            "f_to": f_to,
        }
        tasks.append(_)
    return tasks


# async def wait download_external_pages(task):
# pa


if __name__ == "__main__":
    urls = [
        "https://ru.wikipedia.org/wiki/%D0%9C%D1%8B%D1%88%D0%BB%D0%B5%D0%BD%D0%B8%D0%B5_(%D0%BF%D1%81%D0%B8%D1%85%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D1%8F)",
    ]
    d_to = "temp/external_pages/test"
    tasks = get_download_task_from_urls(urls, d_to=d_to)
    show_list(tasks)
