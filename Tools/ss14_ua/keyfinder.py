import typing
import logging

from pydash import py_

from file import FluentFile
from fluentast import FluentAstAbstract
from fluentformatter import FluentFormatter
from project import Project
from fluent.syntax import ast, FluentParser, FluentSerializer



######################################### Class defifitions ############################################################
class RelativeFile:
    def __init__(self, file: FluentFile, locale: typing.AnyStr, relative_path_from_locale: typing.AnyStr):
        self.file = file
        self.locale = locale
        self.relative_path_from_locale = relative_path_from_locale


class FilesFinder:
    def __init__(self, project: Project):
        self.project: Project = project
        self.created_files: typing.List[FluentFile] = []

    def get_relative_path_dict(self, file: FluentFile, locale):
        if locale == 'uk-UA':
            return RelativeFile(file=file, locale=locale,
                                relative_path_from_locale=file.get_relative_path(self.project.uk_locale_dir_path))
        elif locale == 'en-US':
            return RelativeFile(file=file, locale=locale,
                                relative_path_from_locale=file.get_relative_path(self.project.en_locale_dir_path))
        else:
            raise Exception(f'Локаль {locale} не підтримується')

    def get_file_pair(self, en_file: FluentFile) -> typing.Tuple[FluentFile, FluentFile]:
        uk_file_path = en_file.full_path.replace('en-US', 'uk-UA')
        uk_file = FluentFile(uk_file_path)

        return en_file, uk_file

    def execute(self):
        self.created_files = []
        groups = self.get_files_pars()
        keys_without_pair = list(filter(lambda g: len(groups[g]) < 2, groups))

        for key_without_pair in keys_without_pair:
            relative_file: RelativeFile = groups.get(key_without_pair)[0]

            if relative_file.locale == 'en-US':
                uk_file = self.create_uk_analog(relative_file)
                self.created_files.append(uk_file)
            elif relative_file.locale == 'uk-UA':
                is_engine_files = "robust-toolbox" in (relative_file.file.full_path)
                if not is_engine_files:
                    self.warn_en_analog_not_exist(relative_file)
            else:
                raise Exception(f'Файл {relative_file.file.full_path} має невідому локаль "{relative_file.locale}"')

        return self.created_files

    def get_files_pars(self):
        en_fluent_files = self.project.get_fluent_files_by_dir(project.en_locale_dir_path)
        uk_fluent_files = self.project.get_fluent_files_by_dir(project.uk_locale_dir_path)

        en_fluent_relative_files = list(map(lambda f: self.get_relative_path_dict(f, 'en-US'), en_fluent_files))
        uk_fluent_relative_files = list(map(lambda f: self.get_relative_path_dict(f, 'uk-UA'), uk_fluent_files))
        relative_files = py_.flatten_depth(py_.concat(en_fluent_relative_files, uk_fluent_relative_files), depth=1)

        return py_.group_by(relative_files, 'relative_path_from_locale')

    def create_uk_analog(self, en_relative_file: RelativeFile) -> FluentFile:
        en_file: FluentFile = en_relative_file.file
        en_file_data = en_file.read_data()
        uk_file_path = en_file.full_path.replace('en-US', 'uk-UA')
        uk_file = FluentFile(uk_file_path)
        uk_file.save_data(en_file_data)

        logging.info(f'Створено файл {uk_file_path} з перекладом з англійськго файлу')

        return uk_file

    def warn_en_analog_not_exist(self, uk_relative_file: RelativeFile):
        file: FluentFile = uk_relative_file.file
        en_file_path = file.full_path.replace('uk-UA', 'en-US')

        logging.warning(f'Файл {file.full_path} не має англійськго аналогу за шляхом {en_file_path}')


