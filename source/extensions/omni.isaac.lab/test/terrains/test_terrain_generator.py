# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Launch Isaac Sim Simulator first."""

from omni.isaac.lab.app import AppLauncher, run_tests

# launch omniverse app
simulation_app = AppLauncher(headless=True).app

"""Rest everything follows."""

import numpy as np
import os
import shutil
import unittest

from omni.isaac.lab.terrains import TerrainGenerator, TerrainGeneratorCfg
from omni.isaac.lab.terrains.config.rough import ROUGH_TERRAINS_CFG


class TestTerrainGenerator(unittest.TestCase):
    """Test the procedural terrain generator."""

    def setUp(self):
        # Create directory to dump results
        test_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(test_dir, "output", "generator")

    def test_generation(self):
        """Generates assorted terrains and tests that the resulting mesh has the expected size."""
        # create terrain generator
        cfg = ROUGH_TERRAINS_CFG.copy()
        terrain_generator = TerrainGenerator(cfg=cfg)

        # print terrain generator info
        print(terrain_generator)

        # get size from mesh bounds
        bounds = terrain_generator.terrain_mesh.bounds
        actualSize = abs(bounds[1] - bounds[0])
        # compute the expected size
        expectedSizeX = cfg.size[0] * cfg.num_rows + 2 * cfg.border_width
        expectedSizeY = cfg.size[1] * cfg.num_cols + 2 * cfg.border_width

        # check if the size is as expected
        self.assertAlmostEqual(actualSize[0], expectedSizeX)
        self.assertAlmostEqual(actualSize[1], expectedSizeY)

    def test_generation_cache(self):
        """Generate the terrain and check that caching works.

        When caching is enabled, the terrain should be generated only once and the same terrain should be returned
        when the terrain generator is created again.
        """
        # try out with and without curriculum
        for curriculum in [True, False]:
            with self.subTest(curriculum=curriculum):
                # clear output directory
                if os.path.exists(self.output_dir):
                    shutil.rmtree(self.output_dir)
                # create terrain generator with cache enabled
                cfg: TerrainGeneratorCfg = ROUGH_TERRAINS_CFG.copy()
                cfg.use_cache = True
                cfg.seed = 0
                cfg.cache_dir = self.output_dir
                cfg.curriculum = curriculum
                terrain_generator = TerrainGenerator(cfg=cfg)
                # keep a copy of the generated terrain mesh
                terrain_mesh_1 = terrain_generator.terrain_mesh.copy()

                # check cache exists and is equal to the number of terrains
                # with curriculum, all sub-terrains are uniquely generated
                hash_ids_1 = set(os.listdir(cfg.cache_dir))
                self.assertTrue(os.listdir(cfg.cache_dir))

                # create terrain generator with cache enabled
                terrain_generator = TerrainGenerator(cfg=cfg)
                # keep a copy of the generated terrain mesh
                terrain_mesh_2 = terrain_generator.terrain_mesh.copy()

                # check no new terrain is generated
                hash_ids_2 = set(os.listdir(cfg.cache_dir))
                self.assertEqual(len(hash_ids_1), len(hash_ids_2))
                self.assertSetEqual(hash_ids_1, hash_ids_2)

                # check if the mesh is the same
                # check they don't point to the same object
                self.assertIsNot(terrain_mesh_1, terrain_mesh_2)

                # check if the meshes are equal
                np.testing.assert_allclose(
                    terrain_mesh_1.vertices, terrain_mesh_2.vertices, atol=1e-5, err_msg="Vertices are not equal"
                )
                np.testing.assert_allclose(
                    terrain_mesh_1.faces, terrain_mesh_2.faces, atol=1e-5, err_msg="Faces are not equal"
                )


if __name__ == "__main__":
    run_tests()
