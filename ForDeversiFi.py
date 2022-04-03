import json

# block_id	transaction_hash	index	depth	time
# failed	fail_reason	type	sender	recipient	child_call_count
# value	value_usd	transferred	input_hex	output_hex
import networkx as nx
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')  # 大小写无所谓 tkaGg ,TkAgg 都行
import matplotlib.pyplot as plt
from tqdm import trange
import numpy as np
import coreAddress


if __name__ == '__main__':
    file_path = r'./SushiSwap'
    datas = pd.read_csv(file_path, sep='\s', header=None,names=['from','fromInput','to','toInput','num'],index_col=None)
    # from fromInput to toInput num
    # 总计16个地址

    currentAddress=coreAddress.currentAddress_sushiswap

    #region 折线图
    # print(datas)
    # datas_ana = datas[(datas["from"].isin(currentAddress)) | (datas["to"].isin(currentAddress))]
    # print(len(datas_ana))
    # nums=datas_ana.sort_values("num",ascending=False)
    # sorted_nums=nums["num"]
    # sorted_nums=sorted_nums.reset_index(drop=True)
    # plt.plot(sorted_nums)
    # plt.show()
    #endregion

    #region 依赖图
    uncurrentAddress1=[]
    currentAddress_has=[]
    uncurrentAddress2=[]
    threshold=2000
    #X=>currentAddress的所有地址
    datas_to_in_currentAddress = datas[datas["to"].isin(currentAddress)]
    #currentAddress=>X的所有地址
    datas_from_in_currentAddress = datas[datas["from"].isin(currentAddress)]
    D = nx.DiGraph()
    for i in trange(len(datas_to_in_currentAddress)):
        from_address=datas_to_in_currentAddress["from"].values[i]
        to_address=datas_to_in_currentAddress["to"].values[i]
        num = datas_to_in_currentAddress["num"].values[i]

        if num < threshold:
            continue
        if from_address in currentAddress:
            continue

        #用于单独标色——非核心地址，如果不在uncurrentAddress1中，加入，用于最后标色以及下面的画图
        if from_address not in uncurrentAddress1:
            uncurrentAddress1.append(from_address)

        #用于单独标色——核心地址：如果在原始地址集且也出现了，加入最后的标色集里，如果出现过就不新加入
        if (to_address in currentAddress) and (to_address not in currentAddress_has):
            currentAddress_has.append(to_address)

        #开始绘图
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
    for i in trange(len(datas_from_in_currentAddress)):
        from_address=datas_from_in_currentAddress["from"].values[i]
        to_address=datas_from_in_currentAddress["to"].values[i]
        to_address_short=to_address[0:8]
        num = datas_from_in_currentAddress["num"].values[i]
        if num < threshold:
            continue
        if to_address in currentAddress:#如果是项目内部调用的话就跳过
            continue

        #用于单独标色——非核心地址，如果不在uncurrentAddress2中，加入，用于最后标色以及下面的画图
        if to_address_short not in uncurrentAddress2:
            uncurrentAddress2.append(to_address_short)

        #用于单独标色——核心地址：如果在原始地址集且也出现了，加入最后的标色集里，如果出现过就不新加入
        if (from_address in currentAddress) and (from_address not in currentAddress_has):
            currentAddress_has.append(from_address)

        #开始绘图
        if not (D.has_node(from_address) or D.has_node(to_address_short)):# 如果当前图中，任何一个from和to都不存在
            D.add_node(from_address)
            D.add_node(to_address_short)
            D.add_edge(from_address, to_address_short, weight=num)
            continue
        if D.has_node(from_address) and D.has_node(to_address_short):#如果当前图中，from和to都存在
            D.add_edge(from_address, to_address_short, weight=num)
        elif D.has_node(from_address) and not D.has_node(to_address_short):# 如果当前图中，from存在且to不存在
            D.add_node(to_address_short)
            D.add_edge(from_address, to_address_short, weight=num)
        elif D.has_node(to_address_short) and not D.has_node(from_address):# 如果当前图中，from不存在且to存在
            D.add_node(from_address)
            D.add_edge(from_address, to_address_short, weight=num)

    pos = nx.shell_layout(D)
    # print(D.nodes)
    labels={}
    for node in D.nodes:
        if node in currentAddress_has:
            labels[node]=node
    # nx.draw(D, with_labels=True, labels=labels)
    nx.draw_networkx_nodes(D, pos=pos, nodelist=uncurrentAddress1, node_size=30, node_color='blue')
    nx.draw_networkx_nodes(D, pos=pos, nodelist=currentAddress_has, node_size=100, node_color='red')
    nx.draw_networkx_nodes(D, pos=pos, nodelist=uncurrentAddress2, node_size=30, node_color='green')
    nx.draw_networkx_edges(D,pos=pos,edge_color='grey',width=0.1)
    # nx.draw_networkx(D, pos=pos, nodelist=uncurrentAddress1, node_size=50, node_color='blue', font_size=1, width=1,with_labels=False)
    # nx.draw_networkx(D, pos=pos, nodelist=currentAddress_has, node_size=100, node_color='red', font_size=20, width=2,with_labels=False)
    # nx.draw_networkx(D, pos=pos, nodelist=uncurrentAddress2, node_size=50, node_color='green', font_size=1, width=1,with_labels=False)
    nx.draw_networkx_labels(D,pos,labels,font_size=16,font_color='red')
    plt.show()
    #endregion


    #region 重入
    # sorted_nums_cumsum=sorted_nums.cumsum()
    # print(sorted_nums)
    # # print(sorted_nums)
    # sorted_nums_cumsum=sorted_nums_cumsum.apply(np.log10)  # np.exp与np.log互为逆运算
    # # sorted_nums=sorted_nums.apply(1/x)  # np.exp与np.log互为逆运算

    # D=nx.DiGraph()
    # for i in trange(len(datas)):
    #
    #     from_address = datas["from"].values[i]
    #     from_Input=datas["fromInput"].values[i]
    #     to_address=datas["to"].values[i]
    #     to_Input=datas["toInput"].values[i]
    #     num=datas["num"].values[i]
    #     if num<2:
    #         continue
    #
    #     fromInfo=from_address+" "+str(from_Input)
    #     toInfo=to_address+" "+str(to_Input)
    #     # fromInfo=from_address
    #     # toInfo=to_address
    #     D.add_node(fromInfo)
    #     D.add_node(toInfo)
    #     D.add_edge(fromInfo,toInfo,weight=num)
    # # pos = nx.shell_layout(D)
    # # print(D.edges(data=True))
    # # nx.draw(D,pos,with_labels=True)
    # # plt.show()
    # # nx.find_cycle(D, orientation="original")
    # print(list(nx.simple_cycles(D)))
    # endregion