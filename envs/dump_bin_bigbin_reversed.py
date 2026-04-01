from ._base_task import Base_Task
from .utils import *
import sapien
from copy import deepcopy


class dump_bin_bigbin_reversed(Base_Task):

    def setup_demo(self, **kwags):
        super()._init_task_env_(table_xy_bias=[-0.3, 0], **kwags)

    def load_actors(self):
        self.dustbin = create_actor(
            self,
            pose=sapien.Pose([0.45, 0, 0], [0.5, 0.5, 0.5, 0.5]),
            modelname="011_dustbin",
            convex=True,
            is_static=True,
        )
        deskbin_pose = rand_pose(
            xlim=[-0.2, -0.05],
            ylim=[-0.2, -0.05],
            qpos=[0.274575, 0.274387, 0.651424, 0.651895],
            rotate_rand=True,
            rotate_lim=[0, np.pi / 8.5, 0],
        )
        while abs(deskbin_pose.p[0]) < 0.05:
            deskbin_pose = rand_pose(
                xlim=[-0.2, -0.05],
                ylim=[-0.2, -0.05],
                qpos=[0.274575, 0.274387, 0.651424, 0.651895],
                rotate_rand=True,
                rotate_lim=[0, np.pi / 8.5, 0],
            )

        self.deskbin_id = np.random.choice([0, 3, 7, 8, 9, 10], 1)[0]
        self.deskbin = create_actor(
            self,
            pose=deskbin_pose,
            modelname="063_tabletrashbin",
            model_id=self.deskbin_id,
            convex=True,
        )
        self.garbage_num = 5
        self.sphere_lst = []
        for i in range(self.garbage_num):
            sphere_pose = sapien.Pose(
                [
                    deskbin_pose.p[0] + np.random.rand() * 0.02 - 0.01,
                    deskbin_pose.p[1] + np.random.rand() * 0.02 - 0.01,
                    0.80 + i * 0.005,
                ],
                [1, 0, 0, 0],
            )
            sphere = create_sphere(
                self.scene,
                pose=sphere_pose,
                radius=0.008,
                color=[1, 0, 0],
                name="garbage",
            )
            self.sphere_lst.append(sphere)
            self.sphere_lst[-1].find_component_by_type(sapien.physx.PhysxRigidDynamicComponent).mass = 0.0001

        self.add_prohibit_area(self.deskbin, padding=0.04)
        self.prohibited_area.append([-0.2, -0.2, 0.2, 0.2])
        # Define target pose for placing
        self.middle_pose = [0, 0.1, 0.741 + self.table_z_bias, 0, 0, 0, 1]
        # Define movement actions for shaking the deskbin
        action_lst = [
            Action(
                ArmTag('right'),
                "move",
                [0.45, -0.05, 1.05, 0.676862, 0.165979, -0.178228, 0.694654],
            ),
            Action(
                ArmTag('right'),
                "move",
                [
                    0.45,
                    -0.05 - np.random.rand() * 0.02,
                    1.05 - np.random.rand() * 0.02,
                    0.676862,
                    0.165979,
                    -0.178228,
                    0.694654,
                ],
            ),
        ]
        self.pour_actions = (ArmTag('right'), action_lst)

    def play_once(self):
        # Get deskbin's current position
        deskbin_pose = self.deskbin.get_pose().p
        # Determine which arm to use for grasping based on deskbin's position
        # If x > 0 (Right side, near to big bin), use Right arm.
        # If x < 0 (Left side, far from big bin), use Left arm.
        grasp_deskbin_arm_tag = ArmTag("right" if deskbin_pose[0] > 0 else "left")
        # Always use right arm for placing
        place_deskbin_arm_tag = ArmTag("right")

        if grasp_deskbin_arm_tag == "left":
            # Grasp the deskbin with left arm (Far side)
            self.move(
                self.grasp_actor(
                    self.deskbin,
                    arm_tag=grasp_deskbin_arm_tag,
                    pre_grasp_dis=0.08,
                    contact_point_id=3,
                ))
            # Lift the deskbin up
            self.move(self.move_by_displacement(grasp_deskbin_arm_tag, z=0.08, move_axis="arm"))
            # Place the deskbin at target pose
            self.move(
                self.place_actor(
                    self.deskbin,
                    target_pose=self.middle_pose,
                    arm_tag=grasp_deskbin_arm_tag,
                    pre_dis=0.08,
                    dis=0.01,
                ))
            # Move arm up after placing
            self.move(self.move_by_displacement(grasp_deskbin_arm_tag, z=0.1, move_axis="arm"))
            # Return left arm to origin while simultaneously grasping with right arm
            self.move(
                self.back_to_origin(grasp_deskbin_arm_tag),
                self.grasp_actor(
                    self.deskbin,
                    arm_tag=place_deskbin_arm_tag,
                    pre_grasp_dis=0.08,
                    contact_point_id=1,
                ),
            )
        else:
            # If deskbin is on right side (Near side), directly grasp with right arm
            self.move(
                self.grasp_actor(
                    self.deskbin,
                    arm_tag=place_deskbin_arm_tag,
                    pre_grasp_dis=0.08,
                    contact_point_id=1,
                ))

        # Lift the deskbin with right arm
        self.move(self.move_by_displacement(arm_tag=place_deskbin_arm_tag, z=0.08, move_axis="arm"))
        # Perform shaking motion 3 times
        for i in range(3):
            self.move(self.pour_actions)
        # Delay for 6 seconds
        self.delay(6)

        self.info["info"] = {"{A}": f"063_tabletrashbin/base{self.deskbin_id}"}
        return self.info

    def check_success(self):
        deskbin_pose = self.deskbin.get_pose().p
        if deskbin_pose[2] < 1:
            return False
        for i in range(self.garbage_num):
            pose = self.sphere_lst[i].get_pose().p
            if pose[2] >= 0.13 and pose[2] <= 0.25:
                continue
            return False
        return True
