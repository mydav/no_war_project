from zipfile import ZipFile
import zlib
import hashlib


from modules import *

logger = get_logger(__name__)


def check_dir_and_zip_identical(d, f_zip, pwd=None, debug=False):
    """
    проверяем что папка идентична архиву
    """
    errors = []
    reason = ""
    if not file_exists(f_zip):
        errors.append(f"file {f_zip=} not exists")
    if not dir_exists(d):
        errors.append(f"dir {d=} not exists")

    if not errors:
        d_abs = os.path.abspath(d)
        zip_info = get_zip_info(f_zip, pwd)
        if debug:
            print("zip_info:")
            show_dict(zip_info)

        zip_files = []
        for name in zip_info:
            _ = zip_info[name]
            if not _["size"]:
                continue
            id = f'{name} {_["hash"]}'
            zip_files.append(id)
        if debug:
            logger.debug(f"{zip_files=}")

        dir_info = {}
        dir_files = []
        for f in get_all_file_names(d):
            # logger.debug(f"{f=}")
            name = f.replace(d_abs, "")[1:].replace("\\", "/")
            h = calc_hash_crc(f)
            _ = {
                "name": name,
                "hash": h,
            }
            id = f"{name} {h}"
            dir_info[name] = _
            dir_files.append(id)
        if debug:
            logger.debug(f"{dir_files=}")
        if debug:
            show_dict(dir_info)

        zip_files = set(zip_files)
        dir_files = set(dir_files)

        # возможно в зипе больше файлов
        more_in_zip = zip_files.difference(dir_files)
        if more_in_zip:
            errors.append(f"zip has more files {more_in_zip}")

        # возможно в папке больше файлов
        more_in_dir = dir_files.difference(zip_files)
        if more_in_dir:
            errors.append(f"dir has more files {more_in_dir}")

    status = True
    if errors:
        logger.debug(f"not equal data, {errors=}")
        status = False

    res = {
        "status": status,
    }
    if errors:
        res["error"] = errors

    logger.debug(f"identical {res=}")
    return res


def unpack_zipfile(
    filename, extract_dir, encoding="cp866", pwd=None, debug=False
):
    with ZipFile(filename) as archive:
        if pwd:
            archive.setpassword(pwd=bytes(pwd, "utf-8"))
        for entry in archive.infolist():
            name = entry.filename.encode("cp437").decode(
                encoding
            )  # reencode!!!
            if debug:
                logger.debug(f"extract {name=}")

            # don't extract absolute paths or ones with .. in them
            if name.startswith("/") or ".." in name:
                continue

            target = os.path.join(extract_dir, *name.split("/"))
            if debug:
                logger.debug(f"{target=}")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not entry.is_dir():  # file
                with archive.open(entry) as source, open(target, "wb") as dest:
                    shutil.copyfileobj(source, dest)

    if os.path.isdir(extract_dir):
        return True
    else:
        return False


def get_zip_info(f, pwd=None, encoding="cp866", debug=False):
    fun = "get_zip_info"
    # logger.debug(f"{fun} {f=} {pwd=}")
    info = {}
    with ZipFile(f, "r") as zipObj:
        if pwd:
            zipObj.setpassword(pwd=bytes(pwd, "utf-8"))

        blocksize = 1024 ** 2  # 1M chunks

        # Get list of ZipInfo objects
        listOfiles = zipObj.infolist()
        # Iterate of over the list of ZipInfo objects & access members of the object
        for elem in listOfiles:
            elem.filename = elem.filename.encode("cp437").decode(
                encoding
            )  # reencode!!!
            # logger.debug(f"extract {elem=}")
            if debug:
                logger.debug(
                    f"{elem.filename} : size{elem.file_size} date {elem.date_time} size {elem.compress_size}\n{elem}"
                )

            # md5
            # md5 = hashlib.md5()
            # while True:
            #     block = elem.read(blocksize)
            #     if not block:
            #         break
            #     md5.update(block)
            # h = md5.hexdigest()

            h = format(elem.CRC & 0xFFFFFFFF, "08x")

            info[elem.filename] = {
                "name": elem.filename,
                "size": elem.file_size,
                "compress_size": elem.compress_size,
                "data": elem.date_time,
                "hash": h,
            }
    return info


def calc_hash_crc(f):
    buffersize = 65536

    with open(f, "rb") as afile:
        buffr = afile.read(buffersize)
        crcvalue = 0
        while len(buffr) > 0:
            crcvalue = zlib.crc32(buffr, crcvalue)
            buffr = afile.read(buffersize)

    return format(crcvalue & 0xFFFFFFFF, "08x")  # a509ae4b


if __name__ == "__main__":
    f = r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks\a24c519b5deb4e0d4d9bdaed79878cf9.zip"
    f = r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks\real_zip_with_archive.zip"
    d_to = (
        r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks\разархивировал сюда"
    )
    pwd = "no_war"

    special = "unzip_to_directory"
    special = "calc_hash_crc"
    special = "get_zip_info"
    special = "check_dir_and_zip_identical"

    if special == "check_dir_and_zip_identical":
        d = r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks\разархивировал сюда"
        f = r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks\real_zip_with_archive.zip"
        info = check_dir_and_zip_identical(d=d, f_zip=f, pwd=pwd)
        logger.debug(f"identical {info=}")

    elif special == "get_zip_info":
        info = get_zip_info(f, pwd)
        logger.info(f"{info=}")

        f_one = r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks\!ЗАВДАННЯ\musor.xlsx"
        hash = calc_hash_crc(f_one)
        logger.info(f"{hash=}")

    elif special == "unzip_to_directory":
        # info = unzip_to_directory(f, d_to=d_to, pwd=pwd)
        info = unpack_zipfile(f, d_to, pwd=pwd)

    elif special == "calc_hash_crc":
        f = r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks\!ЗАВДАННЯ\musor.xlsx"
        info = calc_hash_crc(f)
        logger.debug(f"{info=}")

    else:
        logger.critical(f"unknown {special=}")

    os._exit(0)
