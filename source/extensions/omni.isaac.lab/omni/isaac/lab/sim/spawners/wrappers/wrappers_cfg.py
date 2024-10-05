# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from dataclasses import MISSING

from omni.isaac.lab.utils import configclass
from omni.isaac.lab.sim.spawners.spawner_cfg import DeformableObjectSpawnerCfg, RigidObjectSpawnerCfg, SpawnerCfg
from omni.isaac.lab.sim.spawners.from_files import UsdFileCfg

from . import wrappers


@configclass
class MultiAssetSpawnerCfg(RigidObjectSpawnerCfg, DeformableObjectSpawnerCfg):
    """Configuration parameters for loading multiple assets from their individual configurations.
    
    Specifying values for any properties at the configuration level will override the settings of
    individual assets' configuration. For instance if the attribute
    :attr:`MultiAssetSpawnerCfg.mass_props` is specified, its value will overwrite the values of the
    mass properties in each configuration inside :attr:`assets_cfg` (wherever applicable).
    This is done to simplify configuring similar properties globally. By default, all properties are set to None.
    
    The following is an exception to the above:

    * :attr:`visible`: This parameter is ignored. Its value for the individual assets is used.
    * :attr:`semantic_tags`: If specified, it will be appended to each individual asset's semantic tags.

    """

    func = wrappers.spawn_multi_asset

    assets_cfg: list[SpawnerCfg] = MISSING
    """List of asset configurations to spawn."""

    random_choice: bool = True
    """Whether to randomly select an asset configuration. Default is True.

    If False, the asset configurations are spawned in the order they are provided in the list.
    If True, a random asset configuration is selected for each spawn.
    """
