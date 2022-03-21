from modules.print_functions import show_dict
from modules.list_functions import sort_nicely, split_list
from modules.test_helpers import sleep_
from modules.print_functions import get_printed_result_as_html
from typing import List
import time


class StatsCollector:
    def __init__(
        self,
        name="",
        short_names={},
        phrase_to_short_name={},
        collector="",
        on_new="",
    ):
        self.name = name
        self.stat = {}

        self.short_names = short_names
        self.phrase_to_short_name = phrase_to_short_name
        self.queue = []

        self.total_size = 0
        self.collector = collector

        self.on_new = on_new

    def without_stat(self):
        """Без статы - значит не собираем никакую стату"""
        return self.collector == "without_stat"

    def plus_1(self, key="", value=1):
        """
            апдейтим стату
        """
        if self.without_stat():
            return

        if key not in self.stat:
            self.stat[key] = 0
            if self.on_new == "print":
                print(f"    plus_1 new `{key}`")
        self.stat[key] += value

        _ = {
            "key": key,
            "t_add": time.time(),
            "short": self.get_short(key),
            "value": value,
        }
        self.queue.append(_)

    def get_short(self, key=""):
        short = self.short_names.get(key, None)
        if short is None:
            for phrase, possible_short in self.phrase_to_short_name.items():
                if phrase in key:
                    short = possible_short
                    break
        if short is None:
            short = key
        return short

    def filter_queue(self, queue: list = None, max_life: float = None) -> dict:
        if queue is None:
            queue = self.queue

        filtered = []
        for element in queue:
            if max_life is not None:
                life = time.time() - element["t_add"]
                # print(f"{life=:.2f}")
                if life > max_life:
                    continue

            filtered.append(element)
        return filtered

    def get_queue_stat(self, queue: list = None) -> dict:
        if queue is None:
            queue = self.queue

        stat = {}
        for element in queue:
            key = element["key"]
            if not key in stat:
                stat[key] = 0
            stat[key] += element["value"]
        return stat

    def print_stat_multi(
        self,
        with_percent: bool = False,
        po_100: bool = True,
        max_lifes: List[float] = None,
    ):
        args = locals()
        # show_dict(args)
        args_default = args.copy()
        del args_default["max_lifes"]
        del args_default["self"]

        if max_lifes is None:
            max_lifes = [None]

        all_args = []
        for max_life in max_lifes:
            args_ = args_default.copy()
            args_["max_life"] = max_life
            all_args.append(args_)
        # print(all_args)

        nl = "\n"
        for num, args in enumerate(all_args, 1):
            print(f'{nl*2} {"-"*20} {num}/{len(all_args)} {args=}')
            self.print_stat(**args)

    def print_stat(
        self,
        with_percent: bool = False,
        po_100: bool = True,
        max_life: float = None,
        limit_po_100: int = 300,
    ):

        queue = self.filter_queue(max_life=max_life)

        if not queue:
            print("empty queue")
            return

        seconds_from_start = time.time() - queue[0]["t_add"]
        if seconds_from_start == 0:
            seconds_from_start = 0.01
        minutes_from_start = seconds_from_start / 60
        hours_from_start = minutes_from_start / 60

        stat = self.get_queue_stat(queue=queue)

        print(
            f"{self.name} - filtered {len(queue)}/{len(self.queue)} - stats for {sum(stat.values())}: {stat}"
        )

        show_dict(stat)

        if with_percent:
            print(
                f"\nin percents seconds={seconds_from_start:.0f}s (minutes={minutes_from_start:.0f}, hours={hours_from_start:.0f})"
            )
            keys = list(stat.keys())
            sort_nicely(keys)
            suma = sum(stat.values())
            for key in keys:
                value = stat[key]
                procent = int(100 * value / suma)

                per_second = value / seconds_from_start
                print(f"    {key}   {value}      {procent}% {per_second=:.1f}")

        if po_100:
            line_size = 100
            queue_short = [_["short"] for _ in queue[-limit_po_100:]]
            queue_short.reverse()
            pa4ki = split_list(queue_short, line_size)

            print(f"\nstata po 100 with {limit_po_100=}/{len(queue)}:")
            num_pa4ka = 0
            cnt_now = 0
            for pa4ka in pa4ki:
                num_pa4ka += 1
                cnt_now += len(pa4ka)

                line = "".join(pa4ka)

                procent_info = " "
                if self.total_size != 0:
                    procent = int(100 * cnt_now / self.total_size)
                    procent_info = "=%d%% " % procent

                print(f"    {cnt_now}/{self.total_size}{procent_info} {line}")


if __name__ == "__main__":
    from random import choice

    short_names = {
        "already_downloaded": "a",
        "downloaded": "+",
        "captcha": "C",
        "error": "e",
    }
    phrase_to_short_name = {"error_": "e"}
    # phrase_to_short_name = {}

    stats_collector = StatsCollector(
        "crawler_stats",
        short_names=short_names,
        phrase_to_short_name=phrase_to_short_name,
    )

    all_keys = list(short_names.keys())
    all_keys = all_keys + ["t1", "t2", "error_1", "error_2"]
    for i in range(110):
        _ = choice(all_keys)
        if i < 3:
            sleep_(0.1)
        stats_collector.plus_1(_)

    with_percent = False
    with_percent = True
    po_100 = True

    special = "print_stat_multi"
    special = "print_stat"

    if special == "print_stat":
        args = {
            "with_percent": with_percent,
            "po_100": po_100,
            "max_life": 0.01,
        }
        stats_collector.print_stat(**args)

    if special == "print_stat_multi":
        args = {
            "with_percent": with_percent,
            "po_100": po_100,
            "max_lifes": [0.01, None],
        }
        stats_collector.print_stat_multi(**args)

    t = 1
    t = 0
    if t:
        printed = get_printed_result_as_html(stats_collector.print_stat, *args)
        print(printed)
