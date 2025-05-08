import numpy as np
import time
import slicer.util as util
from scipy.spatial.transform import Rotation as R
from copy import deepcopy

import math
try:
    from sympy import symbols, solve
except Exception as e:
    util.pip_install('sympy')
    from sympy import symbols, solve

try:
    import transforms3d as tfs
except Exception as e:
    util.pip_install('transforms3d')
    import transforms3d as tfs

try:
    import matplotlib.pyplot as plt
except Exception as e:
    util.pip_install('matplotlib')
    import matplotlib.pyplot as plt 

import datetime   

class AccuracyTest:
    def __init__(self, c_in_b, m_in_h, pe_in_b, pt_in_b, trans_tip_in_hand_frame, trans_tip_in_marker_frame):
        self.pose = np.zeros((6,1))
        self.desired_phi_theta_beta = np.zeros(3)
        self.Target_Tip_in_Base = np.eye(4) # this is the frame attached to the target tip point (represented wrt the base frame of the robot)
        self.delta_position_in_base = []
        self.delta_position_in_cam = []
        self.error_in_base = []
        self.error_in_cam = []
        self.pid_input_p = []
        self.pid_input_i = []
        self.pid_input_d = []
        self.dir_path = r"Output\\"
        self.delta_path_base = "ur_delta_base"
        self.error_path_base = "ur_error_base"
        self.delta_path_cam = "ur_delta_cam"
        self.error_path_cam = "ur_error_cam"
        self.plot_path_base = "plot_base"
        self.plot_path_cam = "plot_cam"
        self.plot_path_pid_p = "plot_pid_p"
        self.plot_path_pid_i = "plot_pid_i"
        self.plot_path_pid_d = "plot_pid_d"
        self.Camera_in_Base = c_in_b
        self.Camera_in_Base[:3, 3] /= 1000.0
        self.Tool_in_Hand = m_in_h
        self.Tool_in_Hand[:3, 3] /= 1000.0
        Tip_in_Hand = np.array(trans_tip_in_hand_frame, dtype = np.float32)
        # print('camera in base : ', c_in_b)
        # print('tool in hand : ', m_in_h)
        self.Tip_in_Hand = Tip_in_Hand
        self.Tip_in_Hand[:3,3] = self.Tip_in_Hand[:3,3]/1000.0

        trans_tip_in_marker_frame = np.array(trans_tip_in_marker_frame, dtype = np.float32)
        self.trans_tip_in_marker_frame = trans_tip_in_marker_frame
        self.trans_tip_in_marker_frame[:3,3] /= 1000.0

        pe_in_b[:3] /= 1000.0
        pt_in_b[:3] /= 1000.0

        # self.reg_wiget = util.getModuleWidget('JIGTRegister')

        self.puncture(pe_in_b, pt_in_b)
    
    def   puncture(self, pe_in_b, pt_in_b):
        """
        pe_in_b:
        pt_in_b: 
        """
        start = time.time()
        # print("target entry in base:", pe_in_b)
        # print("target direction in base:", pt_in_b)
        assert pe_in_b[2]>pt_in_b[2], "height of entry point should be greater than target point"
        print('--------------------------------------------------------------')
        vector_et = self.get_puncture_path(pe_in_b, pt_in_b)[:, 0]  # get unit direction vector
        self.assert_unit_norm(vector_et)

        print("vector_et:", vector_et)

        optical_in_base = self.Camera_in_Base[:3, 3]
        print('Camera origin in base frame:', optical_in_base)
        y_axis_of_camera_in_base = self.Camera_in_Base.dot(np.array([0, 1.0, 0, 1])) # this is the point [0,1,0] tranformed from camera to base frame
        print('Camera [0,1,0,1] point in base frame:', y_axis_of_camera_in_base[:3])
        print('Camera vector from origin to [0,1,0,1] in base frame:', y_axis_of_camera_in_base[:3]-optical_in_base)
        vector_target_2_optical = self.get_unit_vector(optical_in_base-pt_in_b[:3, 0]) # Q1 : pt_in_b or (Tip_in_Hand(:3,3) in base)
        print('Vector from target point to camera origin in base frame:', vector_target_2_optical)
        normal_of_plane_omy = self.get_unit_vector(np.cross(vector_target_2_optical,
                                                            y_axis_of_camera_in_base[:3]-optical_in_base))    # subtract optical_in_base to get vector  # 前后顺序没关系,不需要单位话
        self.assert_unit_norm(normal_of_plane_omy)
        
        # vector_of_needle = self.get_unit_vector(self.Tip_in_Hand[:3, 3])    # Q2 : Tip_in_Hand[:3,3] or tip vector in marker frame? # TODO:这个需要标定出来的
        print('trans_tip_in_marker_frame')
        print(self.trans_tip_in_marker_frame)
        vector_of_needle = self.get_unit_vector(self.trans_tip_in_marker_frame[:3, 3]) 
        print('Vector_of_needle:', vector_of_needle)
        self.assert_unit_norm(vector_of_needle)

        # 计算phi,theta,beta
        # phi, theta, beta = self.get_angle_between_vector_and_coordinate(vector_of_needle, self.trans_tip_in_marker_frame)
        # phi, theta, beta = self.get_angle_between_vector_and_coordinate(vector_of_needle, self.Tip_in_Hand) # Q3 : angles should be wrt to eye(4) [vector is already in the frame under observation]
        phi, theta, beta = self.get_angle_between_vector_and_coordinate(vector_of_needle, np.eye(4))
        print("Expected angle phi, theta, beta:", phi, theta, beta)
        cs_theta = np.cos(theta)
        cs_beta  = np.cos(beta)
        cs_phi   = np.cos(phi)
        self.desired_phi_theta_beta[:] = [phi, theta, beta]
        # print(cs_phi, cs_theta, cs_beta)
        print('Normal to the plane:', normal_of_plane_omy)
        N = normal_of_plane_omy

        # First : get the direction vector of the z axis of Target_Tip_in_Base
        # the z axis of the marker frame is in the plane formed by the (vector_target_2_optical, y_axis_of_camera_in_base[:3]-optical_in_base)
        # ie the dot product of the z axis and N is 0
        x, y, z = symbols('x,y,z')
        f1 = N[0] * x + N[1] * y + N[2] * z
        f2 = vector_et[0] * x + vector_et[1] * y + vector_et[2] * z - cs_beta # the first part represents the angle the entry to target point vector (in base) forms with the z-axis of the frame attached to the target point (wrt base)
        f3 = x ** 2 + y ** 2 + z ** 2 - 1
        r = solve([f1, f2, f3], [x, y, z])
        print(r, vector_target_2_optical)
        z1, z2 = np.array(r, dtype=np.float32)
        print('z1:', z1)
        print('z2:', z2)
        print("z1+z2:", z1+z2)

        angle_z_om_1, angle_z_om_2 = self.angle_between(z1, vector_target_2_optical), self.angle_between(z2, vector_target_2_optical)
        print(angle_z_om_1, angle_z_om_2) 
        if angle_z_om_1 > angle_z_om_2: # choose the larger angle axis
            target_coordinate_z_axis = z1
            print("z1 selected")
        else:
            target_coordinate_z_axis = z2
            print("z2 selected")

        angle_et_z = self.angle_between(target_coordinate_z_axis, vector_et)
        print("angle_et_z:", angle_et_z, "beta:", beta)
        self.angle_matched(angle_et_z, beta)

        # Second : get the direction vector of the y axis of Target_Tip_in_Base  
        x, y, z = symbols('x,y,z')
        f1 = target_coordinate_z_axis[0]*x+target_coordinate_z_axis[1]*y+target_coordinate_z_axis[2]*z
        f2 = vector_et[0]*x + vector_et[1]*y + vector_et[2]*z-cs_theta
        f3 = x**2+y**2+z**2-1
        r = solve([f1, f2, f3], [x, y, z])

        y1, y2 = np.array(r, dtype=np.float32)
        print('y1:', y1)
        print('y2:', y2)
        target_coordinate_y_axis = y1
        
        # Third : get the direction vector of the x axis of Target_Tip_in_Base
        target_coordinate_x_axis = np.cross(target_coordinate_y_axis, target_coordinate_z_axis)
        target_coordinate_x_axis = self.get_unit_vector(target_coordinate_x_axis)
        print('x:',target_coordinate_x_axis)

        # if target_coordinate_x_axis[2] < 0: # to choose the correct y-axis, we see the resulting x-axis. Depending on the marker frame at the tool, we can observe if the resulting x-axis in the base frame of the robot has z component in the +ve direction or the -ve direction of the base frame
        #     target_coordinate_y_axis = y2
        #     target_coordinate_x_axis = np.cross(target_coordinate_y_axis, target_coordinate_z_axis)
        #     print('x changed to:',target_coordinate_x_axis)

        angle_et_y = self.angle_between(target_coordinate_y_axis, vector_et)
        # self.angle_matched(angle_et_y, theta)
        angle_et_x = self.angle_between(target_coordinate_x_axis, vector_et)
        print("angle_et_y:", angle_et_y, "theta:", theta)
        print("angle_et_x:", angle_et_x, "phi:", phi)
        
        angle_threshold = 10 # in degrees
        angle_threshold = math.radians(angle_threshold)

        if(abs(angle_et_y-theta) > angle_threshold or abs(angle_et_x-phi) > angle_threshold):
            target_coordinate_y_axis = y2
            target_coordinate_x_axis = np.cross(target_coordinate_y_axis, target_coordinate_z_axis)
            target_coordinate_x_axis = self.get_unit_vector(target_coordinate_x_axis)
            print('x changed to:',target_coordinate_x_axis)
            angle_et_y = self.angle_between(target_coordinate_y_axis, vector_et)
            angle_et_x = self.angle_between(target_coordinate_x_axis, vector_et)
            print("angle_et_y:", angle_et_y, "theta:", theta)
            print("angle_et_x:", angle_et_x, "phi:", phi)

        self.Target_Tip_in_Base[:3, 3] = pt_in_b[:3, 0]
        self.Target_Tip_in_Base[:3, 0] = target_coordinate_x_axis    # stack the coordinates axis calculated above
        self.Target_Tip_in_Base[:3, 1] = target_coordinate_y_axis    
        self.Target_Tip_in_Base[:3, 2] = target_coordinate_z_axis 

        phi, theta, beta = self.get_angle_between_vector_and_coordinate(vector_et, self.Target_Tip_in_Base)
        print("Exact angle phi, theta, beta:", phi, theta, beta)

        Hand_in_Tip = np.linalg.inv(self.Tip_in_Hand)
        self.Target_Hand_in_Base = self.Target_Tip_in_Base@Hand_in_Tip    # base->Tip Tip->Hand
        print('target tip pose in base : ')
        print(self.Target_Tip_in_Base)
        print('target hand pose in base : ')
        print(self.Target_Hand_in_Base)
        self.pose = self.matrix_to_6D_vector(self.Target_Hand_in_Base)
        self.pose[:3] *= 1000.0    # unit of translation changed to mm

        ## cross-check begins
        r_mat_base_in_hand_frame = np.matmul(self.Tool_in_Hand[:3,:3],np.matmul(self.trans_tip_in_marker_frame[:3,:3],np.linalg.inv(self.Target_Tip_in_Base[:3,:3])))
        t1 = np.dot(r_mat_base_in_hand_frame,np.dot(self.Target_Tip_in_Base[:3,:3],np.dot(np.linalg.inv(self.trans_tip_in_marker_frame[:3,:3]),np.linalg.inv(self.Tool_in_Hand)[:3,3])))
        t1_ = np.dot(self.Tool_in_Hand[:3,:3],np.linalg.inv(self.Tool_in_Hand)[:3,3])
        t2 = np.dot(r_mat_base_in_hand_frame,np.dot(self.Target_Tip_in_Base[:3,:3],np.linalg.inv(self.trans_tip_in_marker_frame)[:3,3]))
        t2_ = np.dot(self.Tip_in_Hand[:3,:3],np.linalg.inv(self.trans_tip_in_marker_frame)[:3,3])
        t3 = np.dot(r_mat_base_in_hand_frame,self.Target_Tip_in_Base[:3,3])
        t_vec_base_in_hand_frame = -(t1 + t2 + t3)
        t_vec_base_in_hand_frame_ = -(t1_ + t2_ + t3)
        # print('r_mat:',r_mat_base_in_hand_frame)
        # print('t_vec:',t_vec_base_in_hand_frame)
        # print('t_vec_:',t_vec_base_in_hand_frame_)
        # print('t1',t1)
        # print('t1_',t1_)
        # print('t2',t2)
        # print('t2_',t2_)
        # print('t3',t3)
        # print('t_vec',t_vec_base_in_hand_frame)
        # print('t_vec_',t_vec_base_in_hand_frame_)
        cc_Base_in_Hand = np.eye(4)
        cc_Base_in_Hand[:3,3] = t_vec_base_in_hand_frame_
        cc_Base_in_Hand[:3,:3] = r_mat_base_in_hand_frame
        cc_Hand_in_Base = np.linalg.inv(cc_Base_in_Hand)
        cc_pose = self.matrix_to_6D_vector(cc_Hand_in_Base)
        # print('cc_pose:',cc_pose)
        ## cross-check ends

        vector_of_needle = (self.Target_Tip_in_Base[:3, 3] - self.Target_Hand_in_Base[:3, 3])
        vector_of_needle = self.get_unit_vector(vector_of_needle)
        self.assert_unit_norm(vector_of_needle)
        print('vector_of_needle:', vector_of_needle)
        print('vector_et:', vector_et)
        print(f"穿刺角度误差:{np.rad2deg(self.angle_between(vector_of_needle, vector_et))}°")
        print("求解耗时:", time.time()-start)

        self.TargetToolTrans = self.Target_Hand_in_Base@self.Tool_in_Hand\
        
        print(self.pose)
    
    # def pidControl(self,Kp,Ki,Kd,error_threshold,target_point_in_base,target_point_in_cam = None):
    #   counter = 1
    #   delta_prev = np.array([0,0,0])
    #   uI_prev = np.array([0,0,0])
    #   uI = np.array([0,0,0])
    #   uD = np.array([0,0,0])
    #   time_prev = round(time.time() * 1000) # in milliseconds
    #   while True:
    #     print('---------counter--------:',counter)
    #     # print('Marker coordinates (all):')
    #     # print(self.marker_coodinates)
    #     tool_marker_ind = self.reg_wiget.tool_marker_ind
    #     marker_coodinates = self.reg_wiget.marker_coodinates
    #     print('tool_marker_ind:')
    #     print(tool_marker_ind)
    #     tool_marker_coodinates = [marker_coodinates[i*3:i*3+3] for i in tool_marker_ind]
    #     tool_marker_coodinates = [item for sublist in tool_marker_coodinates for item in sublist]
    #     while (len(tool_marker_coodinates) != 12):
    #        print('-----------waiting for the correct tool marker coordinates----------; current len is : ', len(tool_marker_coodinates))
    #        print(marker_coodinates)
    #        print(tool_marker_coodinates)
    #        pass
    #     marker_in_cam = np.array(tool_marker_coodinates).reshape(4,3)
    #     # print('Marker coord in cam : ', marker_in_cam)
    #     trans_marker_in_cam_frame = self.reg_wiget.tool_0.get_homo_trans_mat(marker_in_cam) # no need to explicitly specify; register function is called inside
    #     current_marker_origin_in_base = np.dot(self.reg_wiget.camera_in_base,trans_marker_in_cam_frame[:,3])
    #     #######Formulation 1########
    #     # trans_marker_in_base_frame = np.dot(self.reg_wiget.camera_in_base,trans_marker_in_cam_frame)
    #     # trans_hand_in_base_frame = np.dot(trans_marker_in_base_frame,self.reg_wiget.hand_in_marker)
    #     # current_hand_pose = trans_hand_in_base_frame[:3,3] # TODO : use angles as  well
    #     # print('current hand pose : ', current_hand_pose)
    #     #delta = acc_pose[0:3] - current_hand_pose #[acc_pose[i] - current_hand_pose[i] for i in range(3)] # this is in base frame
       
    #     # if flag_target_index == 1:
    #     #   delta = target1[0:3] - marker_in_cam[-1,:] # this is in camera frame
    #     # else:
    #     #   delta = target2[0:3] - marker_in_cam[-1,:] # this is in camera frame
    #     # print('delta (in camera frame): ', delta)
    #     # error = np.linalg.norm(delta)
    #     # print('error (in camera frame): ',error)
        
    #     #######Formulation 2########
    #     trans_current_tip_in_cam_frame = np.dot(trans_marker_in_cam_frame,self.reg_wiget.trans_tip_in_marker_frame)
    #     # To calculate the error in camera frame
    #     if target_point_in_cam is not None:
    #       delta_cam_frame = target_point_in_cam - trans_current_tip_in_cam_frame[:,-1]
    #       delta_cam_frame = delta_cam_frame[:3]
    #       error_cam_frame = np.linalg.norm(delta_cam_frame)
    #       print('delta (in cam frame): ', delta_cam_frame)
    #       print('error (in cam frame): ', error_cam_frame)
    #       self.delta_position_in_cam.append(delta_cam_frame.tolist())
    #       self.error_in_cam.append(error_cam_frame)

    #     # To calculate the angular error
    #     trans_current_tip_in_base_frame = np.dot(self.reg_wiget.camera_in_base,trans_current_tip_in_cam_frame)
    #     current_point_in_base = trans_current_tip_in_base_frame[:,-1]
    #     current_vector_et = self.get_puncture_path(current_marker_origin_in_base, current_point_in_base)  # get unit direction vector
    #     self.assert_unit_norm(current_vector_et)
    #     # print("current_vector_et:", current_vector_et)
    #     phi, theta, beta = self.get_angle_between_vector_and_coordinate(current_vector_et, self.Target_Tip_in_Base)
    #     # print("Current angle phi, theta, beta:", phi, theta, beta)
    #     delta_angle = self.desired_phi_theta_beta - np.array([phi,theta,beta])
    #     print('delta angles (in base frame): ', delta_angle)
    #     print('error angles (in base frame): ', np.linalg.norm(delta_angle))
        
    #     # To calculate the error in base frame of the robot
    #     delta = target_point_in_base - current_point_in_base  
    #     delta = delta[:3]
    #     error = np.linalg.norm(delta)
    #     print('delta (in base frame): ', delta)
    #     print('error (in base frame): ', error)
    #     self.delta_position_in_base.append(delta.tolist())
    #     self.error_in_base.append(error)

    #     if(error < error_threshold):
    #       break

    #     time_now = round(time.time() * 1000) # in milliseconds
        
    #     if counter == 1:
    #       del_time = 4 # for the first control computation assuming 4 ms control time
    #     else:
    #       del_time = time_now - time_prev
    #     print('del time : ', del_time)
    #     if counter > 1:
    #       uI = uI_prev + (del_time/2) * (delta + delta_prev)
    #       uD = (delta - delta_prev) / del_time

    #     P_term = Kp * delta 
    #     I_term = Ki * uI 
    #     D_term = Kd * uD
    #     self.pid_input_p.append(P_term.tolist())
    #     self.pid_input_i.append(I_term.tolist())
    #     self.pid_input_d.append(D_term.tolist())

    #     # hand_in_base_now = self.reg_wiget.get_flange_base()
    #     hand_in_base_now = [float(x) for x in self.reg_wiget.robot_pose.split(',')]
    #     hand_in_base_now = self.reg_wiget.convertUrStandardPoseToNonStandardPose(hand_in_base_now)
    #     hand_in_base_now = np.array(hand_in_base_now, dtype = np.float32)
    #     hand_in_base_now[0] = hand_in_base_now[0] + P_term[0] + I_term[0] + D_term[0]
    #     hand_in_base_now[1] = hand_in_base_now[1] + P_term[1] + I_term[1] + D_term[1]
    #     hand_in_base_now[2] = hand_in_base_now[2] + P_term[2] + I_term[2] + D_term[2]
    #     print('PID pose str:', hand_in_base_now)
    #     hand_in_base_now = self.reg_wiget.convertNonStandardPoseToUrStandardPose(hand_in_base_now)
    #     hand_in_base_now_str = np.array2string(hand_in_base_now, separator=',')[1:-1] # 去掉括号保留逗号

    #     # self.reg_wiget.move_robot_to_random_position(hand_in_base_now_str, 'pose')
    #     self.reg_wiget.move_robot_to_pose(hand_in_base_now_str)
        
    #     # ## wait for the robot to start moving
    #     # while True:
    #     #   if (self.reg_wiget.rbt_state == 3):
    #     #     break
    #     #   pass
    #     while self.reg_wiget.is_robot_steady:
    #       pass
        
    #     # print('Robot state : ', self.reg_wiget.rbt_state)
    #     print('Robot steady ? : ', self.reg_wiget.is_robot_steady)

    #     flag_wait = True
    #     ## wait for the robot to stop moving
    #     # while True:
    #     #   if(self.reg_wiget.rbt_state == 0):
    #     #     break
    #     while not self.reg_wiget.is_robot_steady:
    #       if(flag_wait):
    #         print('[[[[waiting for robot to finish the movement]]]]')
    #         flag_wait = False
    #       time.sleep(0.05)

    #     # print('Robot state : ', self.reg_wiget.rbt_state)
    #     print('Robot steady ? : ', self.reg_wiget.is_robot_steady)
    #     print('P term', P_term)
    #     print('I term', I_term)
    #     print('D term', D_term)
        
    #     delta_prev = delta
    #     time_prev = time_now
    #     uI_prev = uI
    #     counter += 1
    
    # def plotData(self,error,delta,timestamp,plot_path,plot_title,delta_path = None,error_path = None):
    #   error_arr = np.array(error)
    #   delta_arr = np.array(delta).reshape(-1,3)
    #   if delta_path is not None:
    #     np.savetxt(f"{self.dir_path}{timestamp}_{delta_path}.txt", delta_arr,fmt='%.8f')
    #   if error_path is not None:
    #     np.savetxt(f"{self.dir_path}{timestamp}_{error_path}.txt", error_arr,fmt='%.8f')
    #   delta_x = delta_arr[:,0]
    #   delta_y = delta_arr[:,1]
    #   delta_z = delta_arr[:,2]

    #   X = np.arange(0,len(error_arr))
    #   X_delta = np.arange(0,len(delta_x))
    #   fig,axis = plt.subplots(2,2)

    #   if delta_path is not None:
    #     axis[1,1].set_xticks(X)
    #     axis[1,1].plot(X,error_arr,color="black")
    #     axis[1,1].set_title(plot_title + " norm")

    #   axis[0,0].set_xticks(X_delta)
    #   axis[0,0].plot(X_delta,delta_x,color = "red")
    #   axis[0,0].set_title(plot_title + " x")
      
    #   axis[0,1].set_xticks(X_delta)
    #   axis[0,1].plot(delta_y,color = "green")
    #   axis[0,1].set_title(plot_title + " y")
      
    #   axis[1,0].set_xticks(X_delta)
    #   axis[1,0].plot(delta_z,color = "blue")
    #   axis[1,0].set_title(plot_title + " z")

    #   plt.savefig(f"{self.dir_path}{timestamp}_{plot_path}.png")
    #   plt.show()
    
    # def plotDataAll(self):
    #   current_datetime = datetime.datetime.now()
    #   timestamp = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    #   self.plotData(self.error_in_base, self.delta_position_in_base,timestamp,self.plot_path_base,"err base",self.delta_path_base,self.error_path_base,)
    #   self.plotData(self.error_in_cam, self.delta_position_in_cam,timestamp,self.plot_path_cam,"err cam",self.delta_path_cam,self.error_path_cam)
    #   self.plotData(self.error_in_base, self.pid_input_p,timestamp,self.plot_path_pid_p,"P")
    #   self.plotData(self.error_in_base, self.pid_input_i,timestamp,self.plot_path_pid_i,"I")
    #   self.plotData(self.error_in_base, self.pid_input_d,timestamp,self.plot_path_pid_d,"D")
       

    @staticmethod
    def assert_unit_norm(v):
        assert np.isclose(np.linalg.norm(v), 1.0)

    @staticmethod
    def get_unit_vector(v):
        v_copy = deepcopy(v)
        v_copy = v_copy[:3]
        v_copy /= np.linalg.norm(v_copy)
        AccuracyTest.assert_unit_norm(v_copy)
        return v_copy
    
    @staticmethod
    def matrix_to_6D_vector(rmat):
        # Extract the translation vector
        # 使用 decompose() 函数将旋转矩阵转回平移向量和欧拉角
        translation, rotation, scale_shear, _ = tfs.affines.decompose(rmat)

        # 提取平移向量
        x, y, z = translation

        # 将旋转矩阵转换为欧拉角
        rx, ry, rz = tfs.euler.mat2euler(rotation, axes='sxyz')

        # 将欧拉角转换为度数
        rx = math.degrees(rx)
        ry = math.degrees(ry)
        rz = math.degrees(rz)

        # 输出结果
        print("Translation: ", x, y, z)
        print("Euler Angles: ", rx, ry, rz)

        return np.array([x, y, z, rx, ry, rz])
    
    def angle_matched(self, agl_1, agl_2):
        assert np.isclose(agl_1, agl_2) or np.isclose(agl_1+agl_2, math.pi)
        print("angle_matched error:", abs(agl_1-agl_2))

    def get_puncture_path(self, p_in, p_tar):
        """

        :param p_in: 入点在base坐标系下的坐标
        :param p_tar: 靶点在base坐标系下的坐标
        :return:
        """
        d_tar = (p_tar - p_in)[:3]
        # 单位化
        # print('vector from point A to point B', d_tar)
        d_tar /= np.linalg.norm(d_tar)
        # print('Normalized vector', d_tar)
        self.assert_unit_norm(d_tar)
        return d_tar

    def angle_between(self, v1, v2):
        """Returns the angle in radians between vectors 'v1' and 'v2'"""
        dot_product = np.dot(v1, v2) 
        magnitude_v1 = np.linalg.norm(v1)
        magnitude_v2 = np.linalg.norm(v2)
        cos_theta = dot_product / (magnitude_v1 * magnitude_v2)    # TODO:bug
        # print("cos_theta:", cos_theta)
        cos_theta = np.clip(cos_theta, -1, 1)
        theta = np.arccos(cos_theta)
        return theta

    def get_angle_between_vector_and_coordinate(self, vector, homo_trans):
        """

        :param vector:  向量
        :param homo_trans: 相对于base的齐次变换矩阵
        :return: angle in radian
        """
        import numpy as np
        x_axis = np.array([1, 0, 0, 1])
        y_axis = np.array([0, 1, 0, 1])
        z_axis = np.array([0, 0, 1, 1])
        origin = np.array([0, 0, 0, 1])

        x_pos = homo_trans.dot(x_axis)[:3]
        y_pos = homo_trans.dot(y_axis)[:3]
        z_pos = homo_trans.dot(z_axis)[:3]
        origin_pos = homo_trans.dot(origin)[:3]
        # TODO:这里哦语文
        return self.angle_between(x_pos-origin_pos, vector), self.angle_between(y_pos-origin_pos, vector), \
               self.angle_between(z_pos-origin_pos, vector)