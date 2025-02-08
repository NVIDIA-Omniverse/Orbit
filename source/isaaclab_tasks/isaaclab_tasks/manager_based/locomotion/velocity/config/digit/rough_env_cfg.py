# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

import math

from isaaclab_assets.robots.agility import get_digit_articulation_cfg

from isaaclab.managers import (
    EventTermCfg,
    ObservationGroupCfg,
    ObservationTermCfg,
    RewardTermCfg,
    SceneEntityCfg,
    TerminationTermCfg,
)
from isaaclab.utils import configclass
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as mdp
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg

from . import rewards as digit_rewards

LEG_JOINT_NAMES = [
    ".*_hip_roll",
    ".*_hip_yaw",
    ".*_hip_pitch",
    ".*_knee",
    ".*_toe_a",
    ".*_toe_b",
]


ARM_JOINT_NAMES = [".*_arm_.*"]


@configclass
class DigitRewards:
    termination_penalty = RewardTermCfg(
        func=mdp.is_terminated,
        weight=-100.0,
    )
    track_lin_vel_xy_exp = RewardTermCfg(
        func=mdp.track_lin_vel_xy_yaw_frame_exp,
        weight=1.0,
        params={"command_name": "base_velocity", "std": math.sqrt(0.25)},
    )
    track_ang_vel_z_exp = RewardTermCfg(
        func=mdp.track_ang_vel_z_world_exp,
        weight=1.0,
        params={
            "command_name": "base_velocity",
            "std": math.sqrt(0.25),
        },
    )
    feet_air_time = RewardTermCfg(
        func=digit_rewards.feet_air_time_l2,
        weight=20.0,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_leg_toe_roll"),
            "threshold": 0.8,
            "command_name": "base_velocity",
        },
    )
    feet_slide = RewardTermCfg(
        func=mdp.feet_slide,
        weight=-0.25,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_leg_toe_roll"),
            "asset_cfg": SceneEntityCfg("robot", body_names=".*_leg_toe_roll"),
        },
    )
    dof_torques_l2 = RewardTermCfg(
        func=mdp.joint_torques_l2,
        weight=-1.0e-6,
    )
    dof_acc_l2 = RewardTermCfg(
        func=mdp.joint_acc_l2,
        weight=-2.0e-7,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_JOINT_NAMES + ARM_JOINT_NAMES)},
    )
    action_rate_l2 = RewardTermCfg(
        func=mdp.action_rate_l2,
        weight=-0.008,
    )
    flat_orientation_l2 = RewardTermCfg(
        func=mdp.flat_orientation_l2,
        weight=-2.5,
    )
    stand_still = RewardTermCfg(
        func=mdp.stand_still_error,
        weight=-0.4,
        params={
            "command_name": "base_velocity",
            "asset_cfg": SceneEntityCfg("robot", joint_names=LEG_JOINT_NAMES),
        },
    )
    lin_vel_z_l2 = RewardTermCfg(
        func=mdp.lin_vel_z_l2,
        weight=-2.0,
    )
    ang_vel_xy_l2 = RewardTermCfg(
        func=mdp.ang_vel_xy_l2,
        weight=-0.1,
    )
    no_jumps = RewardTermCfg(
        func=mdp.no_jumps,
        weight=-0.5,
        params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=[".*_leg_toe_roll"])},
    )
    dof_pos_limits = RewardTermCfg(
        func=mdp.joint_pos_limits,
        weight=-1.0,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_leg_toe_roll", ".*_leg_toe_pitch", ".*_tarsus"])},
    )
    joint_deviation_hip_roll = RewardTermCfg(
        func=mdp.joint_deviation_l1,
        weight=-0.1,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_leg_hip_roll")},
    )
    joint_deviation_hip_yaw = RewardTermCfg(
        func=mdp.joint_deviation_l1,
        weight=-0.2,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_leg_hip_yaw")},
    )
    joint_deviation_knee = RewardTermCfg(
        func=mdp.joint_deviation_l1,
        weight=-0.2,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=".*_tarsus")},
    )
    joint_deviation_feet = RewardTermCfg(
        func=mdp.joint_deviation_l1,
        weight=-0.1,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_toe_a", ".*_toe_b"])},
    )
    joint_deviation_arms = RewardTermCfg(
        func=mdp.joint_deviation_l1,
        weight=-0.2,
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=".*_arm_.*"),
        },
    )

    undesired_contacts = RewardTermCfg(
        func=mdp.undesired_contacts,
        weight=-0.1,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=[".*_rod", ".*_tarsus"]),
            "threshold": 1.0,
        },
    )


