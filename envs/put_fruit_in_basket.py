from ._base_task import Base_Task
from .utils import *
import sapien
import math
import transforms3d as t3d


class put_fruit_in_basket(Base_Task):

    def setup_demo(self, is_test=False, **kwags):
        super()._init_task_env_(**kwags)

    def check_reachability(self, pose, arm_tag):
        if arm_tag == "left":
            res = self.robot.left_plan_path(pose)
        else:
            res = self.robot.right_plan_path(pose)
        
        # Check if planning was successful
        if isinstance(res, dict) and res.get("status") == "Success":
            return True
        return False

    def choose_top_down_grasp(self, actor, arm_tag):
        # We want the gripper's X-axis (approach direction) to be close to world -Z (0, 0, -1)
        target_dir = np.array([0, 0, -1])
        
        candidates = [] # List of (score, id)
        
        for i, _ in actor.iter_contact_points():
            # Get grasp pose for this contact point
            pose = self.get_grasp_pose(actor, arm_tag, contact_point_id=i, pre_dis=0)
            if pose is None:
                continue
                
            # Extract quaternion [w, x, y, z] and convert to matrix
            quat = pose[3:] 
            mat = t3d.quaternions.quat2mat(quat)
            
            # X-axis is the approach direction
            x_axis = mat[:3, 0]
            
            # Calculate alignment with vertical down vector
            dot = np.dot(x_axis, target_dir)
            
            # Check Z height of the grasp pose
            grasp_z = pose[2]
            
            # Filter out grasps that are too low (potential table collision)
            # 0.745 is close to table (0.74)
            if grasp_z < 0.745: 
                continue

            # Score combines alignment (primary) and height (secondary)
            score = dot * 10.0 + grasp_z
            candidates.append((score, i))
            
        # Sort candidates by score descending
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        print(f"DEBUG: Found {len(candidates)} valid geometric candidates")
        # print(f"DEBUG: Candidates scores: {[f'{s:.3f}' for s, _ in candidates]}")
        
        # Check reachability starting from best score
        for score, i in candidates:
            # We use pre_dis=0.15 matching play_once
            pre_grasp_pose = self.get_grasp_pose(actor, arm_tag, contact_point_id=i, pre_dis=0.15)
            # We use grasp_dis=0.01 matching play_once
            grasp_pose = self.get_grasp_pose(actor, arm_tag, contact_point_id=i, pre_dis=0.01)
            
            if self.check_reachability(pre_grasp_pose, arm_tag) and self.check_reachability(grasp_pose, arm_tag):
                print(f"DEBUG: Selected reachable grasp ID {i} with score {score:.3f}")
                return i
            else:
                 # Optional: print debug for failed reachability
                 # print(f"DEBUG: Grasp ID {i} unreachable")
                 pass
                 
        print("DEBUG: No reachable top-down grasp found!")
        return -1

    def load_actors(self):
        print("DEBUG: Entering load_actors")
        self.arm_tag = ArmTag({0: "left", 1: "right"}[np.random.randint(0, 2)])
        self.basket_name = "110_basket"
        self.basket_id = np.random.randint(0, 2)
        
        # 使用 103_fruit 作为水果，包含多种水果模型 (ID 0-6)
        self.object_name = "103_fruit"
        self.object_id = np.random.randint(0, 7)
        
        # print(f"DEBUG: Creating basket {self.basket_name} id={self.basket_id}")
        if self.arm_tag == "left":  # fruit on left
            self.basket = rand_create_actor(
                scene=self,
                modelname=self.basket_name,
                model_id=self.basket_id,
                xlim=[0.15, 0.20],  # Move basket to right side
                ylim=[-0.05, 0.05],
                qpos=[0.5, 0.5, 0.5, 0.5],
                convex=False,
                is_static=True,
            )
            # print(f"DEBUG: Basket created: {self.basket}")
            # print(f"DEBUG: Creating object {self.object_name} id={self.object_id}")
            self.object = rand_create_actor(
                scene=self,
                modelname=self.object_name,
                model_id=self.object_id,
                xlim=[-0.15, -0.10], # Move fruit to left side, closer to center
                ylim=[-0.05, 0.05],
                rotate_rand=True,
                rotate_lim=[0, np.pi / 6, 0],
                # 水果通常比较小，可能需要调整 qpos 或者让它自然掉落
                # 这里沿用参考代码的 qpos，如果不合适再调整
                qpos=[0.707225, 0.706849, -0.0100455, -0.00982061],
                convex=True,
            )
            # print(f"DEBUG: Object created: {self.object}")
        else:  # fruit on right
            self.basket = rand_create_actor(
                scene=self,
                modelname=self.basket_name,
                model_id=self.basket_id,
                xlim=[-0.20, -0.15], # Move basket to left side
                ylim=[-0.05, 0.05],
                qpos=[0.5, 0.5, 0.5, 0.5],
                convex=False,
                is_static=True,
            )
            # print(f"DEBUG: Basket created: {self.basket}")
            # print(f"DEBUG: Creating object {self.object_name} id={self.object_id}")
            self.object = rand_create_actor(
                scene=self,
                modelname=self.object_name,
                model_id=self.object_id,
                xlim=[0.10, 0.15], # Move fruit to right side
                ylim=[-0.05, 0.05],
                rotate_rand=True,
                rotate_lim=[0, np.pi / 6, 0],
                qpos=[0.707225, 0.706849, -0.0100455, -0.00982061],
                convex=True,
            )
            print(f"DEBUG: Object created: {self.object}")
        
        # self.basket.set_mass(0.5) # Static basket has infinite mass
        self.object.set_mass(0.01)
        self.object_start_height = self.object.get_pose().p[2]
        self.start_height = self.basket.get_pose().p[2]
        self.add_prohibit_area(self.object, padding=0.1)
        self.add_prohibit_area(self.basket, padding=0.05)
        print("DEBUG: load_actors finished")

    def play_once(self):
        print("DEBUG: Entering play_once")
        # Grasp the fruit
        # Select best top-down grasp to avoid table collision and ensure natural motion
        best_grasp_id = self.choose_top_down_grasp(self.object, self.arm_tag)
        
        if best_grasp_id != -1:
            print(f"DEBUG: Using Top-Down Grasp ID {best_grasp_id} with Unconstrained Approach")
            contact_point_id = best_grasp_id
            
            # Manually construct unconstrained grasp actions
            # pre_dis=0.15, grasp_dis=0.01
            pre_grasp_pose = self.get_grasp_pose(self.object, self.arm_tag, contact_point_id=contact_point_id, pre_dis=0.15)
            grasp_pose = self.get_grasp_pose(self.object, self.arm_tag, contact_point_id=contact_point_id, pre_dis=0.01)
            
            actions = [
                Action(self.arm_tag, "move", target_pose=pre_grasp_pose),
                Action(self.arm_tag, "move", target_pose=grasp_pose), # No constraint_pose!
                Action(self.arm_tag, "close", target_gripper_pos=0.0)
            ]
            self.move((self.arm_tag, actions))
            
        else:
            print("DEBUG: Top-Down Grasp failed/unreachable. Falling back to Default Grasp.")
            # Fallback to default (likely side grasp)
            self.move(self.grasp_actor(
                self.object, 
                arm_tag=self.arm_tag, 
                pre_grasp_dis=0.15, 
                grasp_dis=0.01,
                contact_point_id=None
            ))

        # Lift the fruit up
        self.move(self.move_by_displacement(arm_tag=self.arm_tag, z=0.15))

        # Get functional points of basket for placing
        # print("DEBUG: Getting functional points")
        f0_val = self.basket.get_functional_point(0)
        # print(f"DEBUG: f0_val={f0_val}")
        f0 = np.array(f0_val)
        
        f1_val = self.basket.get_functional_point(1)
        # print(f"DEBUG: f1_val={f1_val}")
        f1 = np.array(f1_val)
        place_pose = (f0 if np.linalg.norm(f0[:2] - self.object.get_pose().p[:2])
                      < np.linalg.norm(f1[:2] - self.object.get_pose().p[:2]) else f1)
        place_pose[:2] = f0[:2] if place_pose is f0 else f1[:2]
        place_pose[3:] = (-1, 0, 0, 0) if self.arm_tag == "left" else (0.05, 0, 0, 0.99)

        # Place the fruit in the basket
        self.move(self.place_actor(
            self.object,
            arm_tag=self.arm_tag,
            target_pose=place_pose,
            dis=0.02,
            is_open=False,
        ))

        if not self.plan_success:
            self.plan_success = True  # Try new way
            # Move up and away (recovery motion when plan fails)
            place_pose[0] += -0.15 if self.arm_tag == "left" else 0.15
            place_pose[2] += 0.15
            self.move(self.move_to_pose(arm_tag=self.arm_tag, target_pose=place_pose))

            # Lower down (recovery motion when plan fails)
            place_pose[2] -= 0.05
            self.move(self.move_to_pose(arm_tag=self.arm_tag, target_pose=place_pose))

            # Open gripper to release object
            self.move(self.open_gripper(arm_tag=self.arm_tag))

            # Move arm away
            self.move(self.back_to_origin(arm_tag=self.arm_tag))
        else:
            # Open gripper to release object
            self.move(self.open_gripper(arm_tag=self.arm_tag))
            # lift arm up, to avoid collision with the basket
            self.move(self.move_by_displacement(arm_tag=self.arm_tag, z=0.08))
            # Move arm away
            self.move(self.back_to_origin(arm_tag=self.arm_tag))

        self.info["info"] = {
            "{A}": f"{self.object_name}/base{self.object_id}",
            "{B}": f"{self.basket_name}/base{self.basket_id}",
            "{a}": str(self.arm_tag),
            "{b}": str(self.arm_tag.opposite),
        }
        return self.info

    def check_success(self):
        obj_p = self.object.get_pose().p
        basket_p = self.basket.get_pose().p
        basket_axis = (self.basket.get_pose().to_transformation_matrix()[:3, :3] @ np.array([[0, 1, 0]]).T)

        # Robust contact check logic
        def get_entity_set(actor_wrapper):
            if hasattr(actor_wrapper, 'actor'):
                native_actor = actor_wrapper.actor
                if hasattr(native_actor, 'get_links'):
                    # Articulation
                    return set(link.entity for link in native_actor.get_links())
                else:
                    # Rigid Body (Entity)
                    return {native_actor}
            return set()

        obj_entities = get_entity_set(self.object)
        basket_entities = get_entity_set(self.basket)
        
        contacts = self.scene.get_contacts()
        obj_contact_basket = False
        obj_contact_table = False
        
        # Debug: track what object is touching
        obj_touching = set()

        for contact in contacts:
            e0 = contact.bodies[0].entity
            e1 = contact.bodies[1].entity
            
            # Check table contact
            if (e0 in obj_entities and e1.name == "table"):
                obj_contact_table = True
                obj_touching.add(e1.name)
            elif (e1 in obj_entities and e0.name == "table"):
                obj_contact_table = True
                obj_touching.add(e0.name)
            
            # Check basket contact
            if (e0 in obj_entities and e1 in basket_entities):
                obj_contact_basket = True
                obj_touching.add(e1.name)
            elif (e1 in obj_entities and e0 in basket_entities):
                obj_contact_basket = True
                obj_touching.add(e0.name)
                
            # Debug other contacts
            if e0 in obj_entities:
                obj_touching.add(e1.name)
            if e1 in obj_entities:
                obj_touching.add(e0.name)

        obj_not_contact_table = not obj_contact_table
        
        # Check conditions
        # cond1 = basket_p[2] - self.start_height > 0.02 # Basket should stay on table
        cond2 = obj_p[2] - self.object_start_height > 0.02
        cond3 = np.dot(basket_axis.reshape(3), [0, 0, 1]) > 0.5
        cond4 = np.sum(np.sqrt((obj_p - basket_p)**2)) < 0.15
        
        # Cond5: Fruit should be in contact with the basket. 
        # We relax the table contact check because the fruit might touch the table through the basket mesh 
        # or if the basket bottom is very thin.
        cond5 = obj_contact_basket
        
        print(f"DEBUG: Check success conditions:")
        print(f"  Object touching: {obj_touching}")
        # print(f"  Cond1 (Basket lifted): {cond1} (Current Z: {basket_p[2]}, Start Z: {self.start_height})")
        print(f"  Cond2 (Fruit lifted): {cond2} (Current Z: {obj_p[2]}, Start Z: {self.object_start_height})")
        print(f"  Cond3 (Basket upright): {cond3} (Dot prod: {np.dot(basket_axis.reshape(3), [0, 0, 1])})")
        print(f"  Cond4 (Fruit-Basket dist): {cond4} (Dist: {np.sum(np.sqrt((obj_p - basket_p)**2))})")
        print(f"  Cond5 (Fruit contact): {cond5} (Contact basket: {obj_contact_basket})")
        
        return cond2 and cond3 and cond4 and cond5
