import base64
from encodings.aliases import aliases


def encode_text_to_base64(message="Python is fun", encoding="ascii"):
    message_bytes = message.encode(encoding)
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode(encoding)

    print(f"{message_bytes=}\n{base64_bytes=}\n{base64_message=}")
    return base64_message


def decode_base64_text(
    base64_message="UHl0aG9uIGlzIGZ1bg==",
    encoding="ascii",
    return_mode="bytes",
    func=base64.b64decode,
):
    base64_bytes = base64_message.encode(encoding)
    message_bytes = func(base64_bytes)
    if return_mode == "bytes":
        return message_bytes
    message = message_bytes.decode(encoding)
    return message


if __name__ == "__main__":
    special = "test_encoding"
    special = "guess_forted"
    if special == "guess_forted":
        base64_encoded = "L2dldC8f4oC5CAAAAAAABABN4oCZX+KAmdCrIAzQltCH0KLQl3bCptGB4oCg0KjQuXjQl9CHfdCrUygYOxoD0Z7QgtC9ZA/QtdCj0YRA0LVPYDt+0YDQv+KAnNCUID7QuTdr0KnRidC90JPCrcKsO8K3H3RwEtCj0KHCsdGG0YrQrl7Qi9GGwq3RjdGG0YfRgtGc0Y3RmNGOOFjRiNKR0YA30LEbTmpg4oCUSn3Rj+KApuKAonbQpNCMwrE0wrBHCcKtGgteR1TQkiXQrHADSyUR0Y7QizTRgiLQql/Qp+KAnjPQg9GM0IcGRuKAuVDQlAnRjNC5TkoUfSNS0IxdI3LRhNCf4oKs0LJh0JRST3PigLnCrtGACH8KTtCCNsKx0INxfBrQquKApi0pBdCe0ZcUSVTCplk+Y8KY0pFEXdC/ddCO0YPQkhtyT9GF0YgO0J/QitCh4oCdCBwcajo90IbigqwP4oC60LfQg0ta0JfRgkgJ0LPQndCi0YIySUwlLmZQ0IHQt3hd0KZrNg/RjTDQkVbQhNC24oSWCTjCoA5dezLihJZUEtGJFNCu0YfQhVHCoB3igJnQvtGL4oCdUmDQkdCvSeKAlNGDCjzRlwcf4oCUwqzigJ7QlRHQjmbRnCEbLMKxS8KpJlfQp9CSwqDQptCQ0pBINdGJXiMh0LxNeHocZtC4M9GG0L7QkdGURsKs0ZPCu9Cl0KHigKHQqOKAmdCF0YRCa3TCmBnRjdCn0JXQkdGAZ9CxHdKQRFDRh9GA0JvRlHjRiynQutGe0IJMfeKApgUI0Jk40ITQug9JA9C+VcKuwrF2L0XRgtCQ0JUjEtC3MHXQqF4mGMKwwphsSWrQml7QjtGb0LhgfdCr0IXRn1nQq3XQl9GJH3nQgUoGTgMAAA=="

        # data = base64.b64decode(base64_encoded)[5:]
        func = base64.b32decode
        func = base64.b64decode
        # func = base64.decode
        decoded = decode_base64_text(base64_encoded, func=func)
        start = decoded[:10]
        print(f"{start=}")

    elif special == "test_encoding":
        """
        Что ж такое я отправляю? Проверяю
        https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/
        """
        encoding = "ascii"
        message = "Привет мир"
        message = "Hello world"
        message = "Python is fun"
        encoded = encode_text_to_base64(message, encoding=encoding)
        print(f"{encoded=}")

        decoded = decode_base64_text(encoded, encoding=encoding)
        print(f"{decoded=}")

        print("-" * 100)
        message = "L2dldC8f4oC5CAAAAAAABABNUNCrSgMxENGN4oCifdCkBzXQq9GeUNC2wrVv0InQsCfQpFJw0I430Kxi0YHCp9GCDVrRi1QRL1TRgDHCtdCMZuKAnE3RmWQrFSrQpNC8DdCdQNCeOTNz4oCgYdC6ftClRwdnwqfRhWMU0Z4TXNCRFeKAnn3QilzRhNGTbsK30KFswrfQkn7Qv3IQ0L43ex04bw3QhEfigKEl0IUK0ZnRk9CuZcKp4oCg0IzQu9CKDtGTdjtodC4cZBrQs+KAusKYatCW4oCwNNGaRdCuKsKxMyXQsOKAkyxiJsKt4oCZ0IsZTtGDHNCMTOKAoNCKWOKAmFYUN9C+SwTigJxzGFHQjtCcUmkLI8K10ZLQiXpLJeKAndCz4oCaRsKp0LfQi9CYReKAoErRjMKsYEzSkTUwYTPQhHPQn9CULUAt0KzCq2/QhmByQz3Qk9CZ0ZkzeCDQljrigKHQrETRm9KQUjID0I9i0YvigJjQmtGHcnLihKIoFn/RntGDGdGTZ+KEonDQhNCxJdGH0Zgq0J5pVNCCZ9GYeMK7VjFM4oCm0KLCqWPQhHTRmgjQstGJMNCdRzjRiCQC0K7QmFdM0LwGdtCWOuKEojPRlAvQvtC+fnF74oCeMSpkwq1W0JMO0YbRjDTigKZxwpjCsdGeAdCOf8Kt0YnQm9Ct0LXigJ3RlyjQidGIF9Cz4oC6Nm/RgAEAAA=="
        message = "L2dldC8f4oC5CAAAAAAABABNUNCrSgMxENGN4oCifdCkBzXQq9GeUNC2wrVv0InQsCfQpFJw0I430Kxi0YHCp9GCDVrRi1QRL1TRgDHCtdCMZuKAnE3RmWQrFSrQpNC8DdCdQNCeOTNz4oCgYdC6ftClRwdnwqfRhWMU0Z4TXNCRFeKAnn3QilzRhNGTbsK30KFswrfQkn7Qv3IQ0L43ex04bw3QhEfigKEl0IUK0ZnRk9CuZcKp4oCg0IzQu9CKDtGTdjtodC4cZBrQs+KAusKYatCW4oCwNNGaRdCuKsKxMyXQsOKAkyxiJsKt4oCZ0IsZTtGDHNCMTOKAoNCKWOKAmFYUN9C+SwTigJxzGFHQjtCcUmkLI8K10ZLQiXpLJeKAndCz4oCaRsKp0LfQi9CYReKAoErRjMKsYEzSkTUwYTPQhHPQn9CULUAt0KzCq2/QhmByQz3Qk9CZ0ZkzeCDQljrigKHQrETRm9KQUjID0I9i0YvigJjQmtGHcnLihKIoFn/RntGDGdGTZ+KEonDQhNCxJdGH0Zgq0J5pVNCCZ9GYeMK7VjFM4oCm0KLCqWPQhHTRmgjQstGJMNCdRzjRiCQC0K7QmFdM0LwGdtCWOuKEojPRlAvQvtC+fnF74oCeMSpkwq1W0JMO0YbRjDTigKZxwpjCsdGeAdCOf8Kt0YnQm9Ct0LXigJ3RlyjQidGIF9Cz4oC6Nm/RgAEAAA=="
        message_bytes = message.encode(encoding)

        encoding = "utf-8"
        encoding = "ascii"
        encoding = "koi8-r"

        aliases0 = [
            "utf-8",
            "ascii",
            "koi8-r",
        ]
        print(f"have {len(aliases)} encodings")

        for num, encoding in enumerate(aliases, 1):
            # decoded = base64.decodebytes(message_bytes)
            try:
                decoded = decode_base64_text(message, encoding=encoding)
            except Exception as er:
                print(f"    -bad {encoding=}")
                continue

            print(
                f"{num}/{len(aliases)} {encoding}: {decoded=} {len(decoded)=}"
            )
            # wait_for_ok()
            # continue

            for cut_from in range(0, 100):
                body = decoded[cut_from:]
                if body == b"":
                    break

                want_decode = 0
                if want_decode:
                    try:
                        text = decode_gzip(body)
                        print(text)
                        wait_for_ok("encoded!")
                    except Exception as er:
                        # print(f"   bad {cut_from=}")
                        continue

                with open(
                    f"temp/decoded_{encoding}_{cut_from}", "wb"
                ) as file_to_save:

                    file_to_save.write(body)