class KeyFinder:
    def __init__(self, files_dict):
        self.files_dict = files_dict
        self.changed_files: typing.List[FluentFile] = []

    def execute(self) -> typing.List[FluentFile]:
        self.changed_files = []
        for pair in self.files_dict:
            uk_relative_file = py_.find(self.files_dict[pair], {'locale': 'uk-UA'})
            en_relative_file = py_.find(self.files_dict[pair], {'locale': 'en-US'})

            if not en_relative_file or not uk_relative_file:
                continue

            uk_file: FluentFile = uk_relative_file.file
            en_file: FluentFile = en_relative_file.file

            self.compare_files(en_file, uk_file)

        return self.changed_files


    def compare_files(self, en_file, uk_file):
        uk_file_parsed: ast.Resource = uk_file.parse_data(uk_file.read_data())
        en_file_parsed: ast.Resource = en_file.parse_data(en_file.read_data())

        self.write_to_uk_files(uk_file, uk_file_parsed, en_file_parsed)
        self.log_not_exist_en_files(en_file, uk_file_parsed, en_file_parsed)


    def write_to_uk_files(self, uk_file, uk_file_parsed, en_file_parsed):
        for idx, en_message in enumerate(en_file_parsed.body):
            if isinstance(en_message, ast.ResourceComment) or isinstance(en_message, ast.GroupComment) or isinstance(en_message, ast.Comment):
                continue

            uk_message_analog_idx = py_.find_index(uk_file_parsed.body, lambda uk_message: self.find_duplicate_message_id_name(uk_message, en_message))
            have_changes = False

            # Attributes
            if getattr(en_message, 'attributes', None) and uk_message_analog_idx != -1:
                if not uk_file_parsed.body[uk_message_analog_idx].attributes:
                    uk_file_parsed.body[uk_message_analog_idx].attributes = en_message.attributes
                    have_changes = True
                else:
                    for en_attr in en_message.attributes:
                        uk_attr_analog = py_.find(uk_file_parsed.body[uk_message_analog_idx].attributes, lambda uk_attr: uk_attr.id.name == en_attr.id.name)
                        if not uk_attr_analog:
                            uk_file_parsed.body[uk_message_analog_idx].attributes.append(en_attr)
                            have_changes = True

            # New elements
            if uk_message_analog_idx == -1:
                uk_file_body = uk_file_parsed.body
                if (len(uk_file_body) >= idx + 1):
                    uk_file_parsed = self.append_message(uk_file_parsed, en_message, idx)
                else:
                    uk_file_parsed = self.push_message(uk_file_parsed, en_message)
                have_changes = True

            if have_changes:
                serialized = serializer.serialize(uk_file_parsed)
                self.save_and_log_file(uk_file, serialized, en_message)

    def log_not_exist_en_files(self, en_file, uk_file_parsed, en_file_parsed):
        for idx, uk_message in enumerate(uk_file_parsed.body):
            if isinstance(uk_message, ast.ResourceComment) or isinstance(uk_message, ast.GroupComment) or isinstance(uk_message, ast.Comment):
                continue

            en_message_analog = py_.find(en_file_parsed.body, lambda en_message: self.find_duplicate_message_id_name(uk_message, en_message))

            if not en_message_analog:
                logging.warning(f'Ключ "{FluentAstAbstract.get_id_name(uk_message)}" не має англійськго аналогу за шляхом {en_file.full_path}"')

    def append_message(self, uk_file_parsed, en_message, en_message_idx):
        uk_message_part_1 = uk_file_parsed.body[0:en_message_idx]
        uk_message_part_middle = [en_message]
        uk_message_part_2 = uk_file_parsed.body[en_message_idx:]
        new_body = py_.flatten_depth([uk_message_part_1, uk_message_part_middle, uk_message_part_2], depth=1)
        uk_file_parsed.body = new_body

        return uk_file_parsed

    def push_message(self,  uk_file_parsed, en_message):
        uk_file_parsed.body.append(en_message)
        return uk_file_parsed

    def save_and_log_file(self, file, file_data, message):
        file.save_data(file_data)
        logging.info(f'В файл {file.full_path} доданий ключ "{FluentAstAbstract.get_id_name(message)}"')
        self.changed_files.append(file)

    def find_duplicate_message_id_name(self, uk_message, en_message):
        uk_element_id_name = FluentAstAbstract.get_id_name(uk_message)
        en_element_id_name = FluentAstAbstract.get_id_name(en_message)

        if not uk_element_id_name or not en_element_id_name:
            return False

        if uk_element_id_name == en_element_id_name:
            return uk_message
        else:
            return None

######################################## Var definitions ###############################################################

logging.basicConfig(level = logging.INFO)
project = Project()
parser = FluentParser()
serializer = FluentSerializer(with_junk=True)
files_finder = FilesFinder(project)
key_finder = KeyFinder(files_finder.get_files_pars())

########################################################################################################################

print('Перевірка актуальності файлів ...')
created_files = files_finder.execute()
if len(created_files):
    print('Форматування створених файлів ...')
    FluentFormatter.format(created_files)
print('Перевірка актуальності ключів ...')
changed_files = key_finder.execute()
if len(changed_files):
    print('Форматування зміннених файлів ...')
    FluentFormatter.format(changed_files)
