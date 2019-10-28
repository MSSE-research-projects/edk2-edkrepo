#!/usr/bin/env python3
#
## @file
# config_factory.py
#
# Copyright (c) 2017- 2019, Intel Corporation. All rights reserved.<BR>
# SPDX-License-Identifier: BSD-2-Clause-Patent
#

import os
import sys
import configparser
import collections
from edkrepo.common.edkrepo_exception import EdkrepoGlobalConfigNotFoundException, EdkrepoConfigFileInvalidException
from edkrepo.common.edkrepo_exception import EdkrepoWorkspaceInvalidException, EdkrepoGlobalDataDirectoryNotFoundException
from edkrepo.common.edkrepo_exception import EdkrepoConfigFileReadOnlyException
from edkrepo.common.humble import MIRROR_PRIMARY_REPOS_MISSING, MIRROR_DECODE_WARNING, MAX_PATCH_SET_INVALID
from edkrepo_manifest_parser import edk_manifest
from ctypes import *

def get_edkrepo_global_data_directory():
    global_data_dir = None
    if sys.platform == "win32":
        shell32 = oledll.shell32
        SHGetFolderPath = shell32.SHGetFolderPathW
        SHGetFolderPath.argtypes = [c_void_p, c_uint32, c_void_p, c_uint32, c_wchar_p]
        CSIDL_COMMON_APPDATA = 0x0023
        SHGFP_TYPE_CURRENT = 0
        MAX_PATH = 260
        common_appdata = create_unicode_buffer(MAX_PATH)
        SHGetFolderPath(None, CSIDL_COMMON_APPDATA, None, SHGFP_TYPE_CURRENT, common_appdata)
        global_data_dir = os.path.join(common_appdata.value, "edkrepo")
    elif sys.platform == "darwin":
        raise OSError("macOS support is in progress")
    elif sys.platform.startswith("linux") or os.name == "posix":
        global_data_dir = os.path.expanduser("~/.edkrepo")
    if not os.path.isdir(global_data_dir):
        if not os.path.exists(os.path.dirname(global_data_dir)):
            raise EdkrepoGlobalDataDirectoryNotFoundException("{} does not exist".format(os.path.dirname(global_data_dir)))
        os.mkdir(global_data_dir)
    return global_data_dir

# Data structure used to describe configuration properties and associated values
class CfgProp():
    """
    Describes a configuration file property.  This may include a default value, property name and if
    the value is required to already exist in the file.

    If required is True the section and key must exist in the configuration file at the time it is processed.
    If a default is provided it will be used to create a missing entry in a writeable file.
    """
    def __init__(self, section, key, prop_name, default=None, required=False):
        self.section = section
        self.key = key
        self.default = default
        self.name = prop_name
        self.required = required

def cfg_property(filename, cfg, read_only, section, key):
    """
    CFG property factory.  This function dynamically generates get/set properties based on the input
    parameters provided to the function.  A new property object is returned.
    """
    def _get(self):
        return cfg[section][key]
    def _set(self, value):
        if read_only:
            raise EdkrepoConfigFileReadOnlyException('The configuration file is read only: {}'.format(filename))
        cfg[section][key] = value
        with open(filename, 'w') as cfg_stream:
            cfg.write(cfg_stream)
    return property(_get, _set)

class BaseConfig():
    """
    Base class used to verify the contents of a configuration file and generate get/set properties
    for the class.  Property generation and verification is based off of a list of CfgProp classes.
    """
    prop_list = []
    def __init__(self, filename, read_only=True):
        # Do basic initialization of private variables
        self.read_only = read_only
        self.filename = filename
        self.cfg = configparser.ConfigParser(allow_no_value=True, delimiters='=')
        if os.path.isfile(self.filename):
            self.cfg.read(self.filename)

        # Create properties defined by the prop_list
        cfg_updated = False
        for prop in self.prop_list:
            # Verify config entry exists and create missing enties if file is not read only
            if prop.section not in self.cfg or prop.key not in self.cfg[prop.section]:
                if prop.required or self.read_only:
                    # Required property is missing
                    raise EdkrepoConfigFileInvalidException('{} is not present in {} section of {}'.format(prop.key, prop.section, os.path.basename(self.filename)))
                if not self.read_only:
                    # Create the missing property
                    if prop.section not in self.cfg:
                        self.cfg[prop.section] = {}
                    self.cfg[prop.section][prop.key] = prop.default
                    cfg_updated = True
            # Create property for that entry if a name was provided
            if prop.name is not None:
                setattr(BaseConfig, prop.name, cfg_property(self.filename, self.cfg, self.read_only, prop.section, prop.key))
        # Make sure file is up to date
        if cfg_updated:
            with open(self.filename, 'w') as cfg_stream:
                self.cfg.write(cfg_stream)

