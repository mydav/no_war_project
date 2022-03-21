from modules.text_functions import no_probely
from modules.list_functions import clear_list


def generate_html_from_links(links: list, tpl='<a href="[link]">.</a>'):
    items = []
    for link in links:
        repl = {
            "[link]": link,
        }
        item = no_probely(tpl, repl)
        items.append(item)
    body = "".join(items)
    return body


if __name__ == "__main__":
    special = "generate_html_from_links"
    if special == "generate_html_from_links":
        links = clear_list(
            """
        http://google.com
        http//yandex.ru
        """
        )
        print(links)
        html = generate_html_from_links(links)
        print(f"{html=}")
