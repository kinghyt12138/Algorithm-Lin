from time import time
from typing import List
from Encase3D._cargo import *
from copy import deepcopy
import numpy as np

class Container(object):
    def __init__(self, length: int, width: int, height: int) -> None:
        # 初始化数据 车厢的长宽高
        self._length = length
        self._width = width
        self._height = height
        # 更新车厢状态
        self._refresh()

    # repr函数将对象转换为供解释器读取的形式
    # 返回一个对象的str格式 这里返回车厢的长，宽，高
    def __repr__(self) -> str:
        return f"{self._length}, {self._width}, {self._height}"

    #更新车厢状态函数
    def _refresh(self):
        # 水平放置参考面 平行于yz面
        self._horizontal_planar = 0
        # 垂直放置参考面 平行于xy面
        self._vertical_planar = 0
        # 可放置点有序集合
        self._available_points = [Point(0, 0, 0)]
        # 已放置的货物信息 货物信息由一个有序列表组成 可对其进行增删查操作
        self._setted_cargos : List[Cargo] = []

    # 序列化可放置点列表
    def _serialization_available_points(self):
        point_list = []
        for i in self._available_points:
            xyz = [i.x,i.y,i.z]
            point_list.append(xyz)
        return point_list

    #反序列化可放置点列表
    def _Deserialization_available_points(self,arr):
        point_list = []
        for i in arr:
            xyz = Point(i[0], i[1], i[2])
            point_list.append(xyz)
        return point_list

    # 获取可放置点列表 首先需要排序
    def _sort_available_points(self):
        # 可放置点按照y x z的顺序排列 优先级为z x y
        arr = np.array(self._serialization_available_points())
        # 1 0 2 z x y 越靠后优先级越高
        # 0 1 2 z y x
        arrsortIndex = np.lexsort((arr[:,0],arr[:,1],arr[:,2]))
        arr2 = arr[arrsortIndex,:]
        # 将排好序的可放置点放回可放置点列表
        self._available_points.clear()
        self._available_points = self._Deserialization_available_points(arr2)
        # 输出测试一下
     #   print("可放置点排序")
       # print(self._available_points)

    #检测冲突 冲突返回false 不冲突返回true
    def is_encasable(self, site: Point, cargo: Cargo) -> bool:
        # 默认不冲突
        encasable = True
        # 为了避免检测过程中对原货物数据造成污染 深复制一个临时货物实例 在其基础上操作
        temp = deepcopy(cargo)
        # 货物的放置点
        temp.point = site
        if (
            # 货物放置在x轴超出范围
            temp.x + temp.length > self.length or
            # 货物放置在y轴超出范围
            temp.y + temp.width > self.width or
            # 货物放置在z轴超出范围
            temp.z + temp.height > self.height
        ):
            #则货物放置与容器有冲突
            encasable = False
        # 检测放置货物与已放置的货物之间是否有冲突 是否重叠
        for setted_cargo in self._setted_cargos:
            # 有冲突
            if _is_cargos_collide(temp, setted_cargo):
                encasable = False
        return encasable
    #装箱
    def _encase(self, cargo: Cargo) -> Point:
        # 标记 flag存储放置位置, (-1, -1, 0)放置失败并调整参考面, (-1, -1, -1)放置失败.
        flag = Point(-1, -1, -1)
        # 用于记录执行前的参考面位置, 便于后续比较
        history = [self._horizontal_planar, self._vertical_planar]
        # 参考面是否改变
        def __is_planar_changed() -> bool:
            return (
                # 参考面改变 返回true 否则返回false
                not (self._horizontal_planar == history[0] and
                self._vertical_planar == history[-1])
            )
        # 装箱实现 依次取出可放置点 尝试放置货物
        for point in self._available_points:
            # 正常放置  如果没有碰撞冲突且放置的货物没有超过参考面
            if (
                self.is_encasable(point, cargo) and
                point.x + cargo.length < self._horizontal_planar and
                point.z + cargo.height < self._vertical_planar
            ):
                # 存储放置点 跳出循环
                flag = point
                break
        # 如果放置失败 哪些情况会放置失败呢
        """
        四种情况 
        ① 与车厢冲突 
        ② 与货物冲突 但与车厢冲突和与货物冲突无法调整 那么能调整放置的只有下述两种情况 
        通过调整参考面来调整货物放置
        ③ 超过了yz参考面 
        3.1 yz参考面已达车厢长度 那么考虑叠放 
        3.2 yz参考面未达车厢长度 考虑放与yz平行开始放置下一行 贴着xz面开始放
        ④ 超过了xy参考面
        考虑开始在下一层开始放置 可以和3.1合并
        """
        if not flag.is_valid:
            if (
                # 查看yz参考面的位置 如果为0或者是达到容器边缘
                # 为0说明第一个货物还没放 到容器边缘说明yz参考面已经达到上限 该考虑叠放了
                # 就比如第一层放满了 开始放第二层
                self._horizontal_planar == 0 or
                self._horizontal_planar == self.length
            ):
                # 尝试从z轴的某一点开始放置 开始叠放货物 没有冲突
                if self.is_encasable(Point(0, 0, self._vertical_planar), cargo):
                    # 能放 更新放置点
                    flag = Point(0, 0, self._vertical_planar)
                    # 更新参考面的值
                    self._vertical_planar += cargo.height
                    self._horizontal_planar = cargo.length
                    # 放置了货物 不检测参考面改变
                # 有冲突 说明该货物的高度叠加到当前层后 超出了车厢高度
                elif self._vertical_planar < self.height:
                    #调整xy参考面为车厢最大高度
                    self._vertical_planar = self.height
                    # 检测参考面改变
                    #if __is_planar_changed():
                       # flag.z == 0 # 将flag设置成 放置失败并调整了参考面
            # 否则 继续在当前层放置
            else:
                for point in self._available_points:
                    # 从可放置点列表中选出贴着yz参考面的放置点
                    # 并且该放置点在xz面上
                    # 放置不冲突且放置后货物满足容器垂直参考线的限制
                    # 可以理解为当前层 第一行放满了 放第二行了
                    if (
                        point.x == self._horizontal_planar and
                        point.y == 0 and
                        self.is_encasable(point, cargo) and
                        point.z + cargo.height <= self._vertical_planar
                    ):
                        # 标记为已放置已更新
                        flag = point
                        # 更新水平参考线
                        self._horizontal_planar += cargo.length
                        break
                        # 放置了货物 不检测参考面改变
                # 可放置点列表中没有符合条件的放置点 那么货物未放置 更新yz参考面
                if not flag.is_valid:
                    # 更新yz水平参考线
                    self._horizontal_planar = self.length
                  #  if __is_planar_changed(): #这一步操作没有意义 删除
                     #  flag.z == 0 # 将flag设置为 放置失败并调整了参考面
        # 货物已经成功放置
        if flag.is_valid:
            # 将放置点赋值给货物放置点
            cargo.point = flag
            # 删除该放置点
            if flag in self._available_points:
                self._available_points.remove(flag)
            # 挪动货物 （函数中有判断是否需要挪动）
            self._adjust_setting_cargo(cargo)
            # 将货物添加到已放置列表
            self._setted_cargos.append(cargo)
            # 并将该货物放入后产生的三个新的放置点加入放置点列表
            self._available_points.extend([
                Point(cargo.x + cargo.length, cargo.y, cargo.z),
                Point(cargo.x, cargo.y + cargo.width, cargo.z),
                Point(cargo.x, cargo.y, cargo.z + cargo.height)
            ])
            # 对放置点进行排序
            self._sort_available_points()
        return flag
    # 挪动货物
    def _adjust_setting_cargo(self, cargo: Cargo):
        site = cargo.point
        # 为避免污染 进行一个深复制操作
        temp = deepcopy(cargo)
        # 没有冲突 不需要挪动货物
        if not self.is_encasable(site, cargo):
            return None
        # 序列化坐标
        xyz = [site.x, site.y, site.z]
        # 序列化坐标以执行遍历递减操作, 减少冗余
        for i in [1,0,2]: # 012 向左向后挪动 再向下 以免悬空
            is_continue = True
            while xyz[i] > 1 and is_continue:
                # 依次在xyz三个方向上挪动货物 挪动的结果就是尽量使得货物靠边
                xyz[i] -= 1
                temp.point = Point(xyz[0], xyz[1], xyz[2])
                # 挪动后检测冲突 往边挪 不存在挪出容器的问题 所以 仅检测货物之间的冲突
                for setted_cargo in self._setted_cargos:
                    if not _is_cargos_collide(setted_cargo, temp):
                        continue
                    # 冲突了 挪回去 跳出循环
                    xyz[i] += 1
                    is_continue = False
                    break
        # 在一系列挪动之后 更新货物的放置点
        cargo.point = Point(xyz[0], xyz[1], xyz[2]) # 反序列化
    # 保存已放置货物的放置点和放置状态信息
    def save_encasement_as_file(self, filename):
        name = "E:/postgraduate/课程资料/高级算法设计与分析/算法大作业/csv3/" + filename + "_encasement.csv"
        file = open(name, 'w', encoding='utf-8')
        file.write(f"index,x,y,z,length,width,height\n")
        i = 1
        for cargo in self._setted_cargos:
            file.write(f"{i},({cargo.x},{cargo.y},{cargo.z}),")
            file.write(f"({cargo.length},{cargo.width},{cargo.height})\n")
            i += 1
        file.write(f"container,,,,{self}\n")
        file.close()

    # 长设置为只读属性
    @property
    def length(self) -> int:
        return self._length
    # 宽设置为只读属性
    @property
    def width(self) -> int:
        return self._width
    # 高设置为只读属性
    @property
    def height(self) -> int:
        return self._height
    # 体积设置为只读属性
    @property
    def volume(self) -> int:
        return self.height * self.length * self.width

# 判断长方形是否冲突 冲突返回1 不冲突返回0
def _is_rectangles_overlap(rec1:tuple, rec2:tuple) -> bool:
    return not (
        # 以下四项只要有一个是1（即不冲突） 那么返回就是0
        # 即长方体无冲突 右边的左上角比左边的右下角大 即无碰撞
        # xy面为例子：0和1是矩形左上角的坐标 2和3矩形右下角的坐标
        # 假设rec1是右边的
        rec1[0] >= rec2[2] or rec1[1] >= rec2[3] or
        # 假设rec2是右边
        rec2[0] >= rec1[2] or rec2[1] >= rec1[3]
    )
# 货物之间是否冲突 三个投影面都没有冲突的时候 返回false 即无冲突
def _is_cargos_collide(cargo0: Cargo, cargo1: Cargo) -> bool:
    return (
        _is_rectangles_overlap(cargo0.get_shadow_of("xy"), cargo1.get_shadow_of("xy")) and
        _is_rectangles_overlap(cargo0.get_shadow_of("yz"), cargo1.get_shadow_of("yz")) and
        _is_rectangles_overlap(cargo0.get_shadow_of(
            "xz"), cargo1.get_shadow_of("xz"))
    )






