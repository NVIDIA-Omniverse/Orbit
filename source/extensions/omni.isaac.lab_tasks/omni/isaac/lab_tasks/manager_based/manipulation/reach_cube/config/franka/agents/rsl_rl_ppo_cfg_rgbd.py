# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from omni.isaac.lab.utils import configclass

from omni.isaac.lab_tasks.utils.wrappers.rsl_rl import (
    RslRlOnPolicyRunnerCfg,
    RslRlPpoActorCriticCfg,
    RslRlPpoAlgorithmCfg,
)


@configclass
class LiftCubePPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = 78 #24
    max_iterations = 1500
    save_interval = 50
    experiment_name = "franka_lift_rgbd_optim_params"
    empirical_normalization = False
    policy = RslRlPpoActorCriticCfg(
        class_name="ActorCriticRGBD",
        init_noise_std=1.0,
        activation="selu",
    )
    algorithm = RslRlPpoAlgorithmCfg(
        value_loss_coef=1.5481403727467575, #1.0,
        use_clipped_value_loss=True,
        clip_param=0.7258709416158089, #0.2,
        entropy_coef=0.00951483659316667, #0.006,
        num_learning_epochs=9, #5,
        num_mini_batches=22, #4,
        learning_rate=0.019287231093395307, #1.0e-4,
        schedule="adaptive",
        gamma=0.9845052583039753, #0.98,
        lam=0.95,
        desired_kl=0.06639642347811588, #0.01,
        max_grad_norm=1.0,
    )
