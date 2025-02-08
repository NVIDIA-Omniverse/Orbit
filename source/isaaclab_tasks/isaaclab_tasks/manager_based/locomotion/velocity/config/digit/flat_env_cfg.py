from isaaclab.utils import configclass

from .rough_env_cfg import DigitRoughEnvCfg

@configclass
class DigitFlatEnvCfg(DigitRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()

        # Change terrain to flat.
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        # Remove height scanner.
        # self.scene.height_scanner = None
        # self.observations.policy.height_scan = None
        # Remove terrain curriculum.
        self.curriculum.terrain_levels = None


class DigitFlatEnvCfg_PLAY(DigitFlatEnvCfg):

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
