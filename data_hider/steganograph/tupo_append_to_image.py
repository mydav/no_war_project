import os


class ImageHider:
    def __init__(self, delimiter=b"START_OF_HIDDEN_DATA"):
        self.delimiter = delimiter

    def decrypt(self, f, f_to, data=None):
        if not f and not data:
            return False

        if not data:
            with open(f, "rb") as fp:
                data = fp.read()

        parts = data.split(self.delimiter)
        secret_data = parts[-1]

        return self.write_to_file(secret_data, f_to)

    def hide(self, f_data, f_image, f_to):
        """
        прячем инфу в картинку
        """
        with open(f_image, "rb") as fp:
            data1 = fp.read()
        with open(f_data, "rb") as fp:
            data2 = fp.read()

        data = data1
        data += self.delimiter
        data += data2

        return self.write_to_file(data, f_to)

    def write_to_file(self, data, f_to):
        self.create_directory(os.path.dirname(f_to))
        with open(f_to, "wb") as fp:
            fp.write(data)
        if os.path.isfile(f_to):
            return True
        return False

    def create_directory(self, d=""):
        if not os.path.isdir(d):
            os.makedirs(d)


if __name__ == "__main__":
    hider = ImageHider()
    f_with_image = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\data_hider\steganograph\data\stego_image.png"
    f_with_image = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\data_hider\steganograph\temp\image_with_secret.jpg"
    f_to = "temp/real_data.zip"

    f_data = r"s:\!kyxa\!code\no_war\no_war.zip"
    f_secret_image = r"temp/image_with_secret.jpg"

    f_data = r"s:\!kyxa\!code\no_war\!ЗАВДАННЯ - СЛАВА УКРАЇНІ.zip"
    f_data = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\data_hider\steganograph\temp\real_tasks.zip"
    f_secret_image = r"temp/image_with_secret.jpg"

    f_raw_image = r"s:\!kyxa\!code\!documentation\py4seo\advanced\08\dor_minimum\data_hider\steganograph\data\no_war_raw.jpg"

    t = 1
    if t:
        hide = hider.hide(f_data, f_raw_image, f_secret_image)
        print(f"{hide=}")

        f_new = r"temp/decrypted.zip"
        decrypted = hider.decrypt(f_secret_image, f_new)
        print(f"{decrypted=}")

    t = 0
    if t:
        f_secret_image = r"s:\!kyxa\!code\no_war\temp\tasks\raw_tasks\a24c519b5deb4e0d4d9bdaed79878cf9.jpg"
        f_new = f"temp/secret_archive.zip"
        decrypted = hider.decrypt(f_secret_image, f_new)
        print(f"{decrypted=}")
