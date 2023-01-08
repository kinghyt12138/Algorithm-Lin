from Encase3D import *
from Encase3D import drawer

def openreadtxt(file_name):
    data = []
    file = open(file_name, 'r',encoding='utf-8')  # 打开文件
    file_data = file.readlines()  # 读取所有行
    for row in file_data:
        tmp_list = row.split(',')  # 按‘，’切分每行的数据
        tmp_list[-1] = tmp_list[-1].replace('\n','') #去掉换行符
        #print(tmp_list)
        # 再按照空格切分数据
        for tmp in tmp_list:
            # 去掉首尾的空格
            tmp= tmp.strip()
            tmpnumlist = tmp.split(' ')
            for i in range(0,len(tmpnumlist)):
                tmpnumlist[i] = int(tmpnumlist[i])
            data.append(tmpnumlist)
    return data


if __name__ == "__main__":
    data = openreadtxt('data.txt')
  #  print(len(data))
    # 读入数据 数据有3种箱子 5种箱子 8种箱子 10种箱子 15种箱子 每种各五组数据 一共跑25次
    datalist = [['E3-1','E3-2','E3-3','E3-4','E3-5'],['E5-1','E5-2','E5-3','E5-4','E5-5'],
                ['E8-1','E8-2','E8-3','E8-4','E8-5'],['E10-1','E10-2','E10-3','E10-4','E10-5'],
                ['E15-1','E15-2','E15-3','E15-4','E15-5']]
    numlist = [3,5,8,10,15]
    """
    3种数据是三个三个读 一共读15个数据
    5种数据是五个五个读 一共读25个
    8种数据是8个8个读 一共读40个
    10种数据是10个10个读 一共读50个
    15种数据是15个15个读 一共读75个
    总共15+25+40+50+75=205个
    """
    x = 0
    for m in range(0,5):
        for i in range(0, 5):
            case = Container(587, 233, 220)
            cargos = [Cargo(data[x][0], data[x][1], data[x][2]) for _ in range(data[x][3])]
            x = x + 1
            for j in range(0, numlist[m] - 1):
                cargos.extend(Cargo(data[x][0], data[x][1], data[x][2]) for _ in range(data[x][3]))
                x = x + 1
            print(
               encase_cargos_into_container(cargos,case,VolumeGreedyStrategy)
              )
            case.save_encasement_as_file(datalist[m][i])
            drawer.draw_reslut(case,datalist[m][i])