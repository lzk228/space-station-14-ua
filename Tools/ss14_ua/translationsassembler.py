import logging
import typing

from fluent.syntax import FluentParser, FluentSerializer
from pydash import py_

from file import FluentFile
from fluentast import FluentSerializedMessage
from lokalise_fluent_ast_comparer_manager import LokaliseFluentAstComparerManager
from lokalise_project import LokaliseProject
from lokalisemodels import LokaliseKey
import os

######################################### Class defifitions ############################################################

class TranslationsAssembler:
    def __init__(self, items: typing.List[LokaliseKey]):
        self.group = py_.group_by(items, 'key_base_name')
        keys = list(self.group.keys())
        self.sorted_keys = py_.sort_by(keys, lambda key: self.sort_by_translations_timestamp(self.group[key]),
                                       reverse=True)

    def execute(self):
        for keys in self.group:
            full_message = FluentSerializedMessage.from_lokalise_keys(self.group[keys])
            parsed_message = FluentParser().parse(full_message)
            uk_full_path = self.group[keys][0].get_file_path().uk
            uk_file = FluentFile(uk_full_path)
            try:
                uk_file_parsed = uk_file.read_parsed_data()
            except:
                logging.error(f'Файл {uk_file.full_path} не існує')
                continue

            manager = LokaliseFluentAstComparerManager(sourse_parsed=uk_file_parsed, target_parsed=parsed_message)

            for_update = manager.for_update()
            for_create = manager.for_create()
            for_delete = manager.for_delete()

            if len(for_update):
                updated_uk_file_parsed = manager.update(for_update)
                updated_uk_file_serialized = FluentSerializer(with_junk=True).serialize(updated_uk_file_parsed)
                uk_file.save_data(updated_uk_file_serialized)

                updated_keys = list(map(lambda el: el.get_id_name(), for_update))
                logging.info(f'Оновлені ключі: {updated_keys} в файлі {uk_file.full_path}')

    def sort_by_translations_timestamp(self, list):
        sorted_list = py_.sort_by(list, 'data.translations_modified_at_timestamp', reverse=True)

        return sorted_list[0].data.translations_modified_at_timestamp

######################################## Var definitions ###############################################################

logging.basicConfig(level=logging.INFO)
lokalise_project_id = os.getenv('lokalise_project_id')
lokalise_personal_token = os.getenv('lokalise_personal_token')
lokalise_project = LokaliseProject(project_id=lokalise_project_id,
                                   personal_token=lokalise_personal_token)
all_keys: typing.List[LokaliseKey] = lokalise_project.get_all_keys()
translations_assembler = TranslationsAssembler(all_keys)

########################################################################################################################

translations_assembler.execute()
