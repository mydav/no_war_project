#!/usr/bin/python
# -*- coding: utf-8 -*-

from modules import *

# from modules_mega import *
import json


class DirectoryFirefoxProfile:
    """
        класс для работы с физическим профилем - жестко прописываем там нужные значения
        как работают в Фаерфоксе настройки:
            https://developer.mozilla.org/en-US/docs/Mozilla/Preferences/A_brief_guide_to_Mozilla_preferences
    """

    def __init__(self, d=""):
        self.d = d

    @property
    def exists(self):
        return dir_exists(self.d)

    def delete_preference(self, key):
        """
            находим старую строку и удаляем ее
            Preference conflicts are resolved in favor of the last entry; for example, user.js takes precedence over prefs.js .
        """
        fun = "delete_preference"
        f_settings = self.get_file_path("user.js")
        logger.debug("	[%s %s f=`%s`" % (fun, key, f_settings))
        if not self.exists:
            logger.error("ERROR  - file %s not exists" % (f_settings))
            return False

        files = [
            self.get_file_path("prefs.js"),
            f_settings,
        ]

        for f in files:
            # user_pref("marionette.port", 56578);
            f_name = os.path.basename(f)

            if file_exists(f):
                txt = self.read_file(f_name)

                t = 1
                t = 0
                if t:
                    logger.debug("txt=%s" % txt)
                    wait_for_ok()

                lines = txt.split("\n")
            else:
                lines = []
                if not file_exists(self.get_file_path("prefs.js")):
                    wait_for_ok("no file %s?" % f)

            new_lines = []
            for line in clear_list(lines):
                started = 'user_pref("%s",' % key
                if line.find(started) == 0:
                    continue
                # found_pref = 1
                # wait_for_ok(line)

                new_lines.append(line)

            # show_list(new_lines)
            # wait_for_ok()

            new_txt = "\n".join(new_lines)
            self.write_file(new_txt, f)
        # wait_for_ok('saved to %s' % f)

        # logger.debug("+]")
        return True

    def set_preference(self, key, value=""):
        """
            находим старую строку, заменяем на новую
            Preference conflicts are resolved in favor of the last entry; for example, user.js takes precedence over prefs.js .
        """
        fun = "set_preference"
        f_settings = self.get_file_path("user.js")
        logger.debug("	[%s %s=%s in f=`%s`" % (fun, key, value, f_settings))
        if not self.exists:
            logger.error("ERROR  - file %s not exists" % (f_settings))
            return False

        files = [
            #'prefs.js',
            f_settings,
        ]

        for f in files:
            # user_pref("marionette.port", 56578);
            f_name = os.path.basename(f)

            if file_exists(f):
                txt = self.read_file(f_name)

                t = 1
                t = 0
                if t:
                    logger.debug("txt=%s" % txt)
                    wait_for_ok()

                lines = txt.split("\n")
            else:
                lines = []

                if not file_exists(self.get_file_path("prefs.js")):
                    wait_for_ok("no file %s?" % f)

            # collect all linex except our
        new_lines = []
        for line in clear_list(lines):
            started = 'user_pref("%s",' % key
            if line.find(started) == 0:
                continue
            # line = self.generate_pref_line(key, value)
            # found_pref = 1
            # wait_for_ok(line)

            new_lines.append(line)

        # add new actual line
        line = self.generate_pref_line(key, value)
        new_lines.append(line)
        # wait_for_ok(line)

        # show_list(new_lines)
        # wait_for_ok()

        new_txt = "\n".join(new_lines)
        self.write_file(new_txt, f)
        # wait_for_ok('saved to %s' % f)

        # logger.debug("+]")
        return True

    def _read_existing_userjs(self, f_name="user.js"):
        import warnings

        f_path = self.get_file_path(f_name)
        logger.debug("f_path %s" % f_path)
        dct = {}

        PREF_RE = re.compile(r'user_pref\("(.*)",\s(.*)\)')
        try:
            with open(f_path) as f:
                for usr in f:
                    matches = re.search(PREF_RE, usr)
                    try:
                        dct[matches.group(1)] = json.loads(matches.group(2))
                    except Exception:
                        warnings.warn(
                            "(skipping) failed to json.loads existing preference: "
                            + matches.group(1)
                            + matches.group(2)
                        )
        except Exception:
            # The profile given hasn't had any changes made, i.e no users.js
            warnings.warn("problem with file %s" % f_path)
            pass

        return dct

    def read_file(self, name=""):
        return text_from_file(self.get_file_path(name))

    def write_file(self, text="", name=""):
        return text_to_file(text, self.get_file_path(name))

    def get_file_path(self, name=""):
        if name.find(self.d) != -1:
            return name
        else:
            return "%s/%s" % (self.d, self.get_file_name(name))

    def get_file_name(self, name=""):
        if name == "":
            name = "user.js"
        return name

    def generate_pref_line(self, key, value):
        return 'user_pref("%s", %s);' % (key, json.dumps(value))


@property
def path(self):
    """
    Gets the profile directory that is currently being used
    """
    return self.d


if __name__ == "__main__":
    # profile_path = r'g:\!data\!firefox_profiles\rust_mozprofile.fQ6mvxDgBPDy'
    profile_path = r"g:\!data\!firefox_profiles\rust_mozprofile.test"
    spec = "test DirectoryFirefoxProfile"

    marionette_port = 56578

    if spec == "test DirectoryFirefoxProfile":
        profile = DirectoryFirefoxProfile(profile_path)
        logger.debug("profile: %s" % profile)

        t = 0
        t = 1
        if t:
            if profile.exists:
                profile.set_preference("nah", True)
                profile.set_preference("marionette.port", marionette_port)
            # wait_for_ok()

        t = 0
        t = 1
        if t:
            Show_step("check results of updating")
            dct = profile._read_existing_userjs()
            # show_dict(dct)
            keys_to_show = [
                "marionette.port",
                "nah",
            ]

            for k in keys_to_show:
                logger.debug("  %s=%s" % (k, dct[k]))

        t = 1
        t = 0
        if t:
            wait_for_ok(profile.exists)
