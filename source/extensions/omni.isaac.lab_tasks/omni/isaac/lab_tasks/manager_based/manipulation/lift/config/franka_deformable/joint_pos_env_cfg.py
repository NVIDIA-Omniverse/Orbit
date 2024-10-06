# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import omni.isaac.lab.sim as sim_utils
from omni.isaac.lab.assets import DeformableObjectCfg
from omni.isaac.lab.managers import EventTermCfg as EventTerm
from omni.isaac.lab.managers import SceneEntityCfg
from omni.isaac.lab.utils import configclass

from omni.isaac.lab_tasks.manager_based.manipulation.lift import mdp
from omni.isaac.lab_tasks.manager_based.manipulation.lift.config.franka import joint_pos_env_cfg


@configclass
class FrankaDeformableCubeLiftEnvCfg(joint_pos_env_cfg.FrankaCubeLiftEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # Reduce the number of environments for training with deformables
        self.scene.num_envs = 1024
        # Disable replicator physics since deformable objects are not supported
        self.scene.replicate_physics = False

        # Reduce the PD for the hand to make the gripper less stiff
        self.scene.robot.actuators["panda_hand"].stiffness = 200.0
        self.scene.robot.actuators["panda_hand"].damping = 5.0

        # Set Deformable Cube as object
        self.scene.object = DeformableObjectCfg(
            prim_path="{ENV_REGEX_NS}/Object",
            init_state=DeformableObjectCfg.InitialStateCfg(pos=(0.5, 0.0, 0.05)),
            spawn=sim_utils.MeshCuboidCfg(
                size=(0.06, 0.06, 0.06),
                deformable_props=sim_utils.DeformableBodyPropertiesCfg(
                    self_collision_filter_distance=0.005,
                    settling_threshold=0.1,
                    sleep_damping=1.0,
                    sleep_threshold=0.05,
                    solver_position_iteration_count=20,
                    vertex_velocity_damping=0.5,
                    simulation_hexahedral_resolution=4,
                    rest_offset=0.0001,
                ),
                visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(1.0, 0.0, 0.0)),
                physics_material=sim_utils.DeformableBodyMaterialCfg(
                    dynamic_friction=0.95,
                    youngs_modulus=500000,
                ),
            ),
        )

        # Set events for the specific object type (deformable cube)
        self.events.reset_object_position = EventTerm(
            func=mdp.reset_nodal_state_uniform,
            mode="reset",
            params={
                "position_range": {"x": (-0.1, 0.1), "y": (-0.25, 0.25), "z": (0.0, 0.0)},
                "velocity_range": {},
                "asset_cfg": SceneEntityCfg("object"),
            },
        )


@configclass
class FrankaDeformableCubeLiftEnvCfg_PLAY(FrankaDeformableCubeLiftEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # make a smaller scene for play
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # disable randomization for play
        self.observations.policy.enable_corruption = False
