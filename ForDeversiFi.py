import json

import networkx as nx
import pandas as pd
import matplotlib

matplotlib.use('TkAgg')  # 大小写无所谓 tkaGg ,TkAgg 都行
import matplotlib.pyplot as plt
from tqdm import trange
import coreAddress

if __name__ == '__main__':
    file_path = r'defi_branches/Aave'
    datas = pd.read_csv(file_path, sep='\s', header=None, names=['from', 'fromInput', 'to', 'toInput', 'num'],
                        index_col=None)
    # from fromInput to toInput num

    # 切换功能用的：1：用来统计折线图；2：用来进行依赖分析
    switch_function_flag = 2

    # 用来根据折线图结果输入阈值
    threshold = 2500

    # 从入度结果中继续筛选
    threshold_for_result = 9

    # 使用哪个核心地址集
    currentAddress = coreAddress.currentaddress_aave

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
        # for node in D.nodes:
        #     if node in currentAddress_has:
        #         labels[node] = node
        nx.draw(D_inside, with_labels=True)
        # nx.draw_networkx_nodes(D, pos=pos, nodelist=uncurrentAddress1, node_size=30, node_color='blue')  # 出度
        # nx.draw_networkx_nodes(D, pos=pos, nodelist=currentAddress_has, node_size=100, node_color='red')
        # nx.draw_networkx_nodes(D, pos=pos, nodelist=uncurrentAddress2, node_size=30, node_color='green')  # 入度
        # nx.draw_networkx_edges(D, pos=pos, edge_color='grey', width=0.1)
        # nx.draw_networkx_labels(D, pos, labels, font_size=16, font_color='red')
        # plt.show()

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

        sorted_degrees_reset_index = sorted_degrees.reset_index(drop=True)
        #从全调用图种筛出in_degree少的，从而筛出核心合约
        sorted_degrees_reset_index=sorted_degrees_reset_index[sorted_degrees_reset_index['in_degree']>threshold_for_result]
        print(sorted_degrees_reset_index)
        print('意味着存在那么两种交易1和2，交易1直接调用了A，并且很多，即A是一个核心入口合约')
        print('然而交易2调用合约B也很多，同时A又调用了B，意味着有人绕过了A去调用B，A->B间未存在访问控制')
        print('合约内部调用发起者A\t合约内部调用接收者B')

        for i in trange(len(sorted_degrees_reset_index)):
            in_degree = sorted_degrees_reset_index['in_degree'].values[i]
            address = sorted_degrees_reset_index['address'].values[i]

            # 取出剩下的数据
            list_remain = sorted_degrees_reset_index[~sorted_degrees_reset_index['address'].isin([address])]

            for j in range(len(list_remain)):
                address_compare = list_remain['address'].values[j]
                if D_inside.has_edge(address_compare, address):
                    print(address_compare, '\t', address)
