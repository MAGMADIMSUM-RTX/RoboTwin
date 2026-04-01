from ._base_task import Base_Task
from .utils import *
import sapien
from ._GLOBAL_CONFIGS import *


class realman_test(Base_Task):
    """
    任务：使用锤子敲击方块
    Task: Beat a block with a hammer
    """

    def setup_demo(self, **kwags):
        """
        设置演示环境
        Setup the demo environment
        """
        super()._init_task_env_(**kwags)

    def load_actors(self):
        """
        加载场景中的物体（锤子和方块）
        Load actors in the scene (hammer and block)
        """
        # 创建锤子
        # Create hammer
        self.hammer = create_actor(
            scene=self,
            pose=sapien.Pose([0, -0.06, 0.783], [0, 0, 0.995, 0.105]),
            modelname="037_box",
            convex=True,
            model_id=0,
        )
        
        # 随机生成方块的位置
        # Randomly generate block pose
        block_pose = rand_pose(
            xlim=[-0.25, 0.25],
            ylim=[-0.05, 0.15],
            zlim=[0.76],
            qpos=[1, 0, 0, 0],
            rotate_rand=True,
            rotate_lim=[0, 0, 0.5],
        )
        # 确保方块位置不在原点附近，避免与锤子或其他物体冲突
        # Ensure block is not too close to the origin to avoid conflict
        while abs(block_pose.p[0]) < 0.05 or np.sum(pow(block_pose.p[:2], 2)) < 0.001:
            block_pose = rand_pose(
                xlim=[-0.25, 0.25],
                ylim=[-0.05, 0.15],
                zlim=[0.76],
                qpos=[1, 0, 0, 0],
                rotate_rand=True,
                rotate_lim=[0, 0, 0.5],
            )

        # 创建方块
        # Create block
        self.block = create_box(
            scene=self,
            pose=block_pose,
            half_size=(0.025, 0.025, 0.025),
            color=(1, 0, 0),
            name="box",
            is_static=True,
        )
        self.hammer.set_mass(0.001)

        # 添加禁止区域，防止碰撞
        # Add prohibited area to avoid collision
        self.add_prohibit_area(self.hammer, padding=0.10)
        self.prohibited_area.append([
            block_pose.p[0] - 0.05,
            block_pose.p[1] - 0.05,
            block_pose.p[0] + 0.05,
            block_pose.p[1] + 0.05,
        ])

    def play_once(self):
        """
        执行一次完整的任务流程
        Execute the full task sequence once
        """
        # 获取方块功能点的位置
        # Get the position of the block's functional point
        block_pose = self.block.get_functional_point(0, "pose").p
        # 根据方块位置决定使用左臂还是右臂（如果方块在左侧则使用左臂，否则使用右臂）
        # Determine which arm to use based on block position (left if block is on left side, else right)
        arm_tag = ArmTag("left" if block_pose[0] < 0 else "right")

        # 使用选定的手臂抓取锤子
        # Grasp the hammer with the selected arm
        self.move(self.grasp_actor(self.hammer, arm_tag=arm_tag, pre_grasp_dis=0.12, grasp_dis=0.01))
        # 将锤子向上移动
        # Move the hammer upwards
        self.move(self.move_by_displacement(arm_tag, z=0.07, move_axis="arm"))

        # 将锤子放置在方块的功能点上（模拟敲击动作）
        # Place the hammer on the block's functional point (simulating a beating action)
        self.move(
            self.place_actor(
                self.hammer,
                target_pose=self.block.get_functional_point(1, "pose"),
                arm_tag=arm_tag,
                functional_point_id=0,
                pre_dis=0.06,
                dis=0,
                is_open=False,
            ))

        self.info["info"] = {"{A}": "020_hammer/base0", "{a}": str(arm_tag)}
        return self.info

    def check_success(self):
        """
        检查任务是否成功
        Check if the task is successful
        """
        # 获取锤子和方块的关键点位置
        # Get functional points of hammer and block
        hammer_target_pose = self.hammer.get_functional_point(0, "pose").p
        block_pose = self.block.get_functional_point(1, "pose").p
        eps = np.array([0.02, 0.02])
        # 检查位置偏差是否在允许范围内，并且发生了接触
        # Check if position error is within tolerance and contact occurred
        return np.all(abs(hammer_target_pose[:2] - block_pose[:2]) < eps) and self.check_actors_contact(
            self.hammer.get_name(), self.block.get_name())
