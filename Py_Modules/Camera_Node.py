import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import ros_numpy

import time

class DisparitySubscriber(Node):

    def __init__(self):
        ###fix QOS policy
        super().__init__('disparity_subscriber')  #name of node
        self.subscription = self.create_subscription(
            sensor_msgs.msg.Image,
            '/multisense/left/disparity',  #stream
            self.jonah_code1,  #function called,
            10,
            Relability="keep last")
        self.subscription  # prevent unused variable warning
        
        self.lastupdate= time.time()
        self.want=None

    #called whenever msg is sent out (subscription)
    def jonah_code1(self, msg):
        self.lastupdate= time.time()
        #msg is the Image (sensor_msgs.msg), convert to numpy array
        self.want = ros_numpy.numpify(msg)

    #unused, example func
    def runOnce(self):
        rclpy.spin_once(self, timeout_sec=0.01)


class ColorImgSubscriber(Node):
    def __init__(self):
        ###fix QOS policy
        super().__init__('colorimg_subscriber')  #name of node
        self.subscription = self.create_subscription(
            sensor_msgs.msg.Image,
            '/multisense/left/image_color',  #stream
            self.jonah_code2,  #function called
            10,
            Relability="keep last")
        self.subscription  # prevent unused variable warning
        
        self.bridge = CvBridge()#lets you convert to cv2
        self.lastupdate= time.time()
        self.want=None

    #called whenever msg is sent out (subscription)
    def jonah_code2(self, msg):
        self.lastupdate= time.time()
        #msg is the Image (sensor_msgs.msg), convert to cv2
        self.want= self.bridge.imgmsg_to_cv2(msg, "bgr8")

    #unused, example func
    def runOnce(self):
        rclpy.spin_once(self, timeout_sec=0.01)


if __name__ == '__main__':
    rclpy.init()
    minimal_subscriber = DisparitySubscriber()
    rclpy.spin(disparity_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()
