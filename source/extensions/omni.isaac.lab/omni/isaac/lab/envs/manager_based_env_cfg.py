# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Base configuration of the environment.

This module defines the general configuration of the environment. It includes parameters for
configuring the environment instances, viewer settings, and simulation parameters.
"""

from dataclasses import MISSING

import omni.isaac.lab.envs.mdp as mdp
from omni.isaac.lab.managers import EventTermCfg as EventTerm
from omni.isaac.lab.scene import InteractiveSceneCfg
from omni.isaac.lab.sim import SimulationCfg
from omni.isaac.lab.utils import configclass

from .common import ViewerCfg
from .ui import BaseEnvWindow


@configclass
class DefaultEventManagerCfg:
    """Configuration of the default event manager.

    This manager is used to reset the scene to a default state. The default state is specified
    by the scene configuration.
    """

    reset_scene_to_default = EventTerm(func=mdp.reset_scene_to_default, mode="reset")


@configclass
class ManagerBasedEnvCfg:
    """Base configuration of the environment."""

    # simulation settings
    viewer: ViewerCfg = ViewerCfg()
    """Viewer configuration. Default is ViewerCfg()."""

    sim: SimulationCfg = SimulationCfg()
    """Physics simulation configuration. Default is SimulationCfg()."""

    # ui settings
    ui_window_class_type: type | None = BaseEnvWindow
    """The class type of the UI window. Default is None.

    If None, then no UI window is created.

    Note:
        If you want to make your own UI window, you can create a class that inherits from
        from :class:`omni.isaac.lab.envs.ui.base_env_window.BaseEnvWindow`. Then, you can set
        this attribute to your class type.
    """

    # general settings
    decimation: int = MISSING
    """Number of control action updates @ sim dt per policy dt.

    For instance, if the simulation dt is 0.01s and the policy dt is 0.1s, then the decimation is 10.
    This means that the control action is updated every 10 simulation steps.
    """

    # environment settings
    scene: InteractiveSceneCfg = MISSING
    """Scene settings.

    Please refer to the :class:`omni.isaac.lab.scene.InteractiveSceneCfg` class for more details.
    """

    observations: object = MISSING
    """Observation space settings.

    Please refer to the :class:`omni.isaac.lab.managers.ObservationManager` class for more details.
    """

    actions: object = MISSING
    """Action space settings.

    Please refer to the :class:`omni.isaac.lab.managers.ActionManager` class for more details.
    """

    events: object = DefaultEventManagerCfg()
    """Event settings. Defaults to the basic configuration that resets the scene to its default state.

    Please refer to the :class:`omni.isaac.lab.managers.EventManager` class for more details.
    """

    ##
    # Properties.
    ##

    def set_seed(self, value: int):
        """Set the seed for the environment.

        The seed is set at the beginning of the environment initialization. This ensures that the environment
        creation is more deterministic and behaves similarly across different runs.

        We recommend using this method to set the seed for the environment instead of directly
        setting the seed attribute. This is to ensure that other internal settings are updated
        when the seed is set as well.

        Args:
            value: The seed value. Should be a non-negative integer.
        """
        if value is not None and value < 0:
            raise ValueError(f"Seed value must be a non-negative integer. Got {value}.")
        self.seed = value

    def get_seed(self) -> int | None:
        """Get the seed for the environment.

        Returns:
            The seed value. This is None if the seed is not set.
        """
        return self.seed if hasattr(self, "seed") else None