class GlobalConfig(BaseConfig):
    """
    Class access structure for the edkrepo.cfg file.  This file is read only and maintained by the
    edkrepo installer.
    """
    def __init__(self):
        self.edkrepo_global_data_directory = get_edkrepo_global_data_directory()
        self.filename = os.path.join(self.edkrepo_global_data_directory, "edkrepo.cfg")
        self.prop_list = [
                CfgProp('manifest-repo', 'URL', 'manifest_repo_url', None, True),
                CfgProp('manifest-repo', 'Branch', 'manifest_repo_branch', None, True),
                CfgProp('manifest-repo', 'LocalPath', 'manifest_repo_local_path', None, True),
                CfgProp('sparsecheckout', 'always_include', 'sparsecheckout_always_include', None, True),
                CfgProp('sparsecheckout', 'always_exclude', 'sparsecheckout_always_exclude', None, True),
                CfgProp('f2f-cherry-pick', 'ignored_folder_substrings', 'f2f_cp_ignored_folder_substrings'),
                CfgProp('git-ver', 'minimum', 'minimum_req_git_ver', None, True),
                CfgProp('git-ver', 'recommended', 'rec_git_ver', None, True),
                CfgProp('command-packages', 'packages', 'command_packages', None, True),
                CfgProp('preferred-command-package', 'preferred-package', 'pref_pkg', None, True)]
        if not os.path.isfile(self.filename):
            raise EdkrepoGlobalConfigNotFoundException("edkrepo global config file {} does not exist".format(self.filename))
        super().__init__(self.filename, True)

    @property
    def command_packages_list(self):
        initial_list = self.command_packages.split('|')
        pkg_list = []
        for pkg in initial_list:
            pkg_list.append(pkg.strip())
        return pkg_list

    @property
    def manifest_repo_abs_local_path(self):
        """Provides an absolute path to the manifest repo based on configuration file values."""
        return os.path.join(self.edkrepo_global_data_directory, self.manifest_repo_local_path)

    @property
    def sparsecheckout_data(self):
        always_include = self.sparsecheckout_always_include.split('|')
        always_exclude = self.sparsecheckout_always_exclude.split('|')
        return (always_include, always_exclude)

    @property
    def scm_geo_list(self):
        return self.scm_geos.split(',')

    @property
    def f2f_cp_ignored_folders(self):
        return self.f2f_cp_ignored_folder_substrings.split('|')

class GlobalUserConfig(BaseConfig):
    """
    Class access structure for the edkrepo_user.cfg file.  This file may be modified by the user and is
    generated automatically if not found.
    """
    def __init__(self):
        self.filename = os.path.join(get_edkrepo_global_data_directory(), "edkrepo_user.cfg")
        self.prop_list = [
            CfgProp('scm', 'mirror_geo', 'geo', 'none', False),
            CfgProp('send-review', 'max-patch-set', 'max_patch_set', '10', False)
            ]
        super().__init__(self.filename, False)

    @property
    def max_patch_set_int(self):
        try:
            return int(self.max_patch_set)
        except:
            raise EdkrepoConfigFileInvalidException(MAX_PATCH_SET_INVALID)

def get_workspace_path():
    path = os.path.realpath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(path, "repo")):
            if os.path.isfile(os.path.join(os.path.join(path, "repo"), "Manifest.xml")):
                return path
        if os.path.dirname(path) == path:
            break
        path = os.path.dirname(path)
    raise EdkrepoWorkspaceInvalidException("The current directory does not appear to be a valid workspace")

def get_workspace_manifest_file():
    path = get_workspace_path()
    return os.path.join(os.path.join(path, "repo"), "Manifest.xml")

def get_workspace_manifest():
    manifest_path = get_workspace_manifest_file()
    return edk_manifest.ManifestXml(manifest_path)