@configclass
class DigitObservations:
    @configclass
    class PolicyCfg(ObservationGroupCfg):
        base_lin_vel = ObservationTermCfg(
            func=mdp.base_lin_vel,
            noise=Unoise(n_min=-0.1, n_max=0.1),
        )
        base_ang_vel = ObservationTermCfg(
            func=mdp.base_ang_vel,
            noise=Unoise(n_min=-0.2, n_max=0.2),
        )
        projected_gravity = ObservationTermCfg(
            func=mdp.projected_gravity,
            noise=Unoise(n_min=-0.05, n_max=0.05),
        )
        velocity_commands = ObservationTermCfg(
            func=mdp.generated_commands,
            params={"command_name": "base_velocity"},
        )
        joint_pos = ObservationTermCfg(
            func=mdp.joint_pos_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_JOINT_NAMES + ARM_JOINT_NAMES)},
            noise=Unoise(n_min=-0.01, n_max=0.01),
        )
        joint_vel = ObservationTermCfg(
            func=mdp.joint_vel_rel,
            params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_JOINT_NAMES + ARM_JOINT_NAMES)},
            noise=Unoise(n_min=-1.5, n_max=1.5),
        )
        actions = ObservationTermCfg(func=mdp.last_action)
        height_scan = ObservationTermCfg(
            func=mdp.height_scan,
            params={"sensor_cfg": SceneEntityCfg("height_scanner")},
            noise=Unoise(n_min=-0.1, n_max=0.1),
            clip=(-1.0, 1.0),
        )

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    # Observation groups:
    policy: PolicyCfg = PolicyCfg()


@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    time_out = TerminationTermCfg(func=mdp.time_out, time_out=True)
    base_contact = TerminationTermCfg(
        func=mdp.illegal_contact,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names="torso_base"),
            "threshold": 1.0,
        },
    )


@configclass
class ActionsCfg:
    """Action specifications for the MDP."""

    joint_pos = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=LEG_JOINT_NAMES + ARM_JOINT_NAMES,
        scale=0.5,
        use_default_offset=True,
    )


@configclass
class EventCfg:
    """Configuration for randomization."""

    # Startup events:
    physics_material = EventTermCfg(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.6, 1.0),
            "dynamic_friction_range": (0.6, 0.6),
            "restitution_range": (0.0, 0.0),
            "num_buckets": 64,
        },
    )

    add_base_mass = EventTermCfg(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="torso_base"),
            "mass_distribution_params": (-5.0, 5.0),
            "operation": "add",
        },
    )

    # Reset events:
    base_external_force_torque = EventTermCfg(
        func=mdp.apply_external_force_torque,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="torso_base"),
            "force_range": (0.0, 0.0),
            "torque_range": (-0.0, 0.0),
        },
    )

    reset_base = EventTermCfg(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "yaw": (0.0, 0.0),
            },
            "velocity_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "z": (-0.5, 0.5),
                "roll": (-0.5, 0.5),
                "pitch": (-0.5, 0.5),
                "yaw": (-0.5, 0.5),
            },
        },
    )

    reset_robot_joints = EventTermCfg(
        func=mdp.reset_joints_by_scale,
        mode="reset",
        params={
            "position_range": (1.0, 1.0),
            "velocity_range": (0.0, 0.0),
        },
    )

    # Interval events:
    push_robot = EventTermCfg(
        func=mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(10.0, 15.0),
        params={"velocity_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5)}},
    )


@configclass
class DigitRoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    rewards: DigitRewards = DigitRewards()
    observations: DigitObservations = DigitObservations()
    terminations: TerminationsCfg = TerminationsCfg()
    actions: ActionsCfg = ActionsCfg()
    events: EventCfg = EventCfg()

    def __post_init__(self):
        super().__post_init__()
        self.decimation = 4
        self.sim.dt = 0.005

        # Scene
        self.scene.robot = get_digit_articulation_cfg().replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/torso_base"
        self.scene.contact_forces.history_length = self.decimation
        self.scene.contact_forces.update_period = self.sim.dt
        self.scene.height_scanner.update_period = self.decimation * self.sim.dt

        # Commands
        self.commands.base_velocity.ranges.lin_vel_x = (-0.8, 0.8)
        self.commands.base_velocity.ranges.lin_vel_y = (-0.5, 0.5)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)
        self.commands.base_velocity.rel_standing_envs = 0.1
        self.commands.base_velocity.resampling_time_range = (3.0, 8.0)


@configclass
class DigitRoughEnvCfg_PLAY(DigitRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # Make a smaller scene for play.
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # Spawn the robot randomly in the grid (instead of their terrain levels).
        self.scene.terrain.max_init_terrain_level = None
        # Reduce the number of terrains to save memory.
        if self.scene.terrain.terrain_generator is not None:
            self.scene.terrain.terrain_generator.num_rows = 5
            self.scene.terrain.terrain_generator.num_cols = 5
            self.scene.terrain.terrain_generator.curriculum = False

        self.commands.base_velocity.ranges.lin_vel_x = (1.0, 1.0)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.heading = (0.0, 0.0)
        # Disable randomization for play.
        self.observations.policy.enable_corruption = False
        # Remove random pushing.
        self.randomization.base_external_force_torque = None
        self.randomization.push_robot = None
