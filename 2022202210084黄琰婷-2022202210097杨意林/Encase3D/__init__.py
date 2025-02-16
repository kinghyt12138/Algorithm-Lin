from typing import Iterable, List
from Encase3D._cargo import *
from Encase3D._container import *

class Strategy(object):
    # 继承此类 重写两个静态函数 实现自定义两个装载策略: 装箱顺序 和 货物.
    @staticmethod
    def encasement_sequence(cargos:Iterable) -> Iterable:
        return cargos

    @staticmethod
    def choose_cargo_poses(cargo:Cargo, container:Container) -> list:
        return list(CargoPose)

# 从货物列表一次取货物放入容器
def encase_cargos_into_container(
    cargos:Iterable, 
    container:Container, 
    strategy:type
) -> float:
    # 根据体积大小排列好了货物
    sorted_cargos:List[Cargo] = strategy.encasement_sequence(cargos)
    i = 0 # 记录放当前货物
    while i < len(sorted_cargos):
        j = 0 # 记录当前摆放方式
        cargo = sorted_cargos[i]
        poses = strategy.choose_cargo_poses(cargo, container)
        while j < len(poses):
            cargo.pose = poses[j]
            is_encased = container._encase(cargo)
            if is_encased.is_valid:
                break # 可以装入 不在考虑后续摆放方式
            j += 1  # 不可装入 查看下一个摆放方式
        if is_encased.is_valid:
            i += 1 # 成功放入 继续装箱
        elif is_encased == Point(-1,-1,0):
            continue # 没放进去但是修改了参考面位置 重装
        else :
            i += 1 # 没放进去 跳过看下一个箱子

    result = sum(list(map(
            lambda cargo:cargo.volume,container._setted_cargos
        ))) / container.volume
    #每执行一次该函数 需要refresh一下
 #   container._refresh()
    return result


# 贪心思想 放置策略 从大到小地考虑货物体积 并逐一测试各个摆放方式直至成功置入
class VolumeGreedyStrategy(Strategy):
    @staticmethod
    def encasement_sequence(cargos:Iterable) -> Iterable:
        return sorted(cargos, key= lambda cargo:cargo.volume,reverse=1)

    @staticmethod
    def choose_cargo_poses(cargo:Cargo, container:Container) -> list:
        return list(CargoPose)