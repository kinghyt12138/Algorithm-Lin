from enum import Enum


# 六种摆放方式
class CargoPose(Enum):
    """
    以货物的高将摆放方式分为三类 默认将长平行于x摆放
    在高确定的情况下 将货物根据从前面（垂直于yz面）观察的宽窄分为六类
     # 最长的那条边作为高 第二长的那条边作为宽 因此正面看是宽的
    tall_wide = 0
    # 最长的那条边作为高 最短的那条边作为宽 因此正面看是窄的
    tall_thin = 1
    # 第二长的那条边作为高 最长的那条边作为宽 因此正面看是宽的
    mid_wide = 2
    # 第二长的那条边作为高 最短的那条边作为宽 因此正面看是窄的
    mid_thin = 3
    # 最短的那条边作为高 最长的那条边作为宽 因此正面看是宽的
    short_wide = 4
    # 最短的那条边作为高 第二长的那条边作为宽 因此正面看是窄的
    short_thin = 5
    """
    tall_wide = 0
    tall_thin = 1
    mid_wide = 2
    mid_thin = 3
    short_wide = 4
    short_thin = 5

# 点类
class Point(object):
    def __init__(self, x: int, y: int, z: int) -> None:
        # 初始化数据 点的x y z值
        self.x = x
        self.y = y
        self.z = z
    # 返回点的str格式 x值 y值 z值
    def __repr__(self) -> str:
        return f"({self.x},{self.y},{self.z})"
    # 比较两个点是否相等 返回值为bool
    def __eq__(self, __o: object) -> bool:
        return self.x == __o.x and self.y == __o.y and self.z == __o.z
    # 合法性属性 合法TRUE
    @property
    def is_valid(self) -> bool:
        return self.x >= 0 and self.y >=0 and self.z>= 0
    # 获取该点的x值 y值 z值 序列化属性
    @property
    def tuple(self) -> tuple:
        return (self.x, self.y, self.z)

# 货物类
class Cargo(object):
    def __init__(self, length: int, width: int, height: int) -> None:
        # 初始摆放点 意味着该货物还未摆放
        self._point = Point(-1, -1, -1)
        # 货物形状 长宽高 根据摆放方式返回正确的值
        self._shape = {length, width, height}
        # 摆放形态
        self._pose = CargoPose.tall_thin
    # 返回货物的str格式 摆放位置和长宽高
    def __repr__(self) -> str:
        return f"{self._point} {self.shape}"
    #返回货物的摆放形态
    @property
    def pose(self) -> CargoPose:
        return self._pose
    # 设置货物的摆放形态
    @pose.setter
    def pose(self, new_pose: CargoPose):
        self._pose = new_pose
    # 货物具体摆放方式
    @property
    def _shape_swiche(self) -> dict:
        # 对货物长宽高做一个排序 从小到大
        edges = sorted(self._shape)
        return {
            # 最长的那条边作为高 最短的那条边作为长 因此正面看是窄的
            CargoPose.tall_thin: (edges[1], edges[0], edges[-1]),
            #最长的那条边作为高 第二长的那条边作为长 因此正面看是宽的
            CargoPose.tall_wide: (edges[0], edges[1], edges[-1]),
            # 第二长的那条边作为高 最短的那条边作为长 因此正面看是窄的
            CargoPose.mid_thin: (edges[-1], edges[0], edges[1]),
            # 第二长的那条边作为高 最长的那条边作为长 因此正面看是宽的
            CargoPose.mid_wide: (edges[0], edges[-1], edges[1]),
            # 最短的那条边作为高 第二长的那条边作为长 因此正面看是窄的
            CargoPose.short_thin: (edges[-1], edges[1], edges[0]),
            # 最短的那条边作为高 最长的那条边作为长 因此正面看是宽的
            CargoPose.short_wide: (edges[1], edges[-1], edges[0])
        }
    #返货货物的摆放位置
    @property
    def point(self):
        return self._point
    # 设置货物的摆放位置
    @point.setter
    def point(self, new_point:Point):
        self._point = new_point
    #返回货物摆放位置的x值
    @property
    def x(self) -> int:
        return self._point.x
    # 设置货物摆放位置的x值
    @x.setter
    def x(self, new_x: int):
        self._point = Point(new_x, self.y, self.z)

    # 返回货物摆放位置的y值
    @property
    def y(self) -> int:
        return self._point.y

    # 设置货物摆放位置的y值
    @y.setter
    def y(self, new_y: int):
        self._point = Point(self.x, new_y, self.z)

    # 获取货物摆放位置的z值
    @property
    def z(self) -> int:
        return self._point.z
    # 设置货物摆放位置的z值
    @z.setter
    def z(self, new_z: int):
        self._point = Point(self.z, self.y, new_z)
    # 获取货物的长度
    @property
    def length(self) -> int:
        return self.shape[0]
    #获取获取的宽度
    @property
    def width(self) -> int:
        return self.shape[1]
    # 获取货物的高度
    @property
    def height(self) -> int:
        return self.shape[-1]
    # 碰撞检测会用到投影信息 投影方法 需要传入目标投影面参数
    def get_shadow_of(self, planar: str) -> tuple:
        # 投影面为xy 右上角 左下角 x0和y0为左上角坐标
        if planar in ("xy", "yx"):
            x0, y0 = self.x, self.y
            x1, y1 = self.x + self.length, self.y + self.width
        # 投影面为xz
        elif planar in ("xz", "zx"):
            x0, y0 = self.x, self.z
            x1, y1 = self.x + self.length, self.z + self.height
        # 投影面为yz轴
        elif planar in ("yz", "zy"):
            x0, y0 = self.y, self.z
            x1, y1 = self.y + self.width, self.z + self.height
        return (x0, y0, x1, y1)

    # 返回货物的摆放状态 这里的长宽高是摆放状态的长宽高
    @property
    def shape(self) -> tuple:
        return self._shape_swiche[self._pose]

    # 设置货物的摆放状态
    @shape.setter
    def shape(self, length, width, height):
        self._shape = {length, width, height}
    # 返回货物的体积
    @property
    def volume(self) -> int:
        reslut = 1
        for i in self._shape:
            reslut *= i
        return reslut
