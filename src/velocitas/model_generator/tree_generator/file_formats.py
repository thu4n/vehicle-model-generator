# Copyright (c) 2023-2024 Contributors to the Eclipse Foundation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

import json
from abc import abstractmethod
from typing import List

from vss_tools import log
from vss_tools.vspec.main import load_quantities_and_units
from vss_tools.vspec.main import get_trees
from vss_tools.vspec.tree import build_tree, ModelValidationException
from vss_tools.vspec.vspec import load_vspec
# from vss_tools.vspec.model import 
from pathlib import Path


from velocitas.model_generator.tree_generator.constants import JSON, VSPEC

# supported file formats
formats = [VSPEC, JSON]


class FileFormat:
    def __init__(self, file_path: str):
        self.file_path = file_path

    # method to override when adding a new format
    @abstractmethod
    def load_tree(self):
        pass


class Vspec(FileFormat):
    def __init__(
        self,
        file_path: str,
        unit_file_path_list: List[str],
        quantities_file_path_list: List[str],
        include_dirs: List,
        strict: bool,
        overlays: List[str],
    ):
        super().__init__(file_path)
        self.unit_file_path_list = unit_file_path_list
        self.include_dirs = include_dirs
        self.strict = strict
        self.overlays = overlays
        self.quantities_file_path_list = quantities_file_path_list


    def load_tree(self):
        """loads a tree of a vspec file through vss-tools"""
        print("Loading vspec...")

        include_dir_paths = [Path(include_dir) for include_dir in self.include_dirs]
        vspec_path = Path(self.file_path)
        print("Include ", include_dir_paths)
        unit_files = [Path(unit_file) for unit_file in self.unit_file_path_list]
        quantities_files = [Path(quantities_file) for quantities_file in self.quantities_file_path_list]
        if len(self.overlays) > 0:
            print(f"Applying VSS overlay...")
            tree, _ = get_trees(
                vspec=vspec_path,
                include_dirs=include_dir_paths,
                strict=self.strict,
                expand=False,
                overlays=self.overlays,
                units=unit_files,
                quantities=quantities_files
            )

        else:
            tree, _ = get_trees(
                vspec=vspec_path, 
                include_dirs=include_dir_paths,
                strict=self.strict,
                expand=False,
                units=unit_files,
                quantities=quantities_files
            )

        return tree


class Json(FileFormat):
    def __init__(self, file_path: str, unit_file_path_list: List[str], quantities_file_path_list: List[str]):
        super().__init__(file_path)
        self.unit_file_path_list = unit_file_path_list
        self.quantities_file_path_list = quantities_file_path_list

    # VSS nodes have a field "$file_name",
    # so it needs to be added for the vss-tools to work
    def __extend_fields(self, d: dict):
        if "children" in d:
            for child_d in d["children"].values():
                self.__extend_fields(child_d)
        d["$file_name$"] = ""
        return
    
    def load_tree(self):
        """loads a tree of a json file through vss-tools"""
        print("Loading json...")
        output_json = json.load(open(self.file_path))
        self.__extend_fields(next(iter(output_json.values())))
        print("Generating tree from json...")
        unit_files = [Path(unit_file) for unit_file in self.unit_file_path_list]
        quantities_files = [Path(quantities_file) for quantities_file in self.quantities_file_path_list]
        
        try:
            load_quantities_and_units(quantities_files, unit_files, "")
        except ModelValidationException as e:
            log.critical(e)
            exit(1)
        # vspec_data = load_vspec( [vspec] + list(overlays))
        tree, _ = build_tree(output_json)
        return tree
