import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image \ 
from 

class DisparitySubscriber(Node):

    def __init__(self):
        ###fix QOS policy
        super().__init__('disparity_subscriber')
        self.subscription = self.create_subscription(
            sensor_msgs.msg.Image,
            '/multisense/left/disparity',
            self.jonah_code,
            Relability="keep last",
            10)
        self.subscription  # prevent unused variable warning

    def jonah_code(self, msg):
        print("hello_world")


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = DisparitySubscriber()

    rclpy.spin(disparity_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
