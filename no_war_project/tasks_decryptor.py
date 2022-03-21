from no_war_project.settings import *
from modules import *
from data_hider.steganograph.tupo_append_to_image import ImageHider
from archives.zip_funcs import *


logger = get_logger(__name__)


class HiderUnziper:
    name = "HiderUnziper"

    def __init__(
        self,
        d=None,
        d_raw_tasks=None,
        d_decrypted=None,
        d_tasks=None,
        pwd=None,
    ):
        """
        :param d:  папка абсолютная
        :param d_raw_tasks: качнули сюда картинки
        :param d_decrypted: с картинок сюда вытянули архивы
        :param d_tasks: с архивов вытянули папки
        :param pwd: пароль на архив
        """
        self.pwd = pwd

        if d is None:
            d = get_f_here("temp/tasks")
        self.d = d

        if not d_raw_tasks:
            d_raw_tasks = f"{self.d}/raw_tasks"
        self.d_raw_tasks = d_raw_tasks

        if not d_decrypted:
            d_decrypted = f"{self.d}/decrypted_tasks"
        self.d_decrypted = d_decrypted

        if not d_tasks:
            d_tasks = f"{self.d}/tasks"
        self.d_tasks = d_tasks

        self.hider = ImageHider()
        # logger.info(f"{self} {self.d_raw_tasks=}")
        # os._exit(0)

    def return_identical_directories(self):
        """проверяю какие папки точно идентичные - файлы только с них буду обрабатывать
        враг не подбросит свои...
        """
        d_names = get_dirNames_level_0(self.d_tasks)
        logger.debug(f"have {len(d_names)} auto dirs {d_names=}")
        identicals = []
        for d_name in d_names:
            d_full = f"{self.d_tasks}/{d_name}"
            f_zip = f"{self.d_decrypted}/{d_name}.zip"
            if not file_exists(f_zip):
                logger.debug(f"not exists {f_zip=}, so skip {d_full=}")
                continue

            r_is_identical = check_dir_and_zip_identical(
                d_full, f_zip, pwd=self.pwd
            )
            is_identical = r_is_identical["status"]
            if is_identical:
                identicals.append(d_full)
            else:
                logger.error(f"{d_full=} differs from {f_zip=}")
                if 0:
                    rmdir(d_full)
                    rmfile(f_zip)
        return identicals

    def unzip_dir(self, d=None, d_to=None):
        if d is None:
            d = self.d_decrypted

        if d_to is None:
            d_to = self.d_tasks

        files = get_all_file_names(d)
        for num, f in enumerate(files, 1):
            # logger.debug(f'{num}/{len(files)} {f=}')
            file_name = os.path.basename(f)
            if not file_name.endswith(".zip"):
                logger.warning(f"   file {f} not .zip, so skip")
                continue

            d_name = file_name.split(".")[0]
            d_to_full = f"{d_to}/{d_name}"

            status = None
            # status = unpack_zipfile(f, d_to_full, pwd=self.pwd)
            try:
                status = unpack_zipfile(f, d_to_full, pwd=self.pwd)
            except Exception as er:
                error = str(er)
                logger.debug0(f"unzip error on {f=}, {er=}")
                if "Bad password for file" in error:
                    logger.debug(f"wrong password on file, so delete file {f}")
                    rmfile(f)

            logger.debug(
                f"{num}/{len(files)} unzip {status=} to directory {d_to_full} from file {f=}"
            )

    def decrypt_dir(self, d=None, d_to=None):
        fun = "decrypt_dir"
        if not d:
            d = self.d_raw_tasks
        if not d_to:
            d_to = self.d_decrypted

        files = get_all_file_names(d)
        cnt_good = 0
        for num, f in enumerate(files, 1):
            # logger.debug(f'{num}/{len(files)} {f=}')
            decrypted = None
            try:
                decrypted = self.decrypt_file_to_dir(f, d_to)
                cnt_good += 1
            except Exception as er:
                logger.warning(f"decrypt error on {f=}, {er=}")
            logger.debug(f"{num}/{len(files)} {decrypted=} for {f=}")
        logger.debug(f"+{fun} {cnt_good}/{len(files)} good, {d=} to {d_to=}")

    def decrypt_file_to_dir(self, f=r"", d_to=None):
        if not d_to:
            d_to = self.d_decrypted

        name = os.path.basename(f).split(".")[0]
        f_new = f"{d_to}/{name}.zip"

        decrypted = self.hider.decrypt(f, f_new)
        logger.debug(f"         {decrypted=} to {f_new}")
        return decrypted

    def __repr__(self):
        return f"<{self.name}, d={self.d}>"


if __name__ == "__main__":
    special = "decrypt_file_to_dir"
    special = "return_identical_directories"
    special = "decrypt_dir"

    pwd = "no_war"
    hider = HiderUnziper(pwd=pwd)

    if special == "decrypt_dir":
        d = r"s:\!kyxa\!code\no_war\temp\tasks"

        t = 1
        if t:
            r = hider.decrypt_dir()
            logger.info(f"decrypted directory {r=}")

        r = hider.unzip_dir()
        logger.info(f"unzip directory {r=}")

        r = hider.return_identical_directories()
        logger.info(f"identical directories {r=}")

    elif special == "return_identical_directories":
        r = hider.return_identical_directories()
        logger.info(f"identical directories {r=}")

    elif special == "decrypt_file_to_dir":
        f = r"s:\!kyxa\!code\no_war\temp\tasks\raw_tasks\a24c519b5deb4e0d4d9bdaed79878cf9.jpg"
        f = r"s:\!kyxa\!code\no_war\temp\tasks\raw_tasks\a24c519b5deb4e0d4d9bdaed79878cf9.jpg"
        d_to = r"s:\!kyxa\!code\no_war\temp\tasks\decrypted_tasks"

        d_to = r"s:\!kyxa\!code\no_war\!ЗАВДАННЯ\авто"
        d_to = None

        logger.debug(f"{hider=}")

        res = hider.decrypt_file_to_dir(f, d_to)
        logger.info(f"{res=}")
