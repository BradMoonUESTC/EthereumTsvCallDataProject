import json

import networkx as nx
import pandas as pd
import matplotlib

matplotlib.use('TkAgg')  # 大小写无所谓 tkaGg ,TkAgg 都行
import matplotlib.pyplot as plt
from tqdm import trange
import coreAddress
from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)

if __name__ == '__main__':
    file_path = r'defi_branches/Curve'
    file_path_middleData = r'Middle_Data/Curve'

    datas = pd.read_csv(file_path, sep='\s', header=None, names=['from', 'fromInput', 'to', 'toInput', 'num'],
                        index_col=None)
    # from fromInput to toInput num

    # 是否打印图像
    printPic = False

    # 切换功能用的：1：用来统计折线图；2：用来进行依赖分析
    switch_function_flag = 2

    # 用来根据折线图结果输入阈值
    threshold = 400

    # 从入度结果中继续筛选，我们认为大于threshold_for_result调用次数的是核心合约
    threshold_for_result = 3

    # 使用哪个核心地址集
    currentAddress = coreAddress.currentaddress_curve

    # 入度排序还是出度排序
    inORoutDegree = 'in_degree'
    if switch_function_flag == 1:
        # region 折线图
        # print(datas)
        datas_ana = datas[(datas["from"].isin(currentAddress)) | (datas["to"].isin(currentAddress))]
        print(len(datas_ana))
        nums = datas_ana.sort_values("num", ascending=False)
        sorted_nums = nums["num"]
        sorted_nums = sorted_nums.reset_index(drop=True)
        plt.plot(sorted_nums)
        plt.show()
        # endregion

    if switch_function_flag == 2:

        # region 依赖图
        uncurrentAddress1 = []
        currentAddress_has = []
        uncurrentAddress2 = []

        # X=>currentAddress的所有地址
        datas_to_in_currentAddress = datas[datas["to"].isin(currentAddress)]
        # currentAddress=>X的所有地址
        datas_from_in_currentAddress = datas[datas["from"].isin(currentAddress)]
        D = nx.DiGraph()
        for i in trange(len(datas_to_in_currentAddress)):
            from_address = datas_to_in_currentAddress["from"].values[i]
            to_address = datas_to_in_currentAddress["to"].values[i]
            num = datas_to_in_currentAddress["num"].values[i]

            if num < threshold:
                continue
            # 用来筛出核心合约到核心合约的调用
            if from_address in currentAddress:
                continue

            # 用于单独标色——非核心地址，如果不在uncurrentAddress1中且在currentAddress中，加入，用于最后标色以及下面的画图
            if from_address not in uncurrentAddress1 and from_address not in currentAddress:
                uncurrentAddress1.append(from_address)

            # 用于单独标色——核心地址：如果在原始地址集且也出现了，加入最后的标色集里，如果出现过就不新加入
            if (to_address in currentAddress) and (to_address not in currentAddress_has):
                currentAddress_has.append(to_address)

            # 开始绘图
            if not (D.has_node(from_address) or D.has_node(to_address)):
                D.add_node(from_address)
                D.add_node(to_address)
                D.add_edge(from_address, to_address, weight=num)
                continue
            if D.has_node(from_address) and D.has_node(to_address):
                D.add_edge(from_address, to_address, weight=num)
            elif D.has_node(from_address) and not D.has_node(to_address):
                D.add_node(to_address)
                D.add_edge(from_address, to_address, weight=num)
            elif D.has_node(to_address) and not D.has_node(from_address):
                D.add_node(from_address)
                D.add_edge(from_address, to_address, weight=num)

        pos = nx.shell_layout(D)
        # print(D.nodes)
        labels = {}
        for node in D.nodes:
            if node in currentAddress_has:
                labels[node] = node
        # nx.draw(D, with_labels=True, labels=labels)
        nx.draw_networkx_nodes(D, pos=pos, nodelist=uncurrentAddress1, node_size=30, node_color='blue')  # 出度
        nx.draw_networkx_nodes(D, pos=pos, nodelist=currentAddress_has, node_size=100, node_color='red')
        nx.draw_networkx_nodes(D, pos=pos, nodelist=uncurrentAddress2, node_size=30, node_color='green')  # 入度
        nx.draw_networkx_edges(D, pos=pos, edge_color='grey', width=0.1)
        # nx.draw_networkx_labels(D, pos, labels, font_size=16, font_color='red')
        # 画图1
        if printPic:
            plt.show()
        # endregion

        # region 入度出度统计
        degrees = pd.DataFrame(columns=['address', 'in_degree', 'out_degree'])
        for address in currentAddress:
            in_degree = D.in_degree(address)

            out_degree = D.out_degree(address)
            if str(in_degree).isdigit():
                degree_data = {'address': address, 'in_degree': in_degree, 'out_degree': out_degree}
                degrees = degrees.append(degree_data, ignore_index=True)

        sorted_degrees = degrees.sort_values(inORoutDegree, ascending=False)
        print(sorted_degrees)

        # endregion
        # 输出 sort_degrees ，'address', 'in_degree', 'out_degree'

        # region 合约内部调用图
        datas_to_and_from_in_currentAddress = datas[datas["to"].isin(currentAddress)]
        datas_to_and_from_in_currentAddress = datas_to_and_from_in_currentAddress[
            datas_to_and_from_in_currentAddress["from"].isin(currentAddress)]

        D_inside = nx.DiGraph()
        for i in trange(len(datas_to_and_from_in_currentAddress)):
            from_address = datas_to_and_from_in_currentAddress["from"].values[i]
            to_address = datas_to_and_from_in_currentAddress["to"].values[i]
            num = datas_to_in_currentAddress["num"].values[i]
            if from_address == to_address:
                continue
            # if num < threshold:
            #     continue

            # 开始绘图
            D_inside.add_node(from_address)
            D_inside.add_node(to_address)
            D_inside.add_edge(from_address, to_address, weight=num)

        pos = nx.shell_layout(D_inside)
        labels = {}
        # 画图2
        nx.draw(D_inside, pos=pos, with_labels=True)
        if (printPic):
            plt.show()

        # endregion

        # region 入度出度统计
        degrees_inside = pd.DataFrame(columns=['address', 'in_degree', 'out_degree'])
        for address in currentAddress:
            in_degree = D_inside.in_degree(address)

            out_degree = D_inside.out_degree(address)
            if str(in_degree).isdigit():
                degree_data = {'address': address, 'in_degree': in_degree, 'out_degree': out_degree}
                degrees_inside = degrees_inside.append(degree_data, ignore_index=True)

        sorted_degrees_inside = degrees_inside.sort_values(inORoutDegree, ascending=False)
        print(sorted_degrees_inside)
        # endregion

        # 输出sort_degrees_inside，'address', 'in_degree', 'out_degree'

        # region 结果筛选，叠加判断，输出结果
        sorted_degrees_reset_index = sorted_degrees.reset_index(drop=True)
        # 从全调用图种筛出in_degree少的，从而筛出核心合约
        sorted_degrees_reset_index = sorted_degrees_reset_index[
            sorted_degrees_reset_index['in_degree'] > threshold_for_result]
        print(sorted_degrees_reset_index)
        print('意味着存在那么两种交易1和2，交易1直接调用了A，并且很多，即A是一个核心入口合约')
        print('然而交易2调用合约B也很多，同时A又调用了B，意味着有人绕过了A去调用B，A->B间未存在访问控制')
        print('合约内部调用发起者A\t合约内部调用接收者B')

        # region 0414新增代码功能==>输出疑似骨干合约的下游并拼接==>定义部分
        # 保存疑似骨干合约地址集
        coreContractAddress = []
        # endregion

        for i in trange(len(sorted_degrees_reset_index)):
            in_degree = sorted_degrees_reset_index['in_degree'].values[i]
            address = sorted_degrees_reset_index['address'].values[i]

            # 取出剩下的数据
            list_remain = sorted_degrees_reset_index[~sorted_degrees_reset_index['address'].isin([address])]

            for j in range(len(list_remain)):
                address_compare = list_remain['address'].values[j]
                if D_inside.has_edge(address_compare, address):

                    # region 添加疑似骨干合约至骨干合约地址集
                    if address_compare not in coreContractAddress:
                        coreContractAddress.append(address_compare)
                    if address not in coreContractAddress:
                        coreContractAddress.append(address)
                    # endregion

                    print(address_compare, '\t', address)

        # region 先试着把D_inside里面没有出度的节点删掉,
        # 原因在于，如果没有出度，意味着这个节点永远被人调用，
        # 极大可能是一个库合约，且不可能是核心合约
        # 如果是库合约，意味着防火墙逻辑不能往里面插
        nodelist_inside = []
        for node in D_inside.nodes:
            nodelist_inside.append(node)
        for node in nodelist_inside:
            if D_inside.out_degree(node) == 0:
                D_inside.remove_node(node)

        for node in nodelist_inside:
            if not D_inside.has_node(node):
                continue
            if D_inside.in_degree(node) == 0 and D_inside.out_degree(node) == 0:
                D_inside.remove_node(node)
        # 画图3
        nx.draw(D_inside, pos=pos, with_labels=True)
        if (printPic):
            plt.show()
        # endregion

        # 先从新生成的内部调用图中筛去刚才去掉无出度节点之后的【新】核心地址集，也就是说一开始的coreAddress可能有库合约，我们筛掉
        newCoreContractAddress = []
        for address in coreContractAddress:
            if D_inside.has_node(address):
                newCoreContractAddress.append(address)
        print(newCoreContractAddress)

        D_child_nodelist_include_weight = {}
        D_child_nodelist = []
        D_child = nx.DiGraph()
        # 从D_inside中依次获取【新】核心地址集（骨干合约）的上游地址路径生成一个子图，初始为每个节点赋一个权重为1
        # 子图与子图相加，并赋予新权重，比如说时，两个都是权重为1的子图相加，权重为2。每一次相加权重+1
        # 最后输出整个的图，并只标记【新】核心地址集的权重
        # 那些没有被标进去的意味着是库合约，他们的权重，就算调用再多我们也不考虑
        for address in newCoreContractAddress:
            for node in D_inside.nodes:
                if D_inside.has_edge(node, address):  # 如果存在通路，添加进子图
                    if D_child.has_node(node):  # 如果存在节点置权重为+1
                        D_child_nodelist_include_weight[node] = D_child_nodelist_include_weight[node] + 1
                    if D_child.has_node(address):  # 如果存在节点置权重为+1
                        D_child_nodelist_include_weight[address] = D_child_nodelist_include_weight[address] + 1
                    if not D_child.has_node(node):  # 如果不存在节点置权重为1
                        D_child.add_node(node)
                        D_child_nodelist_include_weight[node] = 1
                        D_child_nodelist.append(node)
                    if not D_child.has_node(address):  # 如果不存在节点置权重为1
                        D_child.add_node(address)
                        D_child_nodelist_include_weight[address] = 1
                        D_child_nodelist.append(address)

                    D_child.add_edge(node, address)

        # 用于标示出权重标签
        labels = {}
        for node in D_child.nodes:
            if node in newCoreContractAddress:
                labels[node] = D_child_nodelist_include_weight[node]
        labels_address = {}
        for node in D_child.nodes:
            if node in D_child_nodelist_include_weight:
                labels_address[node] = node

        nx.draw_networkx_nodes(D_child, pos=pos, nodelist=D_child_nodelist, node_size=30, node_color='green')  # 入度
        nx.draw_networkx_edges(D_child, pos=pos, edge_color='grey', width=0.1)
        nx.draw_networkx_labels(D_child, pos, labels, font_size=30, font_weight=20, font_color='red')
        nx.draw_networkx_labels(D_child, pos, labels_address, font_size=10, font_weight=20, font_color='blue')

        if (printPic):
            plt.show()

        # 算上初始权重
        for node in D_child_nodelist_include_weight.keys():
            original_weight = 0
            if len(sorted_degrees[sorted_degrees['address'] == node]) > 0:
                original_weight = sorted_degrees[sorted_degrees['address'] == node].reset_index(drop=True).in_degree[0]
            D_child_nodelist_include_weight[node] = D_child_nodelist_include_weight[node] \
                                                    + original_weight
        # 用于标示出权重标签
        labels = {}
        for node in D_child.nodes:
            if node in newCoreContractAddress:
                labels[node] = D_child_nodelist_include_weight[node]
        labels_address = {}
        for node in D_child.nodes:
            if node in D_child_nodelist_include_weight:
                labels_address[node] = node

        nx.draw_networkx_nodes(D_child, pos=pos, nodelist=D_child_nodelist, node_size=30, node_color='green')  # 入度
        nx.draw_networkx_edges(D_child, pos=pos, edge_color='grey', width=0.1)
        nx.draw_networkx_labels(D_child, pos, labels, font_size=30, font_weight=20, font_color='red')
        nx.draw_networkx_labels(D_child, pos, labels_address, font_size=10, font_weight=20, font_color='blue')

        # endregion

        if printPic:
            plt.show()
        print("——————————————————————最终结果，我们怀疑的可以进行防火墙逻辑插入的核心合约——————————————————————")
        print(labels)
        print("——————————————————————接下来，我们将会对这些合约地址基于交易元数据进行多维度评估，其中，覆盖率是一个重要的指标——————————————————————")

        datas_middle = pd.read_csv(file_path_middleData, sep='|', header=None,
                            names=['hash', 'date', 'from', 'fromFunction', 'to', 'toFunction', 'callType', 'count'],
                            index_col=None)
        allSum = 0
        labels_data = {}
        for i in trange(len(datas_middle)):
            count = datas_middle["count"].values[i]
            fromAddress = datas_middle["from"].values[i]
            toAddress=datas_middle["to"].values[i]
            currentCount=datas_middle["count"].values[i]
            allSum = allSum + count
            if fromAddress in newCoreContractAddress and fromAddress in labels_data:
                labels_data[fromAddress]=labels_data[fromAddress]+currentCount
            elif fromAddress in newCoreContractAddress and fromAddress not in labels_data:
                labels_data[fromAddress]=currentCount

            if toAddress in newCoreContractAddress and toAddress in labels_data:
                labels_data[toAddress]=labels_data[toAddress]+currentCount
            elif toAddress in newCoreContractAddress and toAddress not in labels_data:
                labels_data[toAddress]=currentCount
        # 去重 统计有多少不同的交易
        datas_drop_duplicates=datas_middle.drop_duplicates(subset='hash')
        print("共有交易数量："+str(len(datas_middle)))

        print("共有调用数量："+str(allSum))
        print("核心地址集调用数量：")
        print(labels_data)

# def addToD_child(currentNode,D_inside):#获取节点的一级上游节点，并添加至一个新图中
#     D_ret = nx.DiGraph()
#     for node in D_inside.nodes:
#         if D_inside.has_edge(node,currentNode):
#             D_ret.add_edge()
