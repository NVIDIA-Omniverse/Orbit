# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math

from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils import configclass
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as mdp
import isaaclab_tasks.manager_based.manipulation.reach.mdp as manipulation_mdp

from .rough_env_cfg import ARM_JOINT_NAMES, LEG_JOINT_NAMES, DigitRewards, DigitRoughEnvCfg


@configclass
class DigitLocoManipRewards(DigitRewards):
    joint_deviation_arms = None

    joint_vel_hip_yaw = RewTerm(
        func=mdp.joint_vel_l2,
        weight=-0.001,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_leg_hip_yaw"])},
    )

    left_ee_pos_tracking = RewTerm(
        func=manipulation_mdp.position_command_error,
        weight=-2.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="left_arm_wrist_yaw"),
            "command_name": "left_ee_position",
        },
    )

    left_ee_pos_tracking_fine_grained = RewTerm(
        func=manipulation_mdp.position_command_error_tanh,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="left_arm_wrist_yaw"),
            "std": 0.05,
            "command_name": "left_ee_position",
        },
        weight=2.0,
    )

    left_end_effector_orientation_tracking = RewTerm(
        func=manipulation_mdp.orientation_command_error,
        weight=-0.2,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="left_arm_wrist_yaw"),
            "command_name": "left_ee_position",
        },
    )

    right_ee_pos_tracking = RewTerm(
        func=manipulation_mdp.position_command_error,
        weight=-2.0,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="right_arm_wrist_yaw"),
            "command_name": "right_ee_position",
        },
    )

    right_ee_pos_tracking_fine_grained = RewTerm(
        func=manipulation_mdp.position_command_error_tanh,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="right_arm_wrist_yaw"),
            "std": 0.05,
            "command_name": "right_ee_position",
        },
        weight=2.0,
    )

    right_end_effector_orientation_tracking = RewTerm(
        func=manipulation_mdp.orientation_command_error,
        weight=-0.2,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="right_arm_wrist_yaw"),
            "command_name": "right_ee_position",
        },
    )


@configclass
class DigitLocoManipObservations:

    @configclass
    class PolicyCfg(ObsGroup):
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel, noise=Unoise(n_min=-0.1, n_max=0.1),)
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel, noise=Unoise(n_min=-0.2, n_max=0.2),)
        projected_gravity = ObsTerm(
            func=mdp.projected_gravity,
            noise=Unoise(n_min=-0.05, n_max=0.05),
        )
        velocity_commands = ObsTerm(
            func=mdp.generated_commands,
            params={"command_name": "base_velocity"},
        )
        left_ee_pos_command = ObsTerm(
            func=mdp.generated_commands,
            params={"command_name": "left_ee_position"},
        )
        right_ee_pos_command = ObsTerm(
            func=mdp.generated_commands,
            params={"command_name": "right_ee_position"},
        )
        joint_pos = ObsTerm(
            func=mdp.joint_pos_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_JOINT_NAMES + ARM_JOINT_NAMES)},
            noise=Unoise(n_min=-0.01, n_max=0.01),
        )
        joint_vel = ObsTerm(
            func=mdp.joint_vel_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_JOINT_NAMES + ARM_JOINT_NAMES)},
            noise=Unoise(n_min=-1.5, n_max=1.5),
        )
        actions = ObsTerm(func=mdp.last_action)
        height_scan = ObsTerm(
            func=mdp.height_scan,
            params={"sensor_cfg": SceneEntityCfg("height_scanner")},
            noise=Unoise(n_min=-0.1, n_max=0.1),
            clip=(-1.0, 1.0),
        )

    policy = PolicyCfg()


@configclass
class DigitLocoManipCommands:
    base_velocity = mdp.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(10.0, 10.0),
        rel_standing_envs=0.25,
        rel_heading_envs=1.0,
        heading_command=True,
        debug_vis=True,
        ranges=mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-1.0, 1.0),
            lin_vel_y=(-1.0, 1.0),
            ang_vel_z=(-1.0, 1.0),
            heading=(-math.pi, math.pi),
        ),
    )

    left_ee_position = mdp.UniformPoseCommandCfg(
        asset_name="robot",
        body_name="left_arm_wrist_yaw",
        resampling_time_range=(1.0, 3.0),
        debug_vis=True,
        ranges=mdp.UniformPoseCommandCfg.Ranges(
            pos_x=(0.25, 0.45),
            pos_y=(0.15, 0.3),
            pos_z=(-0.05, 0.15),
            roll=(0.0, 0.0),
            pitch=(0.0, 0.0),
            yaw=(math.pi / 2.0, math.pi / 2.0),
        ),
    )

    right_ee_position = mdp.UniformPoseCommandCfg(
        asset_name="robot",
        body_name="right_arm_wrist_yaw",
        resampling_time_range=(1.0, 3.0),
        debug_vis=True,
        ranges=mdp.UniformPoseCommandCfg.Ranges(
            pos_x=(0.25, 0.45),
            pos_y=(-0.3, -0.15),
            pos_z=(-0.05, 0.15),
            roll=(0.0, 0.0),
            pitch=(0.0, 0.0),
            yaw=(-math.pi / 2.0, -math.pi / 2.0),
        ),
    )


@configclass
class DigitLocoManipEnvCfg(DigitRoughEnvCfg):
    rewards: DigitLocoManipRewards = DigitLocoManipRewards()
    observations: DigitLocoManipObservations = DigitLocoManipObservations()
    commands: DigitLocoManipCommands = DigitLocoManipCommands()

    def __post_init__(self):
        super().__post_init__()

        self.episode_length_s = 14.0

        # Rewards:
        self.rewards.flat_orientation_l2.weight = -10.5
        self.rewards.termination_penalty.weight = -100.0

        # Commands
        self.commands.base_velocity.ranges.lin_vel_x = (0.0, 0.8)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)

        # Change terrain to flat.
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        # Remove height scanner.
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        # Remove terrain curriculum.
        self.curriculum.terrain_levels = None


class DigitLocoManipEnvCfg_PLAY(DigitLocoManipEnvCfg):

    def __post_init__(self) -> None:
        super().__post_init__()

        # Make a smaller scene for play.
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # Disable randomization for play.
        self.observations.policy.enable_corruption = False
        # Remove random pushing.
        self.randomization.base_external_force_torque = None
        self.randomization.push_robot = None
        self.randomization.reset_base.params = {
            "pose_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "yaw": (-3.1415 * 0, 3.1415 * 0),},
            "velocity_range": {
                "x": (-0.0, 0.0),
                "y": (-0.0, 0.0),
                "z": (-0.0, 0.0),
                "roll": (-0.0, 0.0),
                "pitch": (-0.0, 0.0),
                "yaw": (-0.0, 0.0),
            },
        }

        self.commands.base_velocity.ranges.heading = (0.0, 0.0)
